"""
Componentes de métricas reutilizables para Streamlit.
"""
import streamlit as st
from typing import Dict, Any


def display_kpi_row(metrics: Dict[str, Any], columns: int = 4):
    """
    Muestra una fila de KPIs.
    
    Args:
        metrics: Dict con {label: value, ...}
        columns: Número de columnas
    """
    cols = st.columns(columns)
    for idx, (label, value) in enumerate(metrics.items()):
        with cols[idx % columns]:
            st.metric(label=label, value=value)


def display_overview_card(overview: Dict[str, Any]):
    """
    Muestra tarjeta de overview del dataset.
    
    Args:
        overview: Diccionario con overview del perfil
    """
    st.subheader("📊 Overview del Dataset")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Filas", f"{overview.get('n_rows', 0):,}")
    with col2:
        st.metric("Columnas", f"{overview.get('n_columns', 0):,}")
    with col3:
        st.metric("Memoria", f"{overview.get('memory_mb', 0):.2f} MB")
    with col4:
        dup_pct = overview.get('pct_duplicate_rows', 0)
        st.metric("Duplicados", f"{dup_pct:.1f}%")


def display_column_roles_summary(column_roles: Dict[str, str]):
    """
    Muestra resumen de roles de columnas.
    
    Args:
        column_roles: Dict {column_name: role}
    """
    st.subheader("🏷️ Distribución de Tipos de Variables")
    
    # Contar por rol
    role_counts = {}
    for role in column_roles.values():
        role_counts[role] = role_counts.get(role, 0) + 1
    
    # Mostrar en columnas
    role_labels = {
        "numeric": "🔢 Numéricas",
        "categorical_low_card": "📑 Categóricas (baja card.)",
        "categorical_high_card": "📑 Categóricas (alta card.)",
        "datetime": "📅 Fechas",
        "boolean": "✓ Booleanas",
        "text": "📝 Texto",
        "id_like": "🔑 IDs",
        "constant": "⚪ Constantes",
        "all_missing": "❌ Todo missing",
    }
    
    cols = st.columns(3)
    idx = 0
    for role, count in sorted(role_counts.items(), key=lambda x: x[1], reverse=True):
        with cols[idx % 3]:
            label = role_labels.get(role, role)
            st.metric(label, count)
        idx += 1
