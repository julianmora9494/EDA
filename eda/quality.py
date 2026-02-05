"""
Data quality checks: missing, duplicados, valores inválidos, hallazgos automáticos.
"""
import pandas as pd
import numpy as np
from typing import Dict, List


def check_data_quality(df: pd.DataFrame) -> Dict:
    """
    Ejecuta checks de calidad sobre el dataset.
    
    Args:
        df: DataFrame a analizar
        
    Returns:
        Diccionario con resultados de quality checks
    """
    return {
        "missing": _check_missing(df),
        "duplicates": _check_duplicates(df),
        "constants": _check_constants(df),
        "high_missing_cols": _check_high_missing_columns(df),
    }


def _check_missing(df: pd.DataFrame) -> Dict:
    """Analiza valores faltantes."""
    n_total_cells = df.shape[0] * df.shape[1]
    n_missing_cells = df.isna().sum().sum()
    pct_missing_global = (n_missing_cells / n_total_cells) * 100 if n_total_cells > 0 else 0
    
    missing_by_col = []
    for col in df.columns:
        n_missing = df[col].isna().sum()
        if n_missing > 0:
            missing_by_col.append({
                "column": col,
                "n_missing": int(n_missing),
                "pct_missing": round((n_missing / len(df)) * 100, 2)
            })
    
    missing_by_col = sorted(missing_by_col, key=lambda x: x['n_missing'], reverse=True)
    
    return {
        "n_total_cells": n_total_cells,
        "n_missing_cells": int(n_missing_cells),
        "pct_missing_global": round(pct_missing_global, 2),
        "columns_with_missing": len(missing_by_col),
        "missing_by_column": missing_by_col[:20],  # Top 20
    }


def _check_duplicates(df: pd.DataFrame) -> Dict:
    """Analiza filas duplicadas."""
    n_duplicates = df.duplicated().sum()
    pct_duplicates = (n_duplicates / len(df)) * 100 if len(df) > 0 else 0
    
    return {
        "n_total_rows": len(df),
        "n_duplicate_rows": int(n_duplicates),
        "pct_duplicate_rows": round(pct_duplicates, 2),
        "n_unique_rows": len(df) - n_duplicates,
    }


def _check_constants(df: pd.DataFrame) -> Dict:
    """Detecta columnas constantes o casi constantes."""
    constant_cols = []
    
    for col in df.columns:
        n_unique = df[col].nunique()
        if n_unique == 1:
            constant_cols.append({
                "column": col,
                "type": "constant",
                "n_unique": 1,
                "value": str(df[col].iloc[0]) if len(df) > 0 else None,
            })
        elif n_unique == 2:
            top_freq = df[col].value_counts().iloc[0]
            pct_top = (top_freq / len(df)) * 100
            if pct_top > 99:  # Casi constante
                constant_cols.append({
                    "column": col,
                    "type": "near_constant",
                    "n_unique": 2,
                    "dominant_pct": round(pct_top, 2),
                })
    
    return {
        "n_constant_columns": len([c for c in constant_cols if c['type'] == 'constant']),
        "n_near_constant_columns": len([c for c in constant_cols if c['type'] == 'near_constant']),
        "constant_columns": constant_cols,
    }


def _check_high_missing_columns(df: pd.DataFrame, threshold: float = 50.0) -> List[str]:
    """
    Detecta columnas con missing extremo (>threshold%).
    
    Args:
        df: DataFrame
        threshold: Umbral de % missing
        
    Returns:
        Lista de nombres de columnas
    """
    high_missing = []
    for col in df.columns:
        pct_missing = (df[col].isna().sum() / len(df)) * 100
        if pct_missing > threshold:
            high_missing.append(col)
    return high_missing


