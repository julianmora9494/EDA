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

# URL de la API
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

# Verificar conexión con API
with st.spinner("Verificando conexión con el servidor..."):
    try:
        response = requests.get(f"{API_URL}/", timeout=5)
        if response.status_code == 200:
            st.success("✅ Conectado al servidor correctamente")
        else:
            st.warning(f"⚠️ Servidor respondió con código: {response.status_code}")
    except Exception as e:
        st.error(f"❌ No se puede conectar con el servidor en {API_URL}")
        st.info("💡 Asegúrate de que el backend esté corriendo: `python -m uvicorn api.main:app --reload --port 8000`")
        st.stop()

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

# Sección de carga de archivos
st.subheader("📁 Cargar Archivo de Datos")

uploaded_file = st.file_uploader(
    "Selecciona un archivo CSV, Excel o Parquet",
    type=["csv", "xlsx", "xls", "parquet"],
    help="Formatos soportados: CSV, Excel (.xlsx, .xls), Parquet"
)

if uploaded_file is not None:
    # Mostrar información del archivo
    file_details = {
        "Nombre": uploaded_file.name,
        "Tamaño": f"{uploaded_file.size:,} bytes",
        "Tipo": uploaded_file.type
    }
    
    st.success("✅ Archivo cargado correctamente")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.json(file_details)
    
    with col2:
        if st.button("🚀 Analizar Datos", type="primary", use_container_width=True):
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
