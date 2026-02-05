"""
Componentes de tablas reutilizables.
"""
import streamlit as st
import pandas as pd
from typing import List, Dict, Any


def display_dataframe_preview(preview_data: Dict[str, List[Dict]]):
    """
    Muestra preview de head y tail del dataset.
    
    Args:
        preview_data: Dict con {head: [...], tail: [...]}
    """
    st.subheader("👀 Vista Previa de Datos")
    
    tab1, tab2 = st.tabs(["📄 Primeras filas", "📄 Últimas filas"])
    
    with tab1:
        df_head = pd.DataFrame(preview_data.get("head", []))
        if not df_head.empty:
            st.dataframe(df_head, use_container_width=True)
        else:
            st.info("No hay datos disponibles")
    
    with tab2:
        df_tail = pd.DataFrame(preview_data.get("tail", []))
        if not df_tail.empty:
            st.dataframe(df_tail, use_container_width=True)
        else:
            st.info("No hay datos disponibles")


def display_columns_table(columns: List[Dict[str, Any]]):
    """
    Tabla interactiva de columnas con metadata.
    
    Args:
        columns: Lista de dicts con metadata de columnas
    """
    if not columns:
        st.info("No hay columnas para mostrar")
        return
    
    # Crear DataFrame
    df = pd.DataFrame(columns)
    
    # Seleccionar columnas relevantes
    display_cols = ["name", "role", "dtype", "n_missing", "pct_missing", "n_unique", "relevance_score"]
    display_cols = [c for c in display_cols if c in df.columns]
    
    df_display = df[display_cols].copy()
    
    # Renombrar para mejor UX
    rename_map = {
        "name": "Columna",
        "role": "Tipo",
        "dtype": "Dtype",
        "n_missing": "# Missing",
        "pct_missing": "% Missing",
        "n_unique": "# Únicos",
        "relevance_score": "Score",
    }
    df_display = df_display.rename(columns=rename_map)
    
    # Formatear
    if "% Missing" in df_display.columns:
        df_display["% Missing"] = df_display["% Missing"].apply(lambda x: f"{x:.1f}%")
    if "Score" in df_display.columns:
        df_display["Score"] = df_display["Score"].apply(lambda x: f"{x:.1f}")
    
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        height=min(600, len(df_display) * 35 + 38)
    )


def display_insights_table(insights: List[Dict[str, Any]]):
    """
    Tabla de hallazgos/insights con formato.
    
    Args:
        insights: Lista de insights
    """
    if not insights:
        st.success("✓ No se detectaron problemas de calidad significativos")
        return
    
    st.subheader("💡 Hallazgos Automáticos")
    
    for idx, insight in enumerate(insights, 1):
        severity = insight.get("severity", "low")
        category = insight.get("category", "general")
        title = insight.get("title", "")
        description = insight.get("description", "")
        
        # Iconos por severidad
        icon_map = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        icon = icon_map.get(severity, "🔵")
        
        with st.expander(f"{icon} {title}", expanded=(severity == "high")):
            st.write(description)
            st.caption(f"Categoría: {category} | Severidad: {severity}")