def generate_insights(df: pd.DataFrame, quality_report: Dict, column_metadata: List[Dict]) -> List[Dict]:
    """
    Genera hallazgos automáticos basados en quality checks.
    
    Args:
        df: DataFrame
        quality_report: Resultado de check_data_quality
        column_metadata: Metadata de columnas del profiler
        
    Returns:
        Lista de insights (hallazgos)
    """
    insights = []
    
    # 1. Columnas con missing extremo
    high_missing = quality_report.get("high_missing_cols", [])
    if high_missing:
        insights.append({
            "type": "warning",
            "category": "missing_data",
            "title": f"{len(high_missing)} columnas con >50% missing",
            "description": f"Columnas: {', '.join(high_missing[:5])}{'...' if len(high_missing) > 5 else ''}",
            "severity": "high" if len(high_missing) > 5 else "medium",
        })
    
    # 2. Duplicados
    pct_dup = quality_report.get("duplicates", {}).get("pct_duplicate_rows", 0)
    if pct_dup > 5:
        insights.append({
            "type": "warning",
            "category": "duplicates",
            "title": f"{pct_dup:.1f}% de filas duplicadas",
            "description": "Considere eliminar o investigar duplicados",
            "severity": "high" if pct_dup > 20 else "medium",
        })
    
    # 3. Columnas constantes
    n_const = quality_report.get("constants", {}).get("n_constant_columns", 0)
    if n_const > 0:
        insights.append({
            "type": "info",
            "category": "constants",
            "title": f"{n_const} columnas constantes detectadas",
            "description": "Estas columnas no aportan información y pueden eliminarse",
            "severity": "low",
        })
    
    # 4. Columnas ID-like
    id_cols = [col["name"] for col in column_metadata if col.get("role") == "id_like"]
    if id_cols:
        insights.append({
            "type": "info",
            "category": "ids",
            "title": f"{len(id_cols)} columnas identificadas como IDs",
            "description": f"Columnas: {', '.join(id_cols[:5])}. No se graficarán como categóricas.",
            "severity": "low",
        })
    
    # 5. Missing global alto
    pct_missing_global = quality_report.get("missing", {}).get("pct_missing_global", 0)
    if pct_missing_global > 20:
        insights.append({
            "type": "warning",
            "category": "missing_data",
            "title": f"{pct_missing_global:.1f}% de datos faltantes en total",
            "description": "El dataset tiene una proporción significativa de missing values",
            "severity": "high" if pct_missing_global > 40 else "medium",
        })
    
    # 6. Variables numéricas (conteo)
    numeric_cols = [col for col in column_metadata if col.get("role") == "numeric"]
    if numeric_cols:
        insights.append({
            "type": "info",
            "category": "data_types",
            "title": f"{len(numeric_cols)} variables numéricas detectadas",
            "description": f"Disponibles para análisis cuantitativo y correlaciones",
            "severity": "low",
        })
    
    # 7. Variables categóricas
    cat_cols = [col for col in column_metadata if col.get("role") in ["categorical_low_card", "categorical_high_card"]]
    if cat_cols:
        insights.append({
            "type": "info",
            "category": "data_types",
            "title": f"{len(cat_cols)} variables categóricas detectadas",
            "description": f"Disponibles para segmentación y análisis de grupos",
            "severity": "low",
        })
    
    # 8. Variables con alta cardinalidad
    high_card_cols = [col for col in column_metadata if col.get("role") == "categorical_high_card"]
    if len(high_card_cols) > 0:
        insights.append({
            "type": "warning",
            "category": "cardinality",
            "title": f"{len(high_card_cols)} variables con alta cardinalidad",
            "description": f"Columnas: {', '.join([c['name'] for c in high_card_cols[:3]])}. Considere agrupar categorías.",
            "severity": "medium",
        })
    
    # 9. Fechas detectadas
    date_cols = [col for col in column_metadata if col.get("role") == "datetime"]
    if date_cols:
        insights.append({
            "type": "info",
            "category": "temporal",
            "title": f"{len(date_cols)} variables temporales detectadas",
            "description": f"Columnas: {', '.join([c['name'] for c in date_cols])}. Disponibles para análisis de series temporales.",
            "severity": "low",
        })
    
    # 10. Texto largo detectado
    text_cols = [col for col in column_metadata if col.get("role") == "text"]
    if text_cols:
        insights.append({
            "type": "info",
            "category": "text",
            "title": f"{len(text_cols)} columnas de texto largo detectadas",
            "description": f"Columnas: {', '.join([c['name'] for c in text_cols])}. Considere análisis de texto (NLP).",
            "severity": "low",
        })
    
    return insights
