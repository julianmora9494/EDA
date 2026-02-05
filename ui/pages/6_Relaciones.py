"""
Página de Relaciones: Correlaciones y asociaciones entre variables.
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Añadir ruta para imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from ui.components.charts import plot_correlation_heatmap

st.set_page_config(page_title="Relaciones - EDA Dashboard", page_icon="🔗", layout="wide")

st.title("🔗 Relaciones entre Variables")

with st.expander("ℹ️ ¿Qué muestra esta página?", expanded=False):
    st.markdown("""
    ### Análisis de Asociaciones Bivariadas
    
    Esta página identifica **relaciones entre pares de variables**:
    
    **🔢 Correlación Numérica (Pearson):**
    - **Qué mide**: Relación lineal entre variables numéricas
    - **Rango**: -1 (correlación negativa perfecta) a +1 (positiva perfecta)
    - **Interpretación**:
      - |r| > 0.7: Correlación fuerte
      - |r| 0.3-0.7: Correlación moderada
      - |r| < 0.3: Correlación débil
    - **Uso**: Detectar multicolinealidad, redundancia
    
    **🔢 Correlación Numérica (Spearman):**
    - **Qué mide**: Relación monótona (no necesariamente lineal)
    - **Ventaja**: Más robusto a outliers y relaciones no lineales
    - **Uso**: Cuando la relación no es estrictamente lineal
    
    **📑 Asociación Categórica (Cramér's V):**
    - **Qué mide**: Asociación entre variables categóricas
    - **Rango**: 0 (independientes) a 1 (completamente asociadas)
    - **Método**: Chi-cuadrado normalizado
    - **Limitación**: Solo para categóricas de baja cardinalidad (<50 categorías)
    
    **🔗 Asociación Cat-Num (Kruskal-Wallis):**
    - **Qué mide**: Si la variable numérica difiere entre grupos categóricos
    - **Método**: Test no paramétrico (no asume normalidad)
    - **p-value < 0.05**: Diferencia significativa entre grupos
    - **Uso**: Identificar variables categóricas que "explican" variación numérica
    
    **⚠️ Límites de Performance:**
    - Correlaciones: Todas las numéricas
    - Cramér's V: Máximo 50 pares
    - Cat-Num: Máximo 30 pares
    - Muestreo: Si dataset >50k filas, se usa muestra
    """)

# Verificar que hay datos cargados
if "profile" not in st.session_state or st.session_state.profile is None:
    st.warning("⚠️ No hay dataset cargado. Ve a la página principal para subir un archivo.")
    st.stop()

profile = st.session_state.profile
associations = profile["associations"]

# Tabs por tipo de asociación
tab1, tab2, tab3, tab4 = st.tabs([
    "🔢 Numéricas (Pearson)",
    "🔢 Numéricas (Spearman)",
    "📑 Categóricas (Cramér's V)",
    "🔗 Cat-Num (Kruskal)"
])

# Tab 1: Correlación Pearson
with tab1:
    st.subheader("Correlación de Pearson (variables numéricas)")
    
    pearson = associations.get("numeric_correlations", {})
    
    if pearson.get("matrix"):
        plot_correlation_heatmap(pearson["matrix"])
        
        # Correlaciones altas
        high_corr = pearson.get("high_correlations", [])
        
        if high_corr:
            st.subheader("⚠️ Correlaciones Altas (|r| > 0.7)")
            
            df_corr = pd.DataFrame(high_corr)
            st.dataframe(
                df_corr[["var1", "var2", "correlation"]],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("✅ No se detectaron correlaciones altas (|r| > 0.7)")
    else:
        st.info("No hay suficientes variables numéricas para calcular correlaciones")

# Tab 2: Correlación Spearman
with tab2:
    st.subheader("Correlación de Spearman (variables numéricas)")
    st.caption("Spearman captura relaciones monótonas no lineales")
    
    spearman = associations.get("numeric_correlations_spearman", {})
    
    if spearman.get("matrix"):
        plot_correlation_heatmap(spearman["matrix"])
        
        high_corr = spearman.get("high_correlations", [])
        
        if high_corr:
            st.subheader("⚠️ Correlaciones Altas (|ρ| > 0.7)")
            
            df_corr = pd.DataFrame(high_corr)
            st.dataframe(
                df_corr[["var1", "var2", "correlation"]],
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("No hay suficientes variables numéricas para calcular correlaciones")

# Tab 3: Cramér's V
with tab3:
    st.subheader("Cramér's V (asociación categórica-categórica)")
    st.caption("Mide asociación entre variables categóricas (0 = independientes, 1 = completamente asociadas)")
    
    cramers = associations.get("categorical_associations", {})
    
    if cramers.get("associations"):
        df_cramers = pd.DataFrame(cramers["associations"])
        
        st.metric("Pares analizados", cramers.get("n_pairs_computed", 0))
        
        st.dataframe(
            df_cramers[["var1", "var2", "cramers_v"]],
            use_container_width=True,
            hide_index=True
        )
        
        # Top asociaciones
        st.subheader("Top 5 Asociaciones más Fuertes")
        top5 = df_cramers.head(5)
        
        for idx, row in top5.iterrows():
            st.info(f"**{row['var1']}** ↔ **{row['var2']}**: V = {row['cramers_v']:.3f}")
    else:
        st.info("No hay suficientes variables categóricas de baja cardinalidad para calcular Cramér's V")

# Tab 4: Cat-Num
with tab4:
    st.subheader("Asociación Categórica-Numérica (Kruskal-Wallis)")
    st.caption("Prueba si la variable numérica difiere significativamente entre grupos categóricos")
    
    cat_num = associations.get("cat_num_associations", {})
    
    if cat_num.get("associations"):
        df_cat_num = pd.DataFrame(cat_num["associations"])
        
        st.metric("Pares analizados", cat_num.get("n_pairs_computed", 0))
        
        # Colorear por significancia
        def highlight_significant(row):
            if row["significant"]:
                return ["background-color: #90EE90"] * len(row)
            return [""] * len(row)
        
        st.dataframe(
            df_cat_num[["categorical", "numeric", "n_groups", "h_statistic", "p_value", "significant"]],
            use_container_width=True,
            hide_index=True
        )
        
        # Top asociaciones significativas
        sig_assoc = df_cat_num[df_cat_num["significant"] == True]
        
        if not sig_assoc.empty:
            st.subheader(f"✅ {len(sig_assoc)} Asociaciones Significativas (p < 0.05)")
            
            for idx, row in sig_assoc.head(10).iterrows():
                st.success(f"**{row['categorical']}** → **{row['numeric']}**: H = {row['h_statistic']:.2f}, p = {row['p_value']:.4f}")
        else:
            st.info("No se detectaron asociaciones significativas (p < 0.05)")
    else:
        st.info("No hay suficientes pares categórica-numérica para analizar")

# Resumen general
st.divider()
st.subheader("📝 Resumen de Asociaciones")

summary_text = []

# Pearson
pearson = associations.get("numeric_correlations", {})
if pearson.get("high_correlations"):
    n_high = len(pearson["high_correlations"])
    summary_text.append(f"- 🔢 **{n_high}** pares de variables numéricas con correlación alta (Pearson |r| > 0.7)")

# Cramér's V
cramers = associations.get("categorical_associations", {})
if cramers.get("associations"):
    top_v = cramers["associations"][0]["cramers_v"] if cramers["associations"] else 0
    summary_text.append(f"- 📑 Asociación categórica más fuerte: V = {top_v:.3f}")

# Cat-Num
cat_num = associations.get("cat_num_associations", {})
if cat_num.get("associations"):
    sig_count = sum(1 for a in cat_num["associations"] if a.get("significant"))
    summary_text.append(f"- 🔗 **{sig_count}** asociaciones cat-num significativas (p < 0.05)")

if summary_text:
    for text in summary_text:
        st.markdown(text)
else:
    st.info("No se detectaron asociaciones significativas en el dataset")
