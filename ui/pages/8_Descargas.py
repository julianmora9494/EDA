"""
Página de Descargas: Exportar perfiles y datos.
"""
import streamlit as st
import requests
import json
import sys
from pathlib import Path

# Importar utilidades del frontend
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import generate_simple_html_report

st.set_page_config(page_title="Descargas - EDA Dashboard", page_icon="📥", layout="wide")

st.title("📥 Exportar Resultados")

# URL de la API
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

# Verificar que hay datos cargados
if "profile" not in st.session_state or st.session_state.profile is None:
    st.warning("⚠️ No hay dataset cargado. Ve a la página principal para subir un archivo.")
    st.stop()

profile = st.session_state.profile
dataset_id = st.session_state.dataset_id

st.markdown("""
Descarga los resultados del análisis EDA en diferentes formatos para:
- 📊 Reportes y documentación
- 🔄 Compartir con el equipo
- 💾 Archivar análisis
- 🔧 Procesamiento posterior
""")

st.divider()

# Sección 1: Perfil EDA
st.subheader("📊 Perfil EDA Completo")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    **Contenido del perfil:**
    - Overview del dataset
    - Metadata de todas las columnas
    - Tipos inferidos y roles
    - Quality checks (missing, duplicados, constantes)
    - Asociaciones y correlaciones
    - Hallazgos automáticos
    - Vista previa de datos
    
    **Formato:** JSON
    """)

with col2:
    if st.button("⬇️ Descargar Perfil JSON", use_container_width=True):
        try:
            # El perfil ya está en session_state, podemos descargarlo directamente
            json_str = json.dumps(profile, indent=2, ensure_ascii=False)
            
            st.download_button(
                label="💾 Guardar perfil.json",
                data=json_str,
                file_name=f"perfil_eda_{dataset_id[:8]}.json",
                mime="application/json",
                use_container_width=True
            )
            
            st.success("✅ Perfil listo para descargar")
        except Exception as e:
            st.error(f"Error al preparar descarga: {str(e)}")

st.divider()

# Sección 2: Exportar a HTML
st.subheader("🌐 Reporte HTML Interactivo")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    **Archivo HTML independiente:**
    - 📄 Documento completo y profesional
    - 🎨 Estilos modernos incluidos
    - 📊 Toda la información en un archivo
    - 🌐 Abre en cualquier navegador
    - 🖨️ Listo para imprimir
    - 👥 Perfecto para compartir con otros
    
    **Contenido:**
    - Resumen ejecutivo con métricas
    - Análisis de calidad de datos
    - Diccionario de datos completo
    - Hallazgos y recomendaciones
    - Información técnica
    
    **Formato:** HTML5
    """)

with col2:
    if st.button("⬇️ Descargar Reporte HTML", use_container_width=True, key="export_html"):
        try:
            # Obtener datos completos del dataset
            data_response = requests.get(f"{API_URL}/datasets/{dataset_id}/data")
            
            if data_response.status_code == 200:
                dataset_data = data_response.json()
                
                # Generar HTML con datos completos
                html_content = generate_simple_html_report(profile, dataset_id[:16])
                
                st.download_button(
                    label="💾 Guardar reporte.html",
                    data=html_content,
                    file_name=f"reporte_completo_{dataset_id[:8]}.html",
                    mime="text/html",
                    use_container_width=True,
                    key="download_html"
                )
                
                st.success("✅ Reporte HTML completo listo para descargar")
                st.info("📊 Incluye: Resumen, Calidad, Productos, Patrimonio, Geográfico, Insights y más")
            else:
                st.error("No se pudieron obtener los datos para generar el reporte completo")
        except Exception as e:
            st.error(f"❌ Error al generar reporte HTML: {str(e)}")

st.divider()

