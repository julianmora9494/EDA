"""
Página de Descargas: Exportar perfiles y datos.
"""
import streamlit as st
import requests
import json
import os
from datetime import datetime

st.set_page_config(page_title="Descargas - EDA Dashboard", page_icon="📥", layout="wide")

st.title("📥 Exportar Resultados")

# URL de la API
API_URL = os.getenv("API_URL", "https://eda-dashboard-api.onrender.com")
try:
    if "API_URL" in st.secrets:
        API_URL = st.secrets["API_URL"]
except:
    pass

# Verificar que hay datos cargados
if "dataset_id" not in st.session_state:
    st.warning("⚠️ No hay ningún dataset cargado.")
    st.info("👈 Ve a la página principal para cargar un archivo.")
    st.stop()

dataset_id = st.session_state["dataset_id"]
filename = st.session_state.get("filename", "dataset")

st.success(f"📊 Dataset activo: **{filename}**")

st.divider()

# Sección 1: Exportar perfil JSON
st.subheader("📄 Perfil Completo (JSON)")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Contenido:**
    - Resumen estadístico completo
    - Análisis de calidad
    - Información de columnas
    - Insights detectados
    
    **Formato:** JSON
    """)

with col2:
    if st.button("⬇️ Descargar Perfil JSON", use_container_width=True, key="export_json"):
        try:
            response = requests.get(f"{API_URL}/datasets/{dataset_id}/profile")
            
            if response.status_code == 200:
                profile_data = response.json()
                
                st.download_button(
                    label="💾 Guardar perfil.json",
                    data=json.dumps(profile_data, indent=2, ensure_ascii=False),
                    file_name=f"perfil_{dataset_id[:8]}.json",
                    mime="application/json",
                    use_container_width=True,
                    key="download_json"
                )
                
                st.success("✅ Perfil JSON listo para descargar")
            else:
                st.error(f"Error al obtener perfil: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

st.divider()

# Sección 2: Exportar HTML
st.subheader("🌐 Reporte HTML")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Contenido:**
    - Resumen ejecutivo
    - Análisis de calidad
    - Diccionario de datos
    - Visualizaciones estáticas
    
    **Formato:** HTML5
    """)

with col2:
    if st.button("⬇️ Descargar Reporte HTML", use_container_width=True, key="export_html"):
        try:
            response = requests.get(f"{API_URL}/datasets/{dataset_id}/profile")
            
            if response.status_code == 200:
                profile = response.json()
                
                # Generar HTML simple
                overview = profile.get("overview", {})
                n_rows = overview.get("n_rows", 0)
                n_columns = overview.get("n_columns", 0)
                
                html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte EDA - {filename}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }}
        h1 {{ color: #667eea; }}
        .metric {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin: 10px 0;
        }}
        .metric-value {{
            font-size: 2rem;
            font-weight: bold;
            color: #333;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Reporte de Análisis</h1>
        <p>Dataset: {filename}</p>
        <p>Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")}</p>
    </div>
    
    <div class="metric">
        <h2>Resumen</h2>
        <p>Total de filas: <span class="metric-value">{n_rows:,}</span></p>
        <p>Total de columnas: <span class="metric-value">{n_columns:,}</span></p>
    </div>
    
    <div class="metric">
        <h2>Información Completa</h2>
        <pre>{json.dumps(profile, indent=2, ensure_ascii=False)}</pre>
    </div>
</body>
</html>"""
                
                st.download_button(
                    label="💾 Guardar reporte.html",
                    data=html_content,
                    file_name=f"reporte_{dataset_id[:8]}.html",
                    mime="text/html",
                    use_container_width=True,
                    key="download_html"
                )
                
                st.success("✅ Reporte HTML listo para descargar")
            else:
                st.error("No se pudo generar el reporte")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

st.divider()

# Sección 3: Datos procesados
st.subheader("💾 Datos Procesados")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Contenido:**
    - Dataset completo procesado
    - Todos los registros
    - Todas las columnas
    
    **Formato:** CSV
    """)

with col2:
    if st.button("⬇️ Descargar Datos CSV", use_container_width=True, key="export_csv"):
        try:
            response = requests.get(f"{API_URL}/datasets/{dataset_id}/data")
            
            if response.status_code == 200:
                data = response.json()
                
                # Convertir a CSV simple
                import io
                output = io.StringIO()
                
                if "data" in data and len(data["data"]) > 0:
                    # Escribir headers
                    headers = list(data["data"][0].keys())
                    output.write(",".join(headers) + "\n")
                    
                    # Escribir filas
                    for row in data["data"]:
                        values = [str(row.get(h, "")) for h in headers]
                        output.write(",".join(values) + "\n")
                    
                    csv_data = output.getvalue()
                    
                    st.download_button(
                        label="💾 Guardar datos.csv",
                        data=csv_data,
                        file_name=f"datos_{dataset_id[:8]}.csv",
                        mime="text/csv",
                        use_container_width=True,
                        key="download_csv"
                    )
                    
                    st.success("✅ Datos CSV listos para descargar")
                else:
                    st.warning("No hay datos disponibles")
            else:
                st.error("No se pudieron obtener los datos")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

st.divider()
st.caption("EDA Dashboard - Exportación de Resultados")
