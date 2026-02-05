"""
Type inference: detecta roles de variables (numeric, categorical, datetime, text, id, constant, etc.)
"""
import re
import pandas as pd
import numpy as np
from typing import Dict, Literal


VariableRole = Literal[
    "numeric",
    "categorical_low_card",
    "categorical_high_card",
    "datetime",
    "boolean",
    "text",
    "id_like",
    "constant",
    "all_missing"
]


def infer_variable_role(series: pd.Series, n_total: int) -> VariableRole:
    """
    Infiere el rol/tipo semántico de una variable.
    
    Args:
        series: Serie de pandas
        n_total: Total de filas del dataset
        
    Returns:
        Rol inferido de la variable
    """
    # 1. All missing
    n_valid = series.notna().sum()
    if n_valid == 0:
        return "all_missing"
    
    # 2. Constant / near-constant
    n_unique = series.nunique()
    if n_unique == 1:
        return "constant"
    
    # 3. Boolean
    if n_unique == 2 and series.dtype in ['bool', 'object', 'int64']:
        unique_vals = set(series.dropna().unique())
        bool_patterns = [
            {True, False},
            {1, 0},
            {'True', 'False'},
            {'true', 'false'},
            {'YES', 'NO'},
            {'Yes', 'No'},
            {'yes', 'no'},
            {'Y', 'N'},
            {'S', 'N'},  # Sí/No
            {'1', '0'},
        ]
        for pattern in bool_patterns:
            if unique_vals.issubset(pattern):
                return "boolean"
    
    # 4. Datetime
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    
    # Intentar parsear como datetime si es string
    if series.dtype == 'object' and n_unique < n_total * 0.5:  # No tiene sentido si casi todo es único
        try:
            pd.to_datetime(series.dropna().head(100), errors='raise')
            return "datetime"
        except:
            pass
    
    # 5. Numeric
    if pd.api.types.is_numeric_dtype(series):
        # ¿Es ID-like?
        if _is_id_like(series, n_total, n_unique):
            return "id_like"
        return "numeric"
    
    # 6. String/Object types
    if series.dtype == 'object':
        # Cardinalidad
        cardinality_ratio = n_unique / n_valid
        
        # ¿Es ID-like?
        if _is_id_like(series, n_total, n_unique):
            return "id_like"
        
        # ¿Es texto largo?
        if _is_text(series):
            return "text"
        
        # Categorical
        if cardinality_ratio < 0.05 or n_unique < 50:  # Baja cardinalidad
            return "categorical_low_card"
        else:
            return "categorical_high_card"
    
    # Default
    return "categorical_high_card"


def _is_id_like(series: pd.Series, n_total: int, n_unique: int) -> bool:
    """
    Detecta si una columna parece un ID (alta cardinalidad, monótonía, patrones).
    
    Args:
        series: Serie de pandas
        n_total: Total de filas
        n_unique: Número de valores únicos
        
    Returns:
        True si parece un ID
    """
    # Alta cardinalidad (>90% único)
    cardinality_ratio = n_unique / n_total
    if cardinality_ratio < 0.9:
        return False
    
    # Monotonicidad (si es numérico)
    if pd.api.types.is_numeric_dtype(series):
        try:
            is_monotonic = series.is_monotonic_increasing or series.is_monotonic_decreasing
            if is_monotonic:
                return True
        except:
            pass
    
    # Patrones de ID en el nombre de la columna
    col_name = series.name.lower() if series.name else ""
    id_patterns = ['id', 'codigo', 'código', 'code', 'key', 'identificac', 'celular', 'telefono', 'phone', 'cedula', 'dni', 'documento']
    if any(pat in col_name for pat in id_patterns):
        return True
    
    # Longitud corta y consistente (para strings)
    if series.dtype == 'object':
        lengths = series.dropna().astype(str).str.len()
        if lengths.std() < 2 and lengths.mean() < 20:  # Longitud consistente y corta
            return True
    
    return False


