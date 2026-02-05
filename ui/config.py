"""
Configuración centralizada para el Dashboard.
"""
import os


def get_api_url():
    """
    Obtener URL de la API desde múltiples fuentes.
    Prioridad: Variable de entorno > Streamlit Secrets > URL de producción > Localhost
    """
    # 1. Primero intentar variable de entorno
    if os.getenv("API_URL"):
        return os.getenv("API_URL")
    
    # 2. Intentar leer desde secrets de Streamlit Cloud
    try:
        import streamlit as st
        if "API_URL" in st.secrets:
            return st.secrets["API_URL"]
    except:
        pass
    
    # 3. Si estamos en producción (detectar por hostname)
    try:
        import socket
        hostname = socket.gethostname()
        if "streamlit" in hostname.lower() or "render" in hostname.lower():
            # Estamos en Streamlit Cloud, usar API de producción
            return "https://eda-dashboard-api.onrender.com"
    except:
        pass
    
    # 4. Fallback a localhost para desarrollo
    return "http://localhost:8000"


# Exportar para uso directo
API_URL = get_api_url()
