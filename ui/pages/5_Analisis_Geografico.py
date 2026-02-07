"""
Análisis Geográfico: Distribución de clientes y saldos por país
Con mapa interactivo tipo choropleth
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

st.set_page_config(page_title="Análisis Geográfico", page_icon="🌎", layout="wide")

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

if "profile" not in st.session_state or st.session_state.profile is None:
    st.warning("⚠️ No hay dataset cargado.")
    st.stop()

profile = st.session_state.profile
dataset_id = st.session_state.dataset_id

st.title("🌎 Análisis Geográfico")
st.caption("Distribución de clientes, activos y pasivos por país")

# Obtener columnas
all_columns = [col['name'] for col in profile['columns']]

pais_col = next((col for col in all_columns if 'país' in col.lower()), None)
activos_col = next((col for col in all_columns if 'activo' in col.lower() and 'saldo' in col.lower()), None)
pasivos_col = next((col for col in all_columns if 'pasivo' in col.lower() and 'saldo' in col.lower()), None)

if not pais_col:
    st.error("❌ No se encontró columna de País")
    st.stop()

# Obtener datos
@st.cache_data
def get_data(dataset_id, columns_list):
    try:
        cols_str = ",".join(columns_list)
        response = requests.get(
            f"{API_URL}/datasets/{dataset_id}/data/columns",
            params={"columns": cols_str}
        )
        if response.status_code == 200:
            return pd.DataFrame(response.json()['data'])
        return None
    except:
        return None

columns_to_fetch = [pais_col]
if activos_col:
    columns_to_fetch.append(activos_col)
if pasivos_col:
    columns_to_fetch.append(pasivos_col)

df = get_data(dataset_id, columns_to_fetch)

if df is None or df.empty:
    st.error("❌ Error al cargar datos")
    st.stop()

# Limpiar datos
df = df.replace([None], np.nan)
if activos_col:
    df[activos_col] = pd.to_numeric(df[activos_col], errors='coerce')
if pasivos_col:
    df[pasivos_col] = pd.to_numeric(df[pasivos_col], errors='coerce')

# Mapeo de países a códigos ISO
country_iso_map = {
    'panama': 'PAN', 'panamá': 'PAN',
    'honduras': 'HND',
    'guatemala': 'GTM',
    'el salvador': 'SLV',
    'nicaragua': 'NIC',
    'costa rica': 'CRI',
    'belize': 'BLZ', 'belice': 'BLZ',
    'mexico': 'MEX', 'méxico': 'MEX',
    'colombia': 'COL',
    'venezuela': 'VEN',
    'ecuador': 'ECU',
    'peru': 'PER', 'perú': 'PER',
    'chile': 'CHL',
    'argentina': 'ARG',
    'brasil': 'BRA', 'brazil': 'BRA',
    'united states': 'USA', 'estados unidos': 'USA', 'usa': 'USA', 'us': 'USA',
    'spain': 'ESP', 'españa': 'ESP',
    'united kingdom': 'GBR', 'reino unido': 'GBR', 'uk': 'GBR',
    'canada': 'CAN', 'canadá': 'CAN',
    'france': 'FRA', 'francia': 'FRA',
    'germany': 'DEU', 'alemania': 'DEU',
    'italy': 'ITA', 'italia': 'ITA',
    'netherlands': 'NLD', 'países bajos': 'NLD', 'holanda': 'NLD',
    'switzerland': 'CHE', 'suiza': 'CHE',
    'china': 'CHN',
    'japan': 'JPN', 'japón': 'JPN',
    'south korea': 'KOR', 'corea del sur': 'KOR'
}

# Agregar código ISO
df['iso_alpha'] = df[pais_col].astype(str).str.lower().str.strip().map(country_iso_map)

# Agregar por país
agg_dict = {}
if activos_col:
    agg_dict[activos_col] = 'sum'
if pasivos_col:
    agg_dict[pasivos_col] = 'sum'

# Si no hay columnas para agregar, solo contar
if not agg_dict:
    df_pais = df.groupby(pais_col).size().reset_index(name='N_Clientes')
else:
    df_pais = df.groupby(pais_col).agg(agg_dict).reset_index()
    # Agregar conteo de clientes
    df_pais['N_Clientes'] = df.groupby(pais_col).size().values

# Calcular balance neto si hay ambos
if activos_col and pasivos_col:
    df_pais['Balance_Neto'] = df_pais[activos_col] - df_pais[pasivos_col]
    df_pais['Total_Balance'] = df_pais[activos_col] + df_pais[pasivos_col]

# Agregar ISO
df_pais['iso_alpha'] = df_pais[pais_col].astype(str).str.lower().str.strip().map(country_iso_map)

# Filtrar países con ISO
df_pais_map = df_pais.dropna(subset=['iso_alpha'])

# ==================== MAPA INTERACTIVO ====================
st.header("🗺️ Mapa Interactivo")

if not df_pais_map.empty and pasivos_col:
    
    # Selector de métrica
    metrica_options = {
        'N° Clientes': 'N_Clientes',
        'Suma ACTIVOS': activos_col if activos_col else None,
        'Suma PASIVOS': pasivos_col if pasivos_col else None,
        'Total Balance': 'Total_Balance' if activos_col and pasivos_col else None,
        'Balance Neto': 'Balance_Neto' if activos_col and pasivos_col else None
    }
    
    # Filtrar opciones válidas
    metrica_options = {k: v for k, v in metrica_options.items() if v is not None}
    
    metrica_seleccionada = st.selectbox(
        "Selecciona la métrica para visualizar en el mapa:",
        list(metrica_options.keys())
    )
    
    col_metrica = metrica_options[metrica_seleccionada]
    
    # Mapa choropleth
    hover_data_dict = {
        "N_Clientes": True,
        "iso_alpha": False
    }
    if activos_col in df_pais_map.columns:
        hover_data_dict[activos_col] = ':$,.0f'
    if pasivos_col in df_pais_map.columns:
        hover_data_dict[pasivos_col] = ':$,.0f'
    
    fig = px.choropleth(
        df_pais_map,
        locations="iso_alpha",
        color=col_metrica,
        hover_name=pais_col,
        hover_data=hover_data_dict,
        color_continuous_scale='Reds',
        title=f'Distribución Geográfica: {metrica_seleccionada}',
        projection="natural earth"
    )
    
    fig.update_geos(
        showcountries=True,
        countrycolor="lightgray",
        showcoastlines=True,
        coastlinecolor="gray",
        showland=True,
        landcolor="white",
        showocean=True,
        oceancolor="lightblue",
        center={"lat": 10, "lon": -85},  # Centrado en Centroamérica
        projection_scale=2.5
    )
    
    fig.update_layout(
        height=600,
        margin={"r":0,"t":50,"l":0,"b":0}
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.caption("""
    **💡 Cómo usar el mapa**:
    - **Hover** sobre un país para ver detalles
    - Los colores más intensos representan valores más altos
    - Cambia la métrica arriba para ver diferentes perspectivas
    """)

else:
    st.info("No hay suficientes datos para mostrar el mapa interactivo.")

st.divider()

# ==================== TABLA DETALLADA ====================
st.header("📊 Análisis Detallado por País")

# Preparar tabla
if activos_col and pasivos_col and 'Total_Balance' in df_pais.columns:
    df_pais_sorted = df_pais.sort_values('Total_Balance', ascending=False)
    
    columns_to_show = [pais_col, 'N_Clientes', activos_col, pasivos_col, 'Balance_Neto', 'Total_Balance']
    
    st.dataframe(
        df_pais_sorted[columns_to_show].style.format({
            'N_Clientes': '{:,}',
            activos_col: '${:,.0f}',
            pasivos_col: '${:,.0f}',
            'Balance_Neto': '${:,.0f}',
            'Total_Balance': '${:,.0f}'
        }).background_gradient(subset=['Total_Balance'], cmap='Reds'),
        use_container_width=True,
        hide_index=True
    )
else:
    st.dataframe(
        df_pais.sort_values('N_Clientes', ascending=False),
        use_container_width=True,
        hide_index=True
    )

st.divider()

# ==================== GRÁFICO DE BARRAS ====================
st.header("📈 Top 15 Países")

if activos_col and pasivos_col and 'Total_Balance' in df_pais.columns:
    df_top = df_pais.sort_values('Total_Balance', ascending=False).head(15)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=df_top[pais_col],
        x=df_top[activos_col],
        name='ACTIVOS',
        orientation='h',
        marker=dict(color='#2ecc71')
    ))
    
    fig.add_trace(go.Bar(
        y=df_top[pais_col],
        x=df_top[pasivos_col],
        name='PASIVOS',
        orientation='h',
        marker=dict(color='#3498db')
    ))
    
    fig.update_layout(
        title='Top 15 Países: ACTIVOS vs PASIVOS',
        xaxis_title='Monto ($)',
        yaxis_title='País',
        barmode='group',
        height=600
    )
    
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.caption("🌎 Análisis geográfico con mapa interactivo y desglose por país")
