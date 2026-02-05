"""
Análisis de Saldos: Cifras Generales de Activos y Pasivos
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

st.set_page_config(page_title="Análisis de Saldos", page_icon="💰", layout="wide")

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

st.title("💰 Análisis de Saldos")
st.caption("Análisis de saldos bancarios de Activos y Pasivos por cliente")

# Obtener total de clientes
total_clientes = profile.get("overview", {}).get("n_rows", 0)

# Obtener columnas
all_columns = [col['name'] for col in profile['columns']]

activos_col = [col for col in all_columns if 'activo' in col.lower() and 'saldo' in col.lower()][0]
pasivos_col = [col for col in all_columns if 'pasivo' in col.lower() and 'saldo' in col.lower()][0]

# Productos ACTIVOS (colocaciones)
activos_productos = [col for col in all_columns if any(x in col for x in ['Saldo TC', 'Saldo PR'])]

# Productos PASIVOS (captaciones)
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

# Total de clientes CON SALDO en cada producto
clientes_con_activos = (df[activos_col] > 0).sum()
clientes_con_pasivos = (df[pasivos_col] > 0).sum()

# Clientes SIN PRODUCTOS (con saldo = $0 en ambos)
clientes_sin_productos = total_clientes - len(set(df[df[activos_col] > 0].index) | set(df[df[pasivos_col] > 0].index))

# Análisis de desbalance por cliente (para scatter plot)
clientes_mas_activos_que_pasivos = (df[activos_col] > df[pasivos_col]).sum()
clientes_mas_pasivos_que_activos = (df[pasivos_col] > df[activos_col]).sum()

# ==================== TABS ====================
tab1, tab2, tab3 = st.tabs([
    "📊 CIFRAS GENERALES",
    "💳 ACTIVOS",
    "💰 PASIVOS"
])

# ==================== TAB 1: CIFRAS GENERALES ====================
with tab1:
    st.header("📊 CIFRAS GENERALES")
    
    # Contexto: Total de clientes
    st.info(f"📈 **Base de Datos**: Total de **{total_clientes:,} clientes** analizados")
    
    st.divider()
    
    st.markdown("### 📊 Desglose de Clientes por Tenencia de Productos")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Clientes", f"{total_clientes:,}")
        st.caption("Base completa")
    
    with col2:
        st.metric("Con ACTIVOS", f"{clientes_con_activos:,}")
        st.caption("Saldo > $0")
    
    with col3:
        st.metric("Con PASIVOS", f"{clientes_con_pasivos:,}")
        st.caption("Saldo > $0")
    
    with col4:
        st.metric("Sin Productos", f"{clientes_sin_productos:,}")
        st.caption("Saldo = $0 en ambos")
    
    st.caption("⚠️ Nota: Los clientes pueden aparecer en múltiples categorías (activos y pasivos simultáneamente)")
    
    st.divider()
    
    st.markdown("### 💰 Saldos Totales")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("**ACTIVOS TOTALES**", f"${suma_activos:,.0f}")
        st.caption("Suma de todos los saldos")
        st.caption(f"De **{clientes_con_activos:,}** clientes")
        st.caption(f"que tienen saldo > $0")
    
    with col2:
        st.metric("**PASIVOS TOTALES**", f"${suma_pasivos:,.0f}")
        st.caption("Suma de todos los saldos")
        st.caption(f"De **{clientes_con_pasivos:,}** clientes")
        st.caption(f"que tienen saldo > $0")
    
    with col3:
        ratio_ap = suma_activos / suma_pasivos if suma_pasivos > 0 else 0
        st.metric("**RATIO A/P**", f"{ratio_ap:.2f}x")
        st.caption(f"Por cada $1 en pasivos")
        st.caption(f"hay ${ratio_ap:.2f} en activos")
    
    st.divider()
    
    # Explicación clara del ratio
    st.markdown("### 📖 Interpretación del Ratio A/P")
    
    if ratio_ap > 1:
        interpretation = f"""
        **El banco tiene {ratio_ap:.2f} unidades de ACTIVOS por cada 1 unidad de PASIVOS**
        
        Esto significa que:
        - Los clientes tienen **más saldos en productos activos** (créditos, tarjetas) que en productos pasivos (depósitos)
        - Por ejemplo, si el total de depósitos es $100, los créditos suman aproximadamente ${ratio_ap*100:.0f}
        - **Implicación**: El banco está colocando más dinero en créditos del que capta en depósitos
        """
    elif ratio_ap < 1:
        interpretation = f"""
        **El banco tiene {ratio_ap:.2f} unidades de ACTIVOS por cada 1 unidad de PASIVOS**
        
        Esto significa que:
        - Los clientes tienen **más saldos en productos pasivos** (depósitos) que en productos activos (créditos)
        - Por ejemplo, si el total de créditos es $100, los depósitos suman aproximadamente ${ratio_ap*100:.0f}
        - **Implicación**: El banco está captando más depósitos de los que está colocando en créditos
        """
    else:
        interpretation = """
        **El ratio es 1.00: ACTIVOS y PASIVOS están perfectamente equilibrados**
        """
    
    st.info(interpretation)
    
    st.divider()
    
    # Comparación visual y análisis de distribución
    col1, col2 = st.columns(2)
    
    with col1:
        df_balance = pd.DataFrame({
            'Tipo': ['ACTIVOS', 'PASIVOS'],
            'Monto': [suma_activos, suma_pasivos]
        })
        
        fig = px.bar(
            df_balance,
            x='Tipo',
            y='Monto',
            title='Comparación: ACTIVOS vs PASIVOS',
            color='Tipo',
            color_discrete_map={
                'ACTIVOS': '#2ecc71',
                'PASIVOS': '#3498db'
            },
            text='Monto',
            labels={'Monto': 'Monto ($)'}
        )
        fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Scatter plot ACTIVOS vs PASIVOS - Definir df_plot ANTES de usarlo
    df_plot = df[(df[activos_col].notna()) & (df[pasivos_col].notna()) & 
                 (df[activos_col] > 0) & (df[pasivos_col] > 0)].copy()
    
    # Análisis profesional del desbalance
    st.markdown("### 🎯 Insight Principal")
    
    if clientes_mas_activos_que_pasivos > clientes_mas_pasivos_que_activos:
        insight = f"""
        **Mayoría de clientes con ACTIVOS dominantes**
        
        De los {len(df_plot):,} clientes que tienen AMBOS productos, 
        el {(clientes_mas_activos_que_pasivos/len(df_plot)*100):.1f}% tienen más créditos que depósitos.
        Esto indica una cartera de colocaciones activa.
        """
    else:
        insight = f"""
        **Mayoría de clientes con PASIVOS dominantes**
        
        De los {len(df_plot):,} clientes que tienen AMBOS productos,
        el {(clientes_mas_pasivos_que_activos/len(df_plot)*100):.1f}% tienen más depósitos que créditos.
        Esto indica una fuerte base de captaciones.
        """
    
    st.success(insight)
    
    st.divider()
    
    # Scatter plot ACTIVOS vs PASIVOS
    st.subheader("📈 Análisis Comparativo: ACTIVOS vs PASIVOS")
    
    # Información clara sobre el filtro
    st.info(f"""
    📊 **Metodología de este análisis**:
    
    Este análisis SOLO compara clientes que tienen AMBOS productos con saldo positivo:
    - **Total de clientes en la base**: {total_clientes:,} clientes únicos
    - **Clientes CON ACTIVOS (saldo > $0)**: {clientes_con_activos:,}
    - **Clientes CON PASIVOS (saldo > $0)**: {clientes_con_pasivos:,}
    - **Clientes analizados aquí** (tienen AMBOS con saldo > $0): **{len(df_plot):,} clientes**
    
    ℹ️ Los gráficos anteriores muestran el total de clientes. Este gráfico solo muestra 
    clientes que tienen simultáneamente saldo en activos Y pasivos para hacer comparación válida.
    """)
    
    # Contar clientes por encima y debajo de la diagonal
    clientes_encima = (df_plot[activos_col] > df_plot[pasivos_col]).sum()
    clientes_debajo = (df_plot[pasivos_col] > df_plot[activos_col]).sum()
    
    fig = px.scatter(
        df_plot,
        x=pasivos_col,
        y=activos_col,
        color=banca_col if banca_col else None,
        title=f'ACTIVOS vs PASIVOS | 🔴 Arriba: {clientes_encima:,} | 🔵 Abajo: {clientes_debajo:,}',
        log_x=True,
        log_y=True,
        opacity=0.6,
        labels={
            pasivos_col: 'PASIVOS ($)',
            activos_col: 'ACTIVOS ($)'
        }
    )
    
    # Línea de referencia A = P
    max_val = max(df_plot[activos_col].max(), df_plot[pasivos_col].max())
    fig.add_trace(go.Scatter(
        x=[1, max_val],
        y=[1, max_val],
        mode='lines',
        name='Equilibrio (A = P)',
        line=dict(color='red', width=2, dash='dash')
    ))
    
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # Explicación de resultados - mejor alineación
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("🔴 ARRIBA de la línea", f"{clientes_encima:,} clientes")
        pct_encima = (clientes_encima / len(df_plot) * 100) if len(df_plot) > 0 else 0
        st.caption(f"{pct_encima:.1f}% de estos {len(df_plot):,} clientes")
        st.info(f"""
        **Clientes con AMBOS productos donde:**
        SALDO ACTIVOS > SALDO PASIVOS
        
        **Ejemplo**: Si un cliente tiene:
        - $1,000 en créditos (activos)
        - $300 en depósitos (pasivos)
        → Está ARRIBA porque $1,000 > $300
        """)
    
    with col2:
        st.metric("🔵 ABAJO de la línea", f"{clientes_debajo:,} clientes")
        pct_debajo = (clientes_debajo / len(df_plot) * 100) if len(df_plot) > 0 else 0
        st.caption(f"{pct_debajo:.1f}% de estos {len(df_plot):,} clientes")
        st.info(f"""
        **Clientes con AMBOS productos donde:**
        SALDO PASIVOS > SALDO ACTIVOS
        
        **Ejemplo**: Si un cliente tiene:
        - $200 en créditos (activos)
        - $2,000 en depósitos (pasivos)
        → Está ABAJO porque $2,000 > $200
        """)

# ==================== TAB 2: ACTIVOS ====================
with tab2:
    st.header(f"💳 {activos_col.upper()}")
    st.caption("Colocaciones: Préstamos y créditos que clientes deben al banco")
    
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
st.caption("💰 Análisis de Saldos Bancarios - Activos y Pasivos por Cliente")