def _is_text(series: pd.Series) -> bool:
    """
    Detecta si una columna es texto largo (comentarios, descripciones, etc.)
    
    Args:
        series: Serie de pandas
        
    Returns:
        True si parece texto largo
    """
    if series.dtype != 'object':
        return False
    
    # Muestra
    sample = series.dropna().head(100)
    if len(sample) == 0:
        return False
    
    # Longitud media
    lengths = sample.astype(str).str.len()
    mean_length = lengths.mean()
    
    # Si la longitud media es > 50, probablemente es texto
    if mean_length > 50:
        return True
    
    # Presencia de espacios (indicador de frases)
    has_spaces = sample.astype(str).str.contains(' ', regex=False).mean()
    if has_spaces > 0.7 and mean_length > 20:
        return True
    
    return False


def get_column_metadata(series: pd.Series, role: VariableRole) -> Dict:
    """
    Extrae metadata básica de una columna según su rol.
    
    Args:
        series: Serie de pandas
        role: Rol inferido de la variable
        
    Returns:
        Diccionario con metadata
    """
    n_total = int(len(series))
    n_valid = int(series.notna().sum())
    n_missing = int(n_total - n_valid)
    n_unique = int(series.nunique())
    
    metadata = {
        "name": str(series.name),
        "role": role,
        "dtype": str(series.dtype),
        "n_total": n_total,
        "n_valid": n_valid,
        "n_missing": n_missing,
        "pct_missing": round(float((n_missing / n_total) * 100), 2) if n_total > 0 else 0.0,
        "n_unique": n_unique,
        "cardinality_ratio": round(float(n_unique / n_valid), 4) if n_valid > 0 else 0.0,
    }
    
    # Metadata específica por rol
    if role == "numeric":
        metadata.update(_numeric_metadata(series))
    elif role in ["categorical_low_card", "categorical_high_card"]:
        metadata.update(_categorical_metadata(series))
    elif role == "text":
        metadata.update(_text_metadata(series))
    elif role == "datetime":
        metadata.update(_datetime_metadata(series))
    
    return metadata


def _numeric_metadata(series: pd.Series) -> Dict:
    """Metadata específica para numéricas."""
    desc = series.describe()
    return {
        "mean": round(float(desc['mean']), 4) if 'mean' in desc else None,
        "std": round(float(desc['std']), 4) if 'std' in desc else None,
        "min": round(float(desc['min']), 4) if 'min' in desc else None,
        "max": round(float(desc['max']), 4) if 'max' in desc else None,
        "q25": round(float(desc['25%']), 4) if '25%' in desc else None,
        "q50": round(float(desc['50%']), 4) if '50%' in desc else None,
        "q75": round(float(desc['75%']), 4) if '75%' in desc else None,
    }


def _categorical_metadata(series: pd.Series) -> Dict:
    """Metadata específica para categóricas."""
    value_counts = series.value_counts()
    top_category = value_counts.index[0] if len(value_counts) > 0 else None
    top_frequency = int(value_counts.iloc[0]) if len(value_counts) > 0 else 0
    
    return {
        "top_category": str(top_category) if top_category is not None else None,
        "top_frequency": top_frequency,
        "top_pct": round((top_frequency / len(series)) * 100, 2) if len(series) > 0 else 0,
    }


def _text_metadata(series: pd.Series) -> Dict:
    """Metadata específica para texto."""
    sample = series.dropna().head(1000)
    if len(sample) == 0:
        return {"mean_length": 0}
    
    lengths = sample.astype(str).str.len()
    return {
        "mean_length": round(float(lengths.mean()), 2),
        "max_length": int(lengths.max()),
    }


def _datetime_metadata(series: pd.Series) -> Dict:
    """Metadata específica para fechas."""
    try:
        dt_series = pd.to_datetime(series, errors='coerce').dropna()
        if len(dt_series) == 0:
            return {}
        
        return {
            "min_date": dt_series.min().isoformat() if pd.notna(dt_series.min()) else None,
            "max_date": dt_series.max().isoformat() if pd.notna(dt_series.max()) else None,
            "date_range_days": (dt_series.max() - dt_series.min()).days if len(dt_series) > 0 else 0,
        }
    except:
        return {}
