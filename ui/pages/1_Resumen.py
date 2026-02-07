"""
Página de Resumen: Overview general del dataset.
"""
import streamlit as st
import sys
from pathlib import Path

# Añadir ruta para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Imports relativos que funcionan en Streamlit Cloud
try:
    from components.metrics import display_overview_card, display_column_roles_summary
    from components.tables import display_dataframe_preview, display_columns_table
except ImportError:
    # Fallback para desarrollo local
    from ui.components.metrics import display_overview_card, display_column_roles_summary
    from ui.components.tables import display_dataframe_preview, display_columns_table

st.set_page_config(page_title="Resumen - EDA Dashboard", page_icon="📊", layout="wide")

st.title("📊 Resumen General")

with st.expander("ℹ️ ¿Qué muestra esta página?", expanded=False):
    st.markdown("""
    ### Resumen General del Dataset
    
    Esta página presenta una **vista panorámica** de tu dataset:
    
    **📊 Overview:**
    - **Filas/Columnas**: Dimensiones del dataset
    - **Memoria**: Espacio que ocupa en RAM
    - **Duplicados**: % de filas repetidas
    
    **🏷️ Distribución de Tipos:**
    El sistema **infiere automáticamente** el rol de cada variable:
    - **Numéricas**: Variables con valores numéricos continuos
    - **Categóricas (baja/alta cardinalidad)**: Variables con categorías (pocas o muchas)
    - **Fechas**: Variables temporales
    - **Booleanas**: Variables binarias (Sí/No, True/False)
    - **Texto**: Campos de texto largo
    - **IDs**: Identificadores únicos (alta cardinalidad + patrones)
    - **Constantes**: Variables con 1 solo valor (no aportan información)
    
    **📋 Detalle de Columnas:**
    - **Score de Relevancia**: Prioriza variables por utilidad exploratoria (0-100)
      - Penaliza: missing, constantes, IDs
      - Premia: variabilidad, entropía, rangos amplios
    """)

# Verificar que hay datos cargados
if "profile" not in st.session_state or st.session_state.profile is None:
    st.warning("⚠️ No hay dataset cargado. Ve a la página principal para subir un archivo.")
    st.stop()

profile = st.session_state.profile

# Overview
display_overview_card(profile["overview"])

st.divider()

# Distribución de tipos
display_column_roles_summary(profile["column_roles"])

st.divider()

# Análisis de distribución de variables
st.subheader("📈 Análisis de Distribución")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Variables Numéricas")
    numeric_cols = [col for col in profile["columns"] if col.get("role") == "numeric"]
    if numeric_cols:
        st.metric("Total", len(numeric_cols))
        
        # Estadísticas agregadas
        avg_missing = sum(col.get("pct_missing", 0) for col in numeric_cols) / len(numeric_cols)
        st.metric("% Missing promedio", f"{avg_missing:.1f}%")
        
        # Variables con outliers
        with_outliers = sum(1 for col in numeric_cols if col.get("n_unique", 0) > 20)
        st.metric("Con suficiente variabilidad", with_outliers)
    else:
        st.info("No hay variables numéricas")

with col2:
    st.markdown("### Variables Categóricas")
    cat_cols = [col for col in profile["columns"] if col.get("role") in ["categorical_low_card", "categorical_high_card"]]
    if cat_cols:
        st.metric("Total", len(cat_cols))
        
        # Cardinalidad promedio
        avg_card = sum(col.get("n_unique", 0) for col in cat_cols) / len(cat_cols)
        st.metric("Cardinalidad promedio", f"{avg_card:.0f}")
        
        # Alta cardinalidad
        high_card = sum(1 for col in cat_cols if col.get("role") == "categorical_high_card")
        st.metric("Alta cardinalidad", high_card)
    else:
        st.info("No hay variables categóricas")

st.divider()

# Preview de datos
display_dataframe_preview(profile["preview"])

st.divider()

# Tabla de columnas
st.subheader("📋 Detalle de Columnas")

# Filtros
col1, col2 = st.columns([1, 3])

with col1:
    role_filter = st.multiselect(
        "Filtrar por tipo",
        options=list(set(profile["column_roles"].values())),
        default=[]
    )

with col2:
    sort_by = st.selectbox(
        "Ordenar por",
        options=["relevance_score", "name", "pct_missing", "n_unique"],
        format_func=lambda x: {
            "relevance_score": "Relevancia",
            "name": "Nombre",
            "pct_missing": "% Missing",
            "n_unique": "# Únicos"
        }[x]
    )

# Aplicar filtros
columns = profile["columns"]

if role_filter:
    columns = [col for col in columns if col.get("role") in role_filter]

# Aplicar orden
if sort_by == "name":
    columns = sorted(columns, key=lambda x: x.get("name", ""))
elif sort_by in ["pct_missing", "n_unique", "relevance_score"]:
    columns = sorted(columns, key=lambda x: x.get(sort_by, 0), reverse=True)

display_columns_table(columns)

# Información adicional
st.divider()

col1, col2 = st.columns(2)

with col1:
    st.info(f"""
    **Información del Perfil**
    - Dataset ID: `{profile['dataset_id'][:16]}...`
    - Hoja: `{profile['sheet_name']}`
    - Perfilado: {profile['profiled_at']}
    - Duración: {profile['profile_duration_seconds']:.2f}s
    - Muestreado: {'Sí' if profile['sampled'] else 'No'}
    """)

with col2:
    from_cache = profile.get("from_cache", False)
    if from_cache:
        st.success("✅ Perfil cargado desde cache (rápido)")
    else:
        st.info("🆕 Perfil generado recientemente")
