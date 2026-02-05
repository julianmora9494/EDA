"""
Conclusiones Ejecutivas y Recomendaciones
Enfoque: Resumen ejecutivo para presentación a líderes
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

st.set_page_config(page_title="Conclusiones Ejecutivas", page_icon="📋", layout="wide")

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

# Verificar datos
if "profile" not in st.session_state or st.session_state.profile is None:
    st.warning("⚠️ No hay dataset cargado.")
    st.stop()

profile = st.session_state.profile
dataset_id = st.session_state.dataset_id

st.title("📋 Conclusiones Ejecutivas")
st.caption("Resumen de hallazgos clave y recomendaciones estratégicas")

# Identificar columnas disponibles
all_columns = [col['name'] for col in profile['columns']]

saldo_total_cols = [col for col in all_columns if 'saldo' in col.lower() and 'total' in col.lower()]
activos_cols = [col for col in all_columns if 'activo' in col.lower() and 'saldo' in col.lower()]
pasivos_cols = [col for col in all_columns if 'pasivo' in col.lower() and 'saldo' in col.lower()]
total_cuentas_cols = [col for col in all_columns if 'total' in col.lower() and 'cuenta' in col.lower()]
edad_cols = [col for col in all_columns if 'edad' in col.lower()]
banca_cols = [col for col in all_columns if 'banca' in col.lower()]

saldo_col = saldo_total_cols[0] if saldo_total_cols else None
activos_col = activos_cols[0] if activos_cols else None
pasivos_col = pasivos_cols[0] if pasivos_cols else None
cuentas_col = total_cuentas_cols[0] if total_cuentas_cols else None
edad_col = edad_cols[0] if edad_cols else None
banca_col = banca_cols[0] if banca_cols else None

if not saldo_col:
    st.error("❌ No se encontró columna de Saldo Total")
    st.stop()

# Obtener datos
@st.cache_data
def get_data(dataset_id, columns_to_get):
    """Obtiene datos para análisis"""
    try:
        cols_str = ",".join(columns_to_get)
        response = requests.get(
            f"{API_URL}/datasets/{dataset_id}/data/columns",
            params={"columns": cols_str}
        )
        if response.status_code == 200:
            data = response.json()['data']
            return pd.DataFrame(data)
        return None
    except:
        return None

columns_to_fetch = [saldo_col]
if activos_col:
    columns_to_fetch.append(activos_col)
if pasivos_col:
    columns_to_fetch.append(pasivos_col)
if cuentas_col:
    columns_to_fetch.append(cuentas_col)
if edad_col:
    columns_to_fetch.append(edad_col)
if banca_col:
    columns_to_fetch.append(banca_col)

df = get_data(dataset_id, columns_to_fetch)

if df is None:
    st.error("❌ No se pudieron cargar los datos")
    st.stop()

# Limpiar datos
df = df.replace([None], np.nan)
for col in df.columns:
    if col not in [banca_col]:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# ==================== RESUMEN EJECUTIVO ====================
st.header("📊 Resumen Ejecutivo")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Registros", f"{len(df):,}")
    st.caption("Base analizada")

with col2:
    # REGLA: TOTAL = Activos + Pasivos
    if activos_col and pasivos_col:
        suma_activos = df[activos_col].sum()
        suma_pasivos = df[pasivos_col].sum()
        total_calculado = suma_activos + suma_pasivos
        patrimonio_total = total_calculado  # Para usar después
        st.metric("TOTAL (A + P)", f"${total_calculado:,.0f}")
        st.caption("Activos + Pasivos")
    else:
        patrimonio_total = df[saldo_col].sum()
        st.metric("Patrimonio Total", f"${patrimonio_total:,.0f}")
        st.caption(f"Suma de {saldo_col}")

with col3:
    saldo_promedio = df[saldo_col].mean()
    st.metric("Saldo Promedio", f"${saldo_promedio:,.0f}")
    st.caption("Por registro")

with col4:
    if cuentas_col:
        productos_promedio = df[cuentas_col].mean()
        st.metric("Productos Promedio", f"{productos_promedio:.1f}")
        st.caption(f"Por registro")

st.divider()

# ==================== HALLAZGOS CLAVE ====================
st.header("🔍 Hallazgos Clave")

# Calcular concentración
saldo_sorted = df[saldo_col].dropna().sort_values(ascending=False).reset_index(drop=True)
idx_10 = int(len(saldo_sorted) * 0.10)
pct_10 = (saldo_sorted.head(idx_10).sum() / saldo_sorted.sum() * 100)

p90 = df[saldo_col].quantile(0.90)
p99 = df[saldo_col].quantile(0.99)

alto_valor_count = len(df[df[saldo_col] >= p99])
alto_valor_patrimonio = df[df[saldo_col] >= p99][saldo_col].sum()
alto_valor_pct = (alto_valor_patrimonio / patrimonio_total * 100)

# Hallazgo 1: Concentración
st.subheader("1️⃣ Concentración Patrimonial")

col1, col2 = st.columns([2, 1])

with col1:
    if pct_10 > 70:
        st.error(f"""
        🔴 **Alta Concentración de Riqueza**
        
        - El **top 10%** concentra **{pct_10:.1f}%** del patrimonio total
        - El **top 1%** representa **{alto_valor_pct:.1f}%** del patrimonio
        - Solo **{alto_valor_count} registros** superan **${p99:,.0f}**
        
        **Implicación**: Alta dependencia de pocos registros de alto valor.
        """)
    elif pct_10 > 50:
        st.warning(f"""
        🟡 **Concentración Moderada-Alta**
        
        - El **top 10%** concentra **{pct_10:.1f}%** del patrimonio total
        - Típico en datos financieros
        """)
    else:
        st.info(f"""
        🟢 **Concentración Moderada**
        
        - El **top 10%** concentra **{pct_10:.1f}%** del patrimonio total
        - Distribución relativamente balanceada
        """)

with col2:
    st.metric("Top 10% Concentra", f"{pct_10:.1f}%")
    st.metric("Top 1% (Alto Valor)", f"{alto_valor_count}")
    st.metric("Patrimonio Top 1%", f"${alto_valor_patrimonio:,.0f}")

st.divider()

# Hallazgo 2: Profundidad (si existe columna de cuentas)
if cuentas_col:
    st.subheader("2️⃣ Profundidad de Relación")
    
    mono_product = len(df[df[cuentas_col] == 1])
    mono_pct = (mono_product / len(df) * 100)
    productos_promedio = df[cuentas_col].mean()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if mono_pct > 30:
            st.warning(f"""
            🟡 **Baja Profundidad de Relación**
            
            - **{mono_pct:.1f}%** de registros tiene solo **1 producto**
            - Productos promedio: **{productos_promedio:.1f}**
            
            **Implicación**: Alto potencial de crecimiento vía cross-sell.
            """)
        else:
            st.success(f"""
            ✅ **Buena Profundidad de Relación**
            
            - Solo **{mono_pct:.1f}%** tiene 1 producto
            - Productos promedio: **{productos_promedio:.1f}**
            """)
    
    with col2:
        st.metric("Mono-producto", f"{mono_product:,}")
        st.metric("% Mono-producto", f"{mono_pct:.1f}%")
        multi_product = len(df[df[cuentas_col] >= 3])
        st.metric("Multi-producto (≥3)", f"{multi_product:,}")
    
    st.divider()

# Hallazgo 3: Calidad de Datos
st.subheader("3️⃣ Calidad de Datos")

missing_data = []
for col in columns_to_fetch:
    if col in df.columns:
        missing_pct = (df[col].isna().sum() / len(df) * 100)
        missing_data.append({'Variable': col, 'Missing %': missing_pct})

df_missing = pd.DataFrame(missing_data)

col1, col2 = st.columns([2, 1])

with col1:
    max_missing = df_missing['Missing %'].max()
    
    if max_missing > 10:
        st.error(f"""
        🔴 **Problemas de Calidad de Datos**
        
        - Variables clave con datos faltantes superiores al 10%
        - Impacto en análisis y segmentación
        
        **Acción requerida**: Validar fuentes de datos y procesos de captura.
        """)
    elif max_missing > 5:
        st.warning(f"""
        🟡 **Calidad de Datos Aceptable**
        
        - Algunas variables con datos faltantes (5-10%)
        - Monitorear calidad en futuras cargas
        """)
    else:
        st.success(f"""
        ✅ **Excelente Calidad de Datos**
        
        - Variables clave con menos del 5% de datos faltantes
        - Base confiable para análisis y decisiones
        """)

with col2:
    st.dataframe(
        df_missing.style.format({'Missing %': '{:.1f}%'}),
        use_container_width=True,
        hide_index=True
    )

st.divider()

# Hallazgo 4: Distribución por Banca (si existe)
if banca_col and banca_col in df.columns:
    st.subheader(f"4️⃣ Distribución por {banca_col}")
    
    banca_stats = df.groupby(banca_col).agg({
        saldo_col: ['count', 'sum', 'mean']
    }).round(0)
    
    banca_stats.columns = ['N° Registros', 'Patrimonio Total', 'Saldo Promedio']
    banca_stats['% Registros'] = (banca_stats['N° Registros'] / len(df) * 100).round(1)
    banca_stats['% Patrimonio'] = (banca_stats['Patrimonio Total'] / patrimonio_total * 100).round(1)
    
    banca_stats = banca_stats.sort_values('Patrimonio Total', ascending=False)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.dataframe(
            banca_stats.style.format({
                'N° Registros': '{:,.0f}',
                'Patrimonio Total': '${:,.0f}',
                'Saldo Promedio': '${:,.0f}',
                '% Registros': '{:.1f}%',
                '% Patrimonio': '{:.1f}%'
            }),
            use_container_width=True
        )
    
    with col2:
        # Identificar segmento con mayor concentración
        top_banca = banca_stats.index[0]
        top_pct = banca_stats.loc[top_banca, '% Patrimonio']
        
        st.info(f"""
        💡 **Insight**:
        
        - **{top_banca}** concentra **{top_pct:.1f}%** del patrimonio total
        - Diferencias significativas entre segmentos
        
        **Acción**: Estrategia diferenciada por segmento.
        """)
    
    st.divider()

# Hallazgo 5: Apalancamiento (si existen activos y pasivos)
if activos_col and pasivos_col:
    st.subheader("5️⃣ Perfil de Apalancamiento")
    
    df_apalancamiento = df[(df[activos_col] > 0) & (df[pasivos_col] > 0)].copy()
    df_apalancamiento['Ratio A/P'] = df_apalancamiento[activos_col] / df_apalancamiento[pasivos_col]
    
    muy_apalancados = len(df_apalancamiento[df_apalancamiento['Ratio A/P'] < 0.5])
    patrimoniales = len(df_apalancamiento[df_apalancamiento['Ratio A/P'] > 2])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Muy Apalancados", f"{muy_apalancados:,}", help="Pasivos > 2x Activos")
    
    with col2:
        balanceados = len(df_apalancamiento) - muy_apalancados - patrimoniales
        st.metric("Balanceados", f"{balanceados:,}", help="0.5 ≤ A/P ≤ 2")
    
    with col3:
        st.metric("Patrimoniales", f"{patrimoniales:,}", help="Activos > 2x Pasivos")
    
    st.info(f"""
    💡 **Insight**:
    
    - **{patrimoniales:,} registros patrimoniales** (alta liquidez) → Oportunidad de colocación
    - **{muy_apalancados:,} muy apalancados** → Monitorear riesgo
    """)
    
    st.divider()

# Hallazgo 6: Ciclo de Vida (si existe edad)
if edad_col and edad_col in df.columns:
    st.subheader("6️⃣ Distribución por Edad")
    
    df['Tramo Edad'] = pd.cut(df[edad_col], bins=[0, 30, 40, 50, 60, 100], labels=['<30', '30-40', '40-50', '50-60', '60+'])
    
    lifecycle_stats = df.groupby('Tramo Edad').agg({
        saldo_col: ['count', 'mean']
    }).round(0)
    
    lifecycle_stats.columns = ['N° Registros', 'Saldo Promedio']
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.dataframe(
            lifecycle_stats.style.format({
                'N° Registros': '{:,.0f}',
                'Saldo Promedio': '${:,.0f}'
            }),
            use_container_width=True
        )
    
    with col2:
        # Identificar tramo con mayor patrimonio
        tramo_max = lifecycle_stats['Saldo Promedio'].idxmax()
        saldo_max = lifecycle_stats.loc[tramo_max, 'Saldo Promedio']
        
        senior_count = len(df[df[edad_col] >= 60])
        senior_pct = (senior_count / len(df) * 100)
        
        st.info(f"""
        💡 **Insight**:
        
        - Tramo **{tramo_max}** años tiene mayor saldo promedio (${saldo_max:,.0f})
        - Segmento senior (60+): **{senior_pct:.1f}%** de registros
        
        **Acción**: Considerar diversificación etaria si la concentración es alta.
        """)

st.divider()

# ==================== RECOMENDACIONES ====================
st.header("🎯 Recomendaciones Estratégicas")

st.success("""
**Acciones Prioritarias**:

1️⃣ **Retención de Alto Valor**:
   - Enfoque en el top 1-5% que concentra alto % del patrimonio
   - Programa de beneficios exclusivos y atención personalizada

2️⃣ **Cross-Sell** (si aplica):
   - Identificar registros con alto saldo pero pocos productos
   - Campañas de profundización de relación

3️⃣ **Calidad de Datos**:
   - Validar y corregir datos faltantes en variables clave
   - Implementar alertas de calidad en procesos de carga

4️⃣ **Segmentación**:
   - Estrategia diferenciada por segmento de valor
   - Productos y servicios adaptados a cada perfil

5️⃣ **Monitoreo Continuo**:
   - Seguimiento mensual de concentración
   - KPIs de retención, cross-sell y calidad de datos
""")

st.divider()
st.caption("📋 Reporte diseñado para presentación ejecutiva y toma de decisiones estratégicas")
