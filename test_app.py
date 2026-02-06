"""
Test mínimo para identificar el error en Streamlit Cloud
"""
import streamlit as st

st.set_page_config(page_title="Test", page_icon="🧪")

st.title("🧪 Test de Streamlit Cloud")

st.write("Si ves esto, Streamlit funciona básicamente.")

# Test 1: Imports
try:
    import pandas as pd
    import numpy as np
    import plotly.express as px
    st.success("✅ Imports básicos OK")
except Exception as e:
    st.error(f"❌ Error en imports: {e}")

# Test 2: Secrets
try:
    if "API_URL" in st.secrets:
        st.success(f"✅ Secrets OK: {st.secrets['API_URL']}")
    else:
        st.warning("⚠️ No hay API_URL en secrets")
except Exception as e:
    st.error(f"❌ Error en secrets: {e}")

# Test 3: Requests
try:
    import requests
    response = requests.get("https://eda-dashboard-api.onrender.com/health", timeout=10)
    st.success(f"✅ Backend responde: {response.json()}")
except Exception as e:
    st.warning(f"⚠️ Backend no responde (puede estar dormido): {e}")

st.write("---")
st.write("Si llegaste hasta aquí, el problema está en ui/app.py específicamente.")
