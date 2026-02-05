"""
Configuración centralizada para el Dashboard.
"""
import os
import streamlit as st


def get_api_url():
    """
    Obtener URL de la API desde múltiples fuentes.
    Prioridad: Streamlit Secrets > Variable de entorno > Localhost
    """
    try:
        # Intentar leer desde secrets de Streamlit Cloud
        return st.secrets["API_URL"]
    except (KeyError, FileNotFoundError, AttributeError):
        # Fallback a variable de entorno o localhost
        return os.getenv("API_URL", "http://localhost:8000")


# Exportar para uso directo
API_URL = get_api_url()
