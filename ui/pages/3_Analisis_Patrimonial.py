"""
Análisis Patrimonial: Balance General del Banco
Orden: 1) Balance General, 2) ACTIVOS, 3) PASIVOS
Ecuación: ACTIVO - PASIVO = PATRIMONIO NETO
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

st.set_page_config(page_title="Análisis Patrimonial", page_icon="💰", layout="wide")

import os
def get_api_url():
    try:
        if "API_URL" in st.secrets:
            return st.secrets["API_URL"]
    except:
        pass
    if os.getenv("API_URL"):
        return os.getenv("API_URL")
    if os.getenv("STREAMLIT_SHARING_MODE"):
        return "https://eda-dashboard-api.onrender.com"
    return "http://localhost:8000"

API_URL = get_api_url()

if "profile" not in st.session_state or st.session_state.profile is None:
    st.warning("⚠️ No hay dataset cargado.")
    st.stop()

profile = st.session_state.profile
dataset_id = st.session_state.dataset_id

st.title("💰 Análisis Patrimonial del Banco")
st.caption("Ecuación Contable: ACTIVO - PASIVO = PATRIMONIO NETO")

# Obtener columnas
all_columns = [col['name'] for col in profile['columns']]

activos_col = [col for col in all_columns if 'activo' in col.lower() and 'saldo' in col.lower()][0]
pasivos_col = [col for col in all_columns if 'pasivo' in col.lower() and 'saldo' in col.lower()][0]

# Productos ACTIVOS (colocaciones: lo que clientes deben)
activos_productos = [col for col in all_columns if any(x in col for x in ['Saldo TC', 'Saldo PR'])]

# Productos PASIVOS (captaciones: lo que clientes depositan)
pasivos_productos = [col for col in all_columns if any(x in col for x in ['Saldo CA', 'Saldo CC', 'Saldo DP'])]

banca_col = [col for col in all_columns if 'banca' in col.lower()]
banca_col = banca_col[0] if banca_col else None

# Obtener datos
@st.cache_data
def get_data(dataset_id, columns_list):
    try:
        cols_str = ",".join(columns_list)
        response = requests.get(
            f"{API_URL}/datasets/{dataset_id}/data/columns",
            params={"columns": cols_str}
        )
        if response.status_code == 200:
            return pd.DataFrame(response.json()['data'])
        return None
    except:
        return None

columns_to_fetch = [activos_col, pasivos_col] + activos_productos + pasivos_productos
if banca_col:
    columns_to_fetch.append(banca_col)

df = get_data(dataset_id, columns_to_fetch)

if df is None:
    st.error("❌ Error al cargar datos")
    st.stop()

# Limpiar datos
df = df.replace([None], np.nan)
for col in df.columns:
    if col != banca_col:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# Calcular totales
suma_activos = df[activos_col].sum()
suma_pasivos = df[pasivos_col].sum()
patrimonio_neto = suma_activos - suma_pasivos

# ==================== TABS ====================
tab1, tab2, tab3 = st.tabs([
    "⚖️ BALANCE GENERAL",
    "💳 ACTIVOS",
    "💰 PASIVOS"
])

# ==================== TAB 1: BALANCE GENERAL ====================
with tab1:
    st.header("⚖️ BALANCE GENERAL")
    
    st.markdown("### 📊 Ecuación Contable")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("**ACTIVOS**", f"${suma_activos:,.0f}")
        st.caption("Colocaciones (TC, PR)")
    
    with col2:
        st.metric("**PASIVOS**", f"${suma_pasivos:,.0f}")
        st.caption("Captaciones (CA, CC, DP)")
    
    with col3:
        st.metric("**PATRIMONIO NETO**", f"${patrimonio_neto:,.0f}")
        st.caption("ACTIVO - PASIVO")
    
    with col4:
        ratio_ap = suma_activos / suma_pasivos if suma_pasivos > 0 else 0
        st.metric("Ratio A/P", f"{ratio_ap:.2%}")
        st.caption("Colocación/Captación")
    
    st.divider()
    
    # Gráfico de composición
    col1, col2 = st.columns([1, 1])
    
    with col1:
        df_balance = pd.DataFrame({
            'Concepto': ['ACTIVOS (Colocaciones)', 'PASIVOS (Captaciones)'],
            'Monto': [suma_activos, suma_pasivos]
        })
        
        fig = px.bar(
            df_balance,
            x='Concepto',
            y='Monto',
            title='Balance General: ACTIVOS vs PASIVOS',
            color='Concepto',
            color_discrete_map={
                'ACTIVOS (Colocaciones)': '#2ecc71',
                'PASIVOS (Captaciones)': '#3498db'
            },
            text='Monto'
        )
        fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**💡 Interpretación Financiera:**")
        
        pct_activos = suma_activos / (suma_activos + suma_pasivos) * 100
        pct_pasivos = suma_pasivos / (suma_activos + suma_pasivos) * 100
        
        st.info(f"""
        📊 **Estructura del Balance**
        
        - **ACTIVOS**: ${suma_activos:,.0f} ({pct_activos:.1f}%)
          - Préstamos y créditos a clientes
        
        - **PASIVOS**: ${suma_pasivos:,.0f} ({pct_pasivos:.1f}%)
          - Depósitos y ahorros de clientes
        
        - **PATRIMONIO NETO**: ${patrimonio_neto:,.0f}
          - Resultado: ACTIVO - PASIVO
        
        ℹ️ Ratio A/P de {ratio_ap:.2%} indica que el banco coloca
        ${ratio_ap:.2f} por cada $1 captado.
        """)
    
    st.divider()
    
    # Scatter plot ACTIVOS vs PASIVOS
    st.subheader("📈 Relación ACTIVOS vs PASIVOS por Cliente")
    
    df_plot = df[(df[activos_col].notna()) & (df[pasivos_col].notna())].copy()
    
    fig = px.scatter(
        df_plot,
        x=pasivos_col,
        y=activos_col,
        color=banca_col if banca_col else None,
        title='ACTIVOS vs PASIVOS (escala logarítmica)',
        log_x=True,
        log_y=True,
        opacity=0.6,
        labels={
            pasivos_col: 'PASIVOS (Captaciones)',
            activos_col: 'ACTIVOS (Colocaciones)'
        }
    )
    
    # Línea de referencia A = P
    max_val = max(df_plot[activos_col].max(), df_plot[pasivos_col].max())
    fig.add_trace(go.Scatter(
        x=[1, max_val],
        y=[1, max_val],
        mode='lines',
        name='A = P (equilibrio)',
        line=dict(color='red', width=2, dash='dash')
    ))
    
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    st.caption("""
    **Interpretación**:
    - **Por encima de la línea roja**: Clientes con más ACTIVOS que PASIVOS (deben más de lo que depositan)
    - **Por debajo de la línea roja**: Clientes con más PASIVOS que ACTIVOS (depositan más de lo que deben)
    """)

# ==================== TAB 2: ACTIVOS ====================
with tab2:
    st.header(f"💳 {activos_col.upper()}")
    st.caption("Colocaciones: Préstamos y créditos que clientes deben al banco")
    
    # REGLA: Suma de TODOS los valores
    promedio_activos = df[activos_col].mean()
    mediana_activos = df[activos_col].median()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(f"Suma {activos_col}", f"${suma_activos:,.0f}")
    with col2:
        st.metric("Promedio", f"${promedio_activos:,.0f}")
    with col3:
        st.metric("Mediana", f"${mediana_activos:,.0f}")
    
    st.divider()
    
    # Productos que componen ACTIVOS
    st.subheader("📦 Composición de ACTIVOS")
    
    productos_activos_data = []
    for col in activos_productos:
        product_name = col.replace('Saldo', '').strip()
        
        suma = df[col].sum()
        promedio = df[col].mean()
        mediana = df[col].median()
        n_clientes = (df[col] > 0).sum()
        
        productos_activos_data.append({
            'Producto': product_name,
            'Suma': suma,
            'Promedio': promedio,
            'Mediana': mediana,
            'N° Clientes (>0)': n_clientes
        })
    
    df_prod_activos = pd.DataFrame(productos_activos_data).sort_values('Suma', ascending=False)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        fig = px.pie(
            df_prod_activos,
            values='Suma',
            names='Producto',
            title='Composición de ACTIVOS',
            color_discrete_sequence=px.colors.sequential.Greens_r
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.dataframe(
            df_prod_activos.style.format({
                'Suma': '${:,.0f}',
                'Promedio': '${:,.0f}',
                'Mediana': '${:,.0f}',
                'N° Clientes (>0)': '{:,}'
            }),
            use_container_width=True,
            hide_index=True
        )

# ==================== TAB 3: PASIVOS ====================
with tab3:
    st.header(f"💰 {pasivos_col.upper()}")
    st.caption("Captaciones: Depósitos y ahorros que clientes dejan en el banco")
    
    # REGLA: Suma de TODOS los valores
    promedio_pasivos = df[pasivos_col].mean()
    mediana_pasivos = df[pasivos_col].median()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(f"Suma {pasivos_col}", f"${suma_pasivos:,.0f}")
    with col2:
        st.metric("Promedio", f"${promedio_pasivos:,.0f}")
    with col3:
        st.metric("Mediana", f"${mediana_pasivos:,.0f}")
    
    st.divider()
    
    # Productos que componen PASIVOS
    st.subheader("📦 Composición de PASIVOS")
    
    productos_pasivos_data = []
    for col in pasivos_productos:
        product_name = col.replace('Saldo', '').strip()
        
        suma = df[col].sum()
        promedio = df[col].mean()
        mediana = df[col].median()
        n_clientes = (df[col] > 0).sum()
        
        productos_pasivos_data.append({
            'Producto': product_name,
            'Suma': suma,
            'Promedio': promedio,
            'Mediana': mediana,
            'N° Clientes (>0)': n_clientes
        })
    
    df_prod_pasivos = pd.DataFrame(productos_pasivos_data).sort_values('Suma', ascending=False)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        fig = px.pie(
            df_prod_pasivos,
            values='Suma',
            names='Producto',
            title='Composición de PASIVOS',
            color_discrete_sequence=px.colors.sequential.Blues_r
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.dataframe(
            df_prod_pasivos.style.format({
                'Suma': '${:,.0f}',
                'Promedio': '${:,.0f}',
                'Mediana': '${:,.0f}',
                'N° Clientes (>0)': '{:,}'
            }),
            use_container_width=True,
            hide_index=True
        )

st.divider()
st.caption("💰 Ecuación Contable: ACTIVO - PASIVO = PATRIMONIO NETO")
