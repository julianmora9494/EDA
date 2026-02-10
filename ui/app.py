"""
Streamlit Dashboard - Página principal (Carga de archivos).
"""
import streamlit as st
import requests
import os
from pathlib import Path

# Configuración de la página
st.set_page_config(
    page_title="EDA Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URL de la API - Detectar automáticamente según el entorno
def get_api_url():
    """Obtener URL de la API según el entorno."""
    # 1. Secrets de Streamlit Cloud (producción)
    try:
        if "API_URL" in st.secrets:
            return st.secrets["API_URL"]
    except:
        pass
    
    # 2. Variable de entorno
    api_url = os.getenv("API_URL")
    if api_url:
        return api_url
    
    # 3. Detectar si estamos en Streamlit Cloud
    if os.getenv("STREAMLIT_SHARING_MODE") or os.getenv("STREAMLIT_SERVER_PORT"):
        return "https://eda-dashboard-api.onrender.com"
    
    # 4. Desarrollo local
    return "http://localhost:8000"

API_URL = get_api_url()

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
    .upload-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin: 2rem 0;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 1.2rem;
        padding: 0.75rem;
        border: none;
        border-radius: 8px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">📊 Exploratory Data Analysis (EDA)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Análisis Exploratorio de Datos Automatizado</div>', unsafe_allow_html=True)

# Verificar conexión con API (sin bloquear si falla)
try:
    with st.spinner("Verificando conexión con el servidor..."):
        response = requests.get(f"{API_URL}/health", timeout=10)
        if response.status_code == 200:
            st.success("✅ Conectado al servidor correctamente")
        else:
            st.warning(f"⚠️ Servidor respondió con código: {response.status_code}. El backend puede estar iniciando...")
except Exception as e:
    st.warning(f"⚠️ El servidor está iniciando... Esto puede tomar 30-60 segundos en el plan gratuito de Render.")
    st.info(f"🔗 Backend: {API_URL}")
    st.caption("💡 La app funcionará una vez que el backend despierte. Intenta recargar en unos segundos.")

st.divider()

# Información del dashboard
col1, col2, col3 = st.columns(3)

with col1:
    st.info("📊 **Análisis Completo**\n\nEstadísticas descriptivas, distribuciones y correlaciones")

with col2:
    st.info("🔍 **Calidad de Datos**\n\nDetección de valores faltantes, duplicados y outliers")

with col3:
    st.info("📈 **Visualizaciones**\n\nGráficos interactivos y reportes exportables")

st.divider()

# Cargar datos demo automáticamente al inicio
if "auto_loaded" not in st.session_state:
    st.session_state.auto_loaded = True
    try:
        import pandas as pd
        from pathlib import Path
        
        demo_file_path = Path(__file__).parent.parent / "base_panama_mejorada.csv"
        
        if demo_file_path.exists():
            # Leer el archivo demo
            with open(demo_file_path, 'rb') as f:
                demo_data = f.read()
            
            # Simular uploaded_file
            class DemoFile:
                def __init__(self, name, data):
                    self.name = name
                    self.size = len(data)
                    self.type = "text/csv"
                    self._data = data
                
                def getvalue(self):
                    return self._data
            
            st.session_state.demo_file = DemoFile("base_panama_mejorada.csv", demo_data)
    except Exception as e:
        st.session_state.demo_file = None

# Usar archivo demo si existe, sino mostrar uploader
uploaded_file = None

if hasattr(st.session_state, 'demo_file') and st.session_state.demo_file is not None:
    uploaded_file = st.session_state.demo_file
    st.info("📊 **Dashboard cargado con datos de ejemplo**. Puedes cargar tu propio archivo abajo si lo deseas.")

# Sección de carga de archivos (opcional)
with st.expander("📁 Cargar tus propios datos (opcional)", expanded=False):
    user_file = st.file_uploader(
        "Selecciona un archivo CSV, Excel o Parquet",
        type=["csv", "xlsx", "xls", "parquet"],
        help="Formatos soportados: CSV, Excel (.xlsx, .xls), Parquet"
    )
    
    if user_file is not None:
        uploaded_file = user_file
        st.session_state.demo_file = None  # Limpiar demo si se carga archivo propio

if uploaded_file is not None:
    # Verificar si ya está procesado
    if "profile" not in st.session_state or st.session_state.get("filename") != uploaded_file.name:
        # Procesar automáticamente
        with st.spinner("Procesando archivo... Esto puede tardar unos segundos."):
            try:
                # Preparar archivo para envío
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                
                # Enviar a API
                response = requests.post(
                    f"{API_URL}/datasets/upload",
                    files=files,
                    timeout=300
                )
                
                if response.status_code == 200:
                    result = response.json()
                    dataset_id = result.get("dataset_id")
                    
                    # Obtener perfil completo
                    profile_response = requests.get(f"{API_URL}/datasets/{dataset_id}/profile")
                    
                    if profile_response.status_code == 200:
                        profile = profile_response.json()
                        
                        # Guardar en session_state
                        st.session_state["dataset_id"] = dataset_id
                        st.session_state["filename"] = uploaded_file.name
                        st.session_state["profile"] = profile
                        
                        st.success("✅ Archivo procesado y analizado correctamente")
                        st.balloons()
                        
                        # Mostrar resumen rápido
                        overview = profile.get("overview", {})
                        
                        st.markdown("### 📊 Resumen Rápido del Dataset")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("📈 Total de Filas", f"{overview.get('n_rows', 0):,}")
                        
                        with col2:
                            st.metric("📊 Total de Columnas", f"{overview.get('n_columns', 0):,}")
                        
                        with col3:
                            st.metric("💾 Memoria", f"{overview.get('memory_mb', 0):.2f} MB")
                        
                        with col4:
                            st.metric("🔄 Duplicados", f"{overview.get('n_duplicate_rows', 0):,}")
                        
                        st.divider()
                        st.info("👈 **Siguiente paso**: Navega por las páginas en el menú lateral para ver análisis detallados de tu dataset")
                    else:
                        st.error("Error al obtener el perfil del dataset")
                else:
                    st.error(f"Error al procesar el archivo: {response.status_code}")
                    st.code(response.text)
                    
            except requests.exceptions.Timeout:
                st.error("⏱️ Timeout: El servidor tardó demasiado en responder. Intenta con un archivo más pequeño.")
            except Exception as e:
                st.error(f"❌ Error al procesar el archivo: {str(e)}")
    else:
        # Ya está procesado, mostrar resumen
        if "profile" in st.session_state:
            profile = st.session_state["profile"]
            overview = profile.get("overview", {})
            
            st.success("✅ Dashboard listo para usar")
            st.markdown("### 📊 Resumen del Dataset")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📈 Total de Filas", f"{overview.get('n_rows', 0):,}")
            
            with col2:
                st.metric("📊 Total de Columnas", f"{overview.get('n_columns', 0):,}")
            
            with col3:
                st.metric("💾 Memoria", f"{overview.get('memory_mb', 0):.2f} MB")
            
            with col4:
                st.metric("🔄 Duplicados", f"{overview.get('n_duplicate_rows', 0):,}")
            
            st.divider()
            st.info("👈 **Navega por las páginas** en el menú lateral para ver análisis detallados")

# Mostrar información del dataset actual si existe
if "dataset_id" in st.session_state:
    st.divider()
    st.success(f"📊 Dataset activo: **{st.session_state.get('filename', 'Sin nombre')}**")
    st.caption(f"ID: `{st.session_state['dataset_id']}`")
    
    if st.button("🗑️ Limpiar y cargar nuevo archivo"):
        # Limpiar session_state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p><strong>EDA Dashboard v1.0</strong></p>
    <p>FastAPI + Streamlit + Pandas</p>
    <p>Desarrollado para análisis exploratorio de datos automatizado</p>
</div>
""", unsafe_allow_html=True)