# Sección 3: Datos procesados
st.subheader("💾 Datos Procesados")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Formato CSV**
    - Compatible con Excel, R, Python, etc.
    - Fácil de leer y editar
    - Texto plano
    """)
    
    if st.button("⬇️ Descargar CSV", use_container_width=True):
        try:
            response = requests.get(f"{API_URL}/datasets/{dataset_id}/export/data?format=csv")
            
            if response.status_code == 200:
                st.download_button(
                    label="💾 Guardar datos.csv",
                    data=response.content,
                    file_name=f"datos_{dataset_id[:8]}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                st.success("✅ CSV listo para descargar")
            else:
                st.error(f"Error al exportar: {response.text}")
        except Exception as e:
            st.error(f"Error: {str(e)}")

with col2:
    st.markdown("""
    **Formato Parquet**
    - Comprimido y eficiente
    - Tipos de datos preservados
    - Ideal para procesamiento
    """)
    
    if st.button("⬇️ Descargar Parquet", use_container_width=True):
        try:
            response = requests.get(f"{API_URL}/datasets/{dataset_id}/export/data?format=parquet")
            
            if response.status_code == 200:
                st.download_button(
                    label="💾 Guardar datos.parquet",
                    data=response.content,
                    file_name=f"datos_{dataset_id[:8]}.parquet",
                    mime="application/octet-stream",
                    use_container_width=True
                )
                st.success("✅ Parquet listo para descargar")
            else:
                st.error(f"Error al exportar: {response.text}")
        except Exception as e:
            st.error(f"Error: {str(e)}")

st.divider()

# Sección 4: Resumen ejecutivo
st.subheader("📄 Resumen Ejecutivo")

st.markdown("Copia el resumen en markdown para documentación:")

overview = profile["overview"]
quality = profile["quality"]
insights = profile.get("insights", [])

markdown_summary = f"""
# Resumen EDA - Dataset {dataset_id[:16]}

## 📊 Overview

- **Filas:** {overview['n_rows']:,}
- **Columnas:** {overview['n_columns']}
- **Memoria:** {overview['memory_mb']:.2f} MB
- **Duplicados:** {overview['pct_duplicate_rows']:.1f}%

## 🔍 Calidad de Datos

- **Missing global:** {quality['missing']['pct_missing_global']:.1f}%
- **Columnas con missing:** {quality['missing']['columns_with_missing']}
- **Columnas constantes:** {quality['constants']['n_constant_columns']}

## 🏷️ Tipos de Variables

{chr(10).join([f"- **{role}:** {count}" for role, count in sorted([(r, list(profile['column_roles'].values()).count(r)) for r in set(profile['column_roles'].values())], key=lambda x: x[1], reverse=True)])}

## 💡 Hallazgos ({len(insights)})

{chr(10).join([f"- **[{i.get('severity', 'low').upper()}]** {i.get('title', '')}" for i in insights[:10]])}

## 📈 Top Variables (por relevancia)

{chr(10).join([f"{idx}. **{col['name']}** ({col['role']}) - Score: {col.get('relevance_score', 0):.1f}" for idx, col in enumerate(sorted(profile['columns'], key=lambda x: x.get('relevance_score', 0), reverse=True)[:10], 1)])}

---

*Generado con EDA Dashboard v1.0*
*Fecha: {profile['profiled_at']}*
"""

st.text_area(
    "Markdown",
    markdown_summary,
    height=400,
    help="Copia este texto para documentación"
)

if st.button("📋 Copiar al portapapeles"):
    st.code(markdown_summary)
    st.info("Selecciona el texto de arriba y copia manualmente (Ctrl+C)")

st.divider()

# Info adicional
st.subheader("ℹ️ Información del Análisis")

col1, col2 = st.columns(2)

with col1:
    st.info(f"""
    **Dataset:**
    - ID: `{dataset_id}`
    - Hoja: `{profile['sheet_name']}`
    - Perfilado: {profile['profiled_at']}
    """)

with col2:
    st.info(f"""
    **Performance:**
    - Duración: {profile['profile_duration_seconds']:.2f}s
    - Muestreado: {'Sí' if profile['sampled'] else 'No'}
    - Cache: {'Sí' if profile.get('from_cache') else 'No'}
    """)
