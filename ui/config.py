"""
Configuración centralizada para el Dashboard.
"""
import os


def get_api_url():
    """
    Obtener URL de la API.
    En producción usa Render, en local usa localhost.
    """
    # 1. Variable de entorno (más prioritaria)
    api_url = os.getenv("API_URL")
    if api_url:
        return api_url
    
    # 2. Secrets de Streamlit Cloud
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and "API_URL" in st.secrets:
            return st.secrets["API_URL"]
    except:
        pass
    
    # 3. Detectar si estamos en producción
    # Si no hay localhost en la URL, asumir producción
    try:
        # Streamlit Cloud siempre setea esta variable
        if os.getenv("STREAMLIT_SHARING_MODE") or os.getenv("STREAMLIT_SERVER_PORT"):
            return "https://eda-dashboard-api.onrender.com"
    except:
        pass
    
    # 4. Desarrollo local
    return "http://localhost:8000"


# URL global
API_URL = get_api_url()
