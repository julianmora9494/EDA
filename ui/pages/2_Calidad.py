"""
Página de Calidad de Datos: Missing, duplicados, constantes, hallazgos.
"""
import streamlit as st
import sys
from pathlib import Path

# Añadir ruta para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Imports relativos que funcionan en Streamlit Cloud
try:
    from components.charts import plot_missing_heatmap
    from components.tables import display_insights_table
except ImportError:
    # Fallback para desarrollo local
    from ui.components.charts import plot_missing_heatmap
    from ui.components.tables import display_insights_table

st.set_page_config(page_title="Calidad - EDA Dashboard", page_icon="🔍", layout="wide")

st.title("🔍 Calidad de Datos")

with st.expander("ℹ️ ¿Qué muestra esta página?", expanded=False):
    st.markdown("""
    ### Análisis de Calidad de Datos
    
    Esta página detecta **problemas de calidad** que pueden afectar tu análisis:
    
    **❌ Valores Faltantes (Missing):**
    - **% Missing Global**: Proporción total de celdas vacías
    - **Por Columna**: Identifica columnas con muchos missing (>50% = problema)
    - **Impacto**: Valores faltantes pueden sesgar análisis y modelos
    
    **🔄 Filas Duplicadas:**
    - **Detección**: Filas completamente idénticas
    - **% Duplicación**: Si >5% puede indicar errores de carga
    - **Acción**: Decidir si eliminar o investigar causa
    
    **⚪ Columnas Constantes:**
    - **Constante**: Solo 1 valor único (no aporta información)
    - **Casi Constante**: 2 valores pero uno domina >99%
    - **Acción**: Considerar eliminarlas del análisis
    
    **💡 Hallazgos Automáticos:**
    - **Severidad**: Alta (🔴), Media (🟡), Baja (🟢)
    - **Categorías**: missing_data, duplicates, constants, ids, correlations
    - **Recomendaciones**: Acciones sugeridas por cada hallazgo
    """)

# Verificar que hay datos cargados
if "profile" not in st.session_state or st.session_state.profile is None:
    st.warning("⚠️ No hay dataset cargado. Ve a la página principal para subir un archivo.")
    st.stop()

profile = st.session_state.profile
quality = profile["quality"]

# KPIs de calidad
st.subheader("📊 Resumen de Calidad")

col1, col2, col3, col4 = st.columns(4)

with col1:
    pct_missing = quality["missing"]["pct_missing_global"]
    st.metric("% Missing Global", f"{pct_missing:.1f}%")

with col2:
    n_cols_missing = quality["missing"]["columns_with_missing"]
    st.metric("Columnas con Missing", n_cols_missing)

with col3:
    pct_dup = quality["duplicates"]["pct_duplicate_rows"]
    st.metric("% Filas Duplicadas", f"{pct_dup:.1f}%")

with col4:
    n_const = quality["constants"]["n_constant_columns"]
    st.metric("Columnas Constantes", n_const)

st.divider()

# Missing values
st.subheader("❌ Valores Faltantes")

missing_by_col = quality["missing"]["missing_by_column"]

if missing_by_col:
    plot_missing_heatmap(missing_by_col)
    
    # Tabla detallada
    with st.expander("📋 Ver tabla detallada de missing"):
        import pandas as pd
        df_missing = pd.DataFrame(missing_by_col)
        st.dataframe(df_missing, use_container_width=True, hide_index=True)
else:
    st.success("✅ No hay valores faltantes en el dataset")

st.divider()

# Duplicados
st.subheader("🔄 Filas Duplicadas")

col1, col2 = st.columns(2)

with col1:
    dup = quality["duplicates"]
    st.metric("Total de filas", f"{dup['n_total_rows']:,}")
    st.metric("Filas duplicadas", f"{dup['n_duplicate_rows']:,}")

with col2:
    st.metric("Filas únicas", f"{int(dup['n_unique_rows']):,}")
    st.metric("% Duplicación", f"{dup['pct_duplicate_rows']:.2f}%")

if dup['pct_duplicate_rows'] > 5:
    st.warning("⚠️ El dataset tiene un nivel significativo de duplicación (>5%)")
elif dup['n_duplicate_rows'] > 0:
    st.info(f"💡 {dup['n_duplicate_rows']} filas duplicadas detectadas")
else:
    st.success("✅ No hay filas duplicadas")

st.divider()

# Columnas constantes
st.subheader("⚪ Columnas Constantes / Casi Constantes")

constants = quality["constants"]

if constants["constant_columns"]:
    for const in constants["constant_columns"]:
        if const["type"] == "constant":
            st.warning(f"**{const['column']}**: Constante (valor: `{const.get('value', 'N/A')}`)")
        elif const["type"] == "near_constant":
            st.info(f"**{const['column']}**: Casi constante ({const['n_unique']} valores, {const['dominant_pct']:.1f}% dominante)")
else:
    st.success("✅ No hay columnas constantes")

st.divider()

# Hallazgos automáticos
display_insights_table(profile["insights"])

# Resumen final
st.divider()

st.subheader("📝 Recomendaciones")

recommendations = []

if quality["missing"]["pct_missing_global"] > 20:
    recommendations.append("🔴 Alto nivel de missing global (>20%). Considere estrategias de imputación o eliminación.")

if quality["duplicates"]["pct_duplicate_rows"] > 10:
    recommendations.append("🔴 Alto nivel de duplicación (>10%). Considere eliminar duplicados.")

if constants["n_constant_columns"] > 0:
    recommendations.append(f"🟡 {constants['n_constant_columns']} columnas constantes pueden eliminarse (no aportan información).")

# Columnas con >80% missing
high_missing = [col for col in quality["missing"]["missing_by_column"] if col["pct_missing"] > 80]
if high_missing:
    recommendations.append(f"🟡 {len(high_missing)} columnas con >80% missing. Considere eliminarlas: {', '.join([c['column'] for c in high_missing[:5]])}")

if not recommendations:
    st.success("✅ La calidad del dataset es buena. No se detectaron problemas críticos.")
else:
    for rec in recommendations:
        st.markdown(f"- {rec}")
