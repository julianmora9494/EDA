"""
Streamlit Dashboard - Página principal (Carga de archivos).
"""
import streamlit as st
import requests
from pathlib import Path

# Configuración de la página
st.set_page_config(
    page_title="EDA Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URL de la API
import os
try:
    # Intentar leer desde secrets de Streamlit Cloud
    API_URL = st.secrets.get("API_URL", "http://localhost:8000")
except:
    # Fallback a variable de entorno o localhost
    API_URL = os.getenv("API_URL", "http://localhost:8000")

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">📊 EDA Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Análisis Exploratorio Automatizado de Datos</div>', unsafe_allow_html=True)

st.divider()

# Inicializar session state
if "dataset_id" not in st.session_state:
    st.session_state.dataset_id = None
if "profile" not in st.session_state:
    st.session_state.profile = None

# Sidebar: Estado del dataset
with st.sidebar:
    st.header("Estado del Dataset")
    
    if st.session_state.dataset_id:
        st.success(f"✓ Dataset cargado")
        st.code(f"ID: {st.session_state.dataset_id[:16]}...")
        
        if st.button("🗑️ Limpiar dataset"):
            st.session_state.dataset_id = None
            st.session_state.profile = None
            st.rerun()
    else:
        st.info("No hay dataset cargado")
    
    st.divider()
    
    st.markdown("""
    ### Navegación
    
    1. **📊 Resumen** - Overview general
    2. **🔍 Calidad** - Missing, duplicados
    3. **💰 Patrimonial** - Concentración, Pareto, por producto
    4. **🏦 Productos** - Cross-sell, profundidad, univariado
    5. **🌎 Geográfico** - Mapa, distribución por país
    6. **🔗 Relaciones** - Correlaciones
    7. **📋 Conclusiones** - Hallazgos y recomendaciones
    8. **💾 Descargas** - Exportar resultados
    """)

# Main content: Upload de archivo
st.header("📤 Carga de Archivo Excel o CSV")

col1, col2 = st.columns([2, 1])

with col1:
    uploaded_file = st.file_uploader(
        "Selecciona un archivo Excel o CSV",
        type=["xlsx", "xls", "csv"],
        help="Sube un archivo Excel o CSV para analizar. Para Excel, el sistema detectará automáticamente las hojas disponibles."
    )

with col2:
    st.info("""
    **Formatos soportados:**
    - Excel (.xlsx, .xls)
    - CSV (.csv)
    - Tamaño máx: 100 MB
    - Excel: una o múltiples hojas
    """)

if uploaded_file is not None:
    st.divider()
    
    with st.spinner("Subiendo archivo y generando perfil EDA..."):
        try:
            # Subir archivo a la API
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            response = requests.post(f"{API_URL}/datasets/upload?auto_profile=true", files=files)
            
            if response.status_code == 200:
                result = response.json()
                dataset_id = result["dataset_id"]
                
                st.session_state.dataset_id = dataset_id
                
                st.success(f"✅ Archivo subido exitosamente: **{result['filename']}** ({result['file_size_mb']} MB)")
                
                # Mostrar info de hojas
                st.info(f"📄 Hojas detectadas: {', '.join(result['sheet_names'])}")
                st.info(f"🔍 Analizando hoja: **{result['selected_sheet']}**")
                
                # Obtener perfil
                with st.spinner("Cargando perfil EDA..."):
                    profile_response = requests.get(f"{API_URL}/datasets/{dataset_id}/profile")
                    
                    if profile_response.status_code == 200:
                        st.session_state.profile = profile_response.json()
                        
                        # Preview rápido
                        st.divider()
                        st.subheader("Vista Rápida del Análisis")
                        
                        overview = st.session_state.profile["overview"]
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Filas", f"{overview['n_rows']:,}")
                        with col2:
                            st.metric("Columnas", f"{overview['n_columns']:,}")
                        with col3:
                            st.metric("Memoria", f"{overview['memory_mb']:.2f} MB")
                        with col4:
                            n_insights = len(st.session_state.profile.get("insights", []))
                            st.metric("Hallazgos", n_insights)
                        
                        st.success("✅ Perfil EDA generado exitosamente. Usa el menú lateral para explorar.")
                        
                        # Botón para ir a Resumen
                        st.markdown("### Siguiente paso")
                        st.info("👈 Usa el menú lateral para navegar a **Resumen** y explorar el análisis completo.")
                    else:
                        st.error(f"Error al obtener perfil: {profile_response.text}")
            else:
                st.error(f"Error al subir archivo: {response.text}")
        
        except requests.exceptions.ConnectionError:
            st.error("""
            ❌ **No se puede conectar con la API**
            
            Asegúrate de que el servidor FastAPI esté corriendo:
            
            ```bash
            python -m uvicorn api.main:app --reload --port 8000
            ```
            """)
        except Exception as e:
            st.error(f"Error inesperado: {str(e)}")

else:
    st.markdown("""
    ### Instrucciones
    
    1. **Sube un archivo Excel o CSV** usando el botón de arriba
    2. El sistema analizará automáticamente:
       - Tipos de variables (numérica, categórica, fecha, texto, ID)
       - Calidad de datos (missing, duplicados, valores inválidos)
       - Estadísticas descriptivas por columna
       - Correlaciones y asociaciones
       - Hallazgos automáticos
    3. Explora los resultados usando el **menú lateral**
    
    ### Ejemplo
    
    Si quieres probar con un dataset de ejemplo, usa `workspace/base_panama.xlsx` (3,838 filas × 33 columnas) o `workspace/base_panama_mejorada.csv`.
    """)

# Footer
st.divider()
st.caption("EDA Dashboard v1.0 | FastAPI + Streamlit + Pandas | Análisis Exploratorio Transversal")
