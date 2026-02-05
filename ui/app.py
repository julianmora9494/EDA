"""
Streamlit Dashboard - Página principal (Carga de archivos).
"""
import streamlit as st
import requests
import os

# Configuración de la página
st.set_page_config(
    page_title="EDA Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URL de la API
API_URL = os.getenv("API_URL", "https://eda-dashboard-api.onrender.com")

# Intentar leer desde secrets
try:
    if "API_URL" in st.secrets:
        API_URL = st.secrets["API_URL"]
except:
    pass

# Header
st.title("📊 EDA Dashboard")
st.markdown("### Análisis Exploratorio de Datos Automatizado")

# Verificar conexión con API
with st.spinner("Conectando con el servidor..."):
    try:
        response = requests.get(f"{API_URL}/", timeout=10)
        if response.status_code == 200:
            st.success("✅ Conectado al servidor")
        else:
            st.error(f"⚠️ Servidor respondió con código: {response.status_code}")
    except requests.exceptions.Timeout:
        st.warning("⏱️ El servidor está iniciando (puede tardar 30-50 segundos). Intenta de nuevo.")
    except Exception as e:
        st.error(f"❌ No se puede conectar con el servidor: {str(e)}")
        st.info(f"URL del servidor: {API_URL}")

st.divider()

# Sección de carga
st.subheader("📁 Cargar Archivo")

uploaded_file = st.file_uploader(
    "Selecciona un archivo CSV, Excel o Parquet",
    type=["csv", "xlsx", "xls", "parquet"],
    help="Formatos soportados: CSV, Excel (.xlsx, .xls), Parquet"
)

if uploaded_file is not None:
    st.info(f"📄 Archivo: **{uploaded_file.name}** ({uploaded_file.size:,} bytes)")
    
    if st.button("🚀 Analizar Datos", type="primary", use_container_width=True):
        with st.spinner("Procesando archivo..."):
            try:
                # Preparar archivo para envío
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                
                # Enviar a API
                response = requests.post(
                    f"{API_URL}/datasets/upload",
                    files=files,
                    timeout=120
                )
                
                if response.status_code == 200:
                    result = response.json()
                    dataset_id = result.get("dataset_id")
                    
                    # Guardar en session_state
                    st.session_state["dataset_id"] = dataset_id
                    st.session_state["filename"] = uploaded_file.name
                    
                    st.success("✅ Archivo procesado correctamente")
                    st.balloons()
                    
                    # Mostrar info básica
                    st.info(f"🆔 ID del dataset: `{dataset_id}`")
                    st.info("👈 Navega por las páginas en el menú lateral para ver los análisis")
                    
                else:
                    st.error(f"Error al procesar: {response.status_code}")
                    st.code(response.text)
                    
            except requests.exceptions.Timeout:
                st.error("⏱️ Timeout: El servidor tardó demasiado. Intenta con un archivo más pequeño.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Mostrar dataset actual
if "dataset_id" in st.session_state:
    st.divider()
    st.success(f"📊 Dataset activo: **{st.session_state.get('filename', 'Sin nombre')}**")
    st.caption(f"ID: `{st.session_state['dataset_id']}`")

# Footer
st.divider()
st.caption("EDA Dashboard v1.0 | FastAPI + Streamlit")
