"""
Componentes de gráficos reutilizables usando Plotly.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List, Any


def plot_missing_heatmap(missing_by_column: List[Dict]):
    """
    Gráfico de barras de % missing por columna.
    
    Args:
        missing_by_column: Lista de dicts con {column, n_missing, pct_missing}
    """
    if not missing_by_column:
        st.info("✓ No hay columnas con valores faltantes")
        return
    
    df = pd.DataFrame(missing_by_column).head(20)
    
    fig = px.bar(
        df,
        x="pct_missing",
        y="column",
        orientation="h",
        title="% de Valores Faltantes por Columna (Top 20)",
        labels={"pct_missing": "% Missing", "column": ""},
        color="pct_missing",
        color_continuous_scale="Reds",
    )
    fig.update_layout(height=max(400, len(df) * 25), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def plot_correlation_heatmap(corr_matrix: Dict[str, Dict[str, float]]):
    """
    Heatmap de correlación.
    
    Args:
        corr_matrix: Matriz de correlación como dict anidado
    """
    if not corr_matrix:
        st.info("No hay suficientes variables numéricas para calcular correlaciones")
        return
    
    df = pd.DataFrame(corr_matrix)
    
    fig = go.Figure(data=go.Heatmap(
        z=df.values,
        x=df.columns,
        y=df.index,
        colorscale="RdBu_r",
        zmid=0,
        text=df.values.round(2),
        texttemplate="%{text}",
        textfont={"size": 10},
        colorbar=dict(title="Correlación"),
    ))
    
    fig.update_layout(
        title="Matriz de Correlación (Pearson)",
        xaxis_title="",
        yaxis_title="",
        height=max(500, len(df) * 30),
    )
    
    st.plotly_chart(fig, use_container_width=True)


def plot_histogram(data: List[float], column_name: str, bins: int = 30):
    """
    Histograma para variable numérica.
    
    Args:
        data: Lista de valores
        column_name: Nombre de la columna
        bins: Número de bins
    """
    fig = px.histogram(
        x=data,
        nbins=bins,
        title=f"Distribución: {column_name}",
        labels={"x": column_name, "count": "Frecuencia"},
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def plot_value_counts(value_counts: List[Dict], column_name: str, max_categories: int = 20):
    """
    Gráfico de barras para variable categórica.
    
    Args:
        value_counts: Lista de dicts con {value, count, percentage}
        column_name: Nombre de la columna
        max_categories: Máximo de categorías a mostrar
    """
    df = pd.DataFrame(value_counts).head(max_categories)
    
    fig = px.bar(
        df,
        x="value",
        y="count",
        title=f"Frecuencias: {column_name} (Top {len(df)})",
        labels={"value": column_name, "count": "Frecuencia"},
        text="percentage",
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)


def plot_boxplot(data: List[float], column_name: str):
    """
    Boxplot para variable numérica.
    
    Args:
        data: Lista de valores
        column_name: Nombre de la columna
    """
    fig = go.Figure(data=[go.Box(y=data, name=column_name)])
    fig.update_layout(
        title=f"Boxplot: {column_name}",
        yaxis_title=column_name,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)
