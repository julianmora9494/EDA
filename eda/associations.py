"""
Associations: correlaciones numéricas, Cramér's V, asociaciones cat-num.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from scipy import stats


def compute_numeric_correlations(
    df: pd.DataFrame,
    numeric_cols: List[str],
    method: str = "pearson"
) -> Dict:
    """
    Calcula correlaciones entre variables numéricas.
    
    Args:
        df: DataFrame
        numeric_cols: Lista de columnas numéricas
        method: 'pearson' o 'spearman'
        
    Returns:
        Diccionario con matriz de correlación y pares destacados
    """
    if len(numeric_cols) < 2:
        return {"matrix": {}, "high_correlations": []}
    
    # Seleccionar solo numéricas válidas
    df_numeric = df[numeric_cols].select_dtypes(include=[np.number])
    
    # Filtrar columnas que parecen IDs, fechas/años, o identificadores
    filtered_cols = []
    for col in df_numeric.columns:
        n_unique = df_numeric[col].nunique()
        n_total = len(df_numeric[col].dropna())
        cardinality_ratio = n_unique / n_total if n_total > 0 else 0
        
        col_lower = str(col).lower()
        
        # Excluir si:
        # 1. Muy alta cardinalidad (>90%) = probablemente ID/celular
        if cardinality_ratio > 0.90:
            continue
        
        # 2. Nombre sugiere ID/celular/documento
        is_explicit_id = any(word in col_lower for word in ['celular', 'telefono', 'phone', 'cedula', 'dni', 'documento', 'id'])
        if is_explicit_id:
            continue
        
        # 3. Parece año/fecha (baja cardinalidad + nombre sugiere temporal)
        is_temporal = any(word in col_lower for word in ['año', 'year', 'anio', 'fecha', 'date', 'mes', 'month', 'dia', 'day'])
        if n_unique < 30 and is_temporal:  # Años típicamente tienen <30 valores únicos
            continue
            
        filtered_cols.append(col)
    
    if len(filtered_cols) < 2:
        return {"matrix": {}, "high_correlations": []}
    
    df_numeric = df_numeric[filtered_cols]
    
    if df_numeric.shape[1] < 2:
        return {"matrix": {}, "high_correlations": []}
    
    # Calcular correlación
    corr_matrix = df_numeric.corr(method=method)
    
    # Convertir a dict
    corr_dict = corr_matrix.to_dict()
    
    # Encontrar correlaciones altas (|r| > 0.7, excluyendo diagonal)
    high_corr = []
    for i, col1 in enumerate(corr_matrix.columns):
        for j, col2 in enumerate(corr_matrix.columns):
            if i < j:  # Solo upper triangle
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.7:
                    high_corr.append({
                        "var1": col1,
                        "var2": col2,
                        "correlation": round(float(corr_val), 4),
                        "abs_correlation": round(abs(float(corr_val)), 4),
                    })
    
    # Ordenar por correlación absoluta
    high_corr = sorted(high_corr, key=lambda x: x['abs_correlation'], reverse=True)
    
    return {
        "method": method,
        "n_variables": len(numeric_cols),
        "matrix": {k: {k2: round(v2, 4) if not pd.isna(v2) else None 
                       for k2, v2 in v.items()} 
                   for k, v in corr_dict.items()},
        "high_correlations": high_corr[:20],  # Top 20
    }


def compute_cramers_v(df: pd.DataFrame, cat_cols: List[str], max_pairs: int = 50) -> Dict:
    """
    Calcula Cramér's V entre variables categóricas de baja cardinalidad.
    
    Args:
        df: DataFrame
        cat_cols: Lista de columnas categóricas
        max_pairs: Máximo de pares a calcular
        
    Returns:
        Diccionario con asociaciones
    """
    if len(cat_cols) < 2:
        return {"associations": []}
    
    # Filtrar categóricas de baja cardinalidad
    low_card_cols = [col for col in cat_cols if df[col].nunique() < 50]
    
    if len(low_card_cols) < 2:
        return {"associations": []}
    
    associations = []
    pair_count = 0
    
    for i, col1 in enumerate(low_card_cols):
        for j, col2 in enumerate(low_card_cols):
            if i < j and pair_count < max_pairs:
                try:
                    v = _cramers_v(df[col1], df[col2])
                    associations.append({
                        "var1": col1,
                        "var2": col2,
                        "cramers_v": round(float(v), 4),
                    })
                    pair_count += 1
                except:
                    pass
    
    # Ordenar por Cramér's V
    associations = sorted(associations, key=lambda x: x['cramers_v'], reverse=True)
    
    return {
        "n_variables": len(low_card_cols),
        "n_pairs_computed": len(associations),
        "associations": associations[:20],  # Top 20
    }


def _cramers_v(x: pd.Series, y: pd.Series) -> float:
    """
    Calcula Cramér's V entre dos variables categóricas.
    
    Args:
        x: Serie 1
        y: Serie 2
        
    Returns:
        Cramér's V (0-1)
    """
    # Tabla de contingencia
    contingency = pd.crosstab(x, y)
    chi2, _, _, _ = stats.chi2_contingency(contingency)
    n = contingency.sum().sum()
    min_dim = min(contingency.shape[0] - 1, contingency.shape[1] - 1)
    
    if min_dim == 0:
        return 0.0
    
    v = np.sqrt(chi2 / (n * min_dim))
    return v


def compute_cat_num_associations(
    df: pd.DataFrame,
    cat_cols: List[str],
    num_cols: List[str],
    max_pairs: int = 30
) -> Dict:
    """
    Analiza asociaciones entre categóricas y numéricas (ANOVA/Kruskal).
    
    Args:
        df: DataFrame
        cat_cols: Columnas categóricas
        num_cols: Columnas numéricas
        max_pairs: Máximo de pares a analizar
        
    Returns:
        Diccionario con asociaciones
    """
    if not cat_cols or not num_cols:
        return {"associations": []}
    
    # Filtrar categóricas de baja cardinalidad
    low_card_cats = [col for col in cat_cols if 2 <= df[col].nunique() < 20]
    
    if not low_card_cats:
        return {"associations": []}
    
    associations = []
    pair_count = 0
    
    for cat_col in low_card_cats:
        for num_col in num_cols:
            if pair_count >= max_pairs:
                break
            try:
                # Agrupar numérica por categórica
                groups = [df[df[cat_col] == cat][num_col].dropna() 
                         for cat in df[cat_col].dropna().unique()]
                
                # Filtrar grupos vacíos
                groups = [g for g in groups if len(g) > 0]
                
                if len(groups) < 2:
                    continue
                
                # Kruskal-Wallis (no paramétrico, más robusto)
                h_stat, p_value = stats.kruskal(*groups)
                
                associations.append({
                    "categorical": cat_col,
                    "numeric": num_col,
                    "n_groups": len(groups),
                    "h_statistic": round(float(h_stat), 4),
                    "p_value": round(float(p_value), 6),
                    "significant": p_value < 0.05,
                })
                pair_count += 1
            except:
                pass
    
    # Ordenar por p-value
    associations = sorted(associations, key=lambda x: x['p_value'])
    
    return {
        "n_categorical": len(low_card_cats),
        "n_numeric": len(num_cols),
        "n_pairs_computed": len(associations),
        "associations": associations[:20],  # Top 20
    }


def compute_all_associations(df: pd.DataFrame, column_roles: Dict[str, str]) -> Dict:
    """
    Calcula todas las asociaciones del dataset.
    
    Args:
        df: DataFrame
        column_roles: Dict {column_name: role}
        
    Returns:
        Diccionario con todas las asociaciones
    """
    # Clasificar columnas por rol (SOLO numéricas puras, excluir IDs, fechas, texto)
    numeric_cols = [col for col, role in column_roles.items() if role == "numeric"]
    cat_low = [col for col, role in column_roles.items() if role == "categorical_low_card"]
    cat_high = [col for col, role in column_roles.items() if role == "categorical_high_card"]
    cat_cols = cat_low + cat_high
    
    return {
        "numeric_correlations": compute_numeric_correlations(df, numeric_cols, method="pearson"),
        "numeric_correlations_spearman": compute_numeric_correlations(df, numeric_cols, method="spearman"),
        "categorical_associations": compute_cramers_v(df, cat_cols),
        "cat_num_associations": compute_cat_num_associations(df, cat_cols, numeric_cols),
    }
