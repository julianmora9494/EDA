"""
Análisis Profundo de Productos: Tenencia, Penetración y Cross-Sell
Enfoque: Análisis univariado y multivariado de productos bancarios
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

st.set_page_config(page_title="Análisis de Productos", page_icon="🏦", layout="wide")

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

st.title("🏦 Análisis Profundo de Productos Bancarios")
st.caption("PASIVOS (CA, CC, DP) | ACTIVOS (TC, PR) - Tenencia, penetración y cross-sell")

# Identificar columnas
all_columns = [col['name'] for col in profile['columns']]

saldo_total_col = [col for col in all_columns if 'saldo' in col.lower() and 'total' in col.lower()][0]
total_cuentas_col = [col for col in all_columns if 'total' in col.lower() and 'cuenta' in col.lower()]
total_cuentas_col = total_cuentas_col[0] if total_cuentas_col else None

# Columnas de productos
cuentas_product_cols = [col for col in all_columns if 'cuenta' in col.lower() and any(x in col.upper() for x in ['CA', 'CC', 'DP', 'PR', 'TC']) and 'btb' not in col.lower()]
saldo_product_cols = [col for col in all_columns if 'saldo' in col.lower() and any(x in col.upper() for x in ['CA', 'CC', 'DP', 'PR', 'TC']) and 'btb' not in col.lower()]

edad_col = [col for col in all_columns if 'edad' in col.lower()]
edad_col = edad_col[0] if edad_col else None

banca_col = [col for col in all_columns if 'banca' in col.lower()]
banca_col = banca_col[0] if banca_col else None

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

columns_to_fetch = [saldo_total_col] + cuentas_product_cols + saldo_product_cols
if total_cuentas_col:
    columns_to_fetch.append(total_cuentas_col)
if edad_col:
    columns_to_fetch.append(edad_col)
if banca_col:
    columns_to_fetch.append(banca_col)

df = get_data(dataset_id, columns_to_fetch)

if df is None:
    st.error("❌ Error al cargar datos")
    st.stop()

# Limpiar datos
df = df.replace([None], np.nan)
for col in df.columns:
    if col not in [banca_col]:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# ==================== TABS ====================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Análisis Univariado",
    "🔗 Análisis Multivariado",
    "🎯 Oportunidades Cross-Sell",
    "👥 Segmentación por Edad"
])

# ==================== TAB 1: UNIVARIADO ====================
with tab1:
    st.header("📊 Análisis Univariado de Productos")
    
    st.markdown("""
    Análisis individual de cada producto: tenencia, saldos, distribución
    """)
    
    # 1. Profundidad de relación
    if total_cuentas_col:
        st.subheader("🏦 Profundidad de Relación")
        
        st.info("""
        **📚 ¿Qué mide esta sección?**
        
        La **profundidad de relación** indica cuántos productos tiene cada cliente:
        
        - **Mono-producto**: Clientes con solo **1 producto** (ej: solo cuenta de ahorro)
        - **Bi-producto**: Clientes con exactamente **2 productos** (ej: cuenta + tarjeta)
        - **Multi-producto**: Clientes con **3 o más productos** (mayor vinculación)
        
        **¿Por qué es importante?**
        - Clientes con más productos son más leales y rentables
        - Identificar clientes mono-producto para ofrecer más productos (cross-sell)
        - Mayor número de productos = mayor valor para el banco
        """)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_prod = df[total_cuentas_col].mean()
            st.metric("Productos Promedio", f"{avg_prod:.2f}")
        
        with col2:
            mono = len(df[df[total_cuentas_col] == 1])
            st.metric("Mono-producto", f"{mono:,}")
            st.caption(f"{mono/len(df)*100:.1f}% del total")
        
        with col3:
            bi = len(df[df[total_cuentas_col] == 2])
            st.metric("Bi-producto", f"{bi:,}")
            st.caption(f"{bi/len(df)*100:.1f}% del total")
        
        with col4:
            multi = len(df[df[total_cuentas_col] >= 3])
            st.metric("Multi-producto (≥3)", f"{multi:,}")
            st.caption(f"{multi/len(df)*100:.1f}% del total")
        
        # Distribución
        col1, col2 = st.columns([2, 1])
        
        with col1:
            counts = df[total_cuentas_col].value_counts().sort_index()
            fig = px.bar(
                x=counts.index,
                y=counts.values,
                title='Distribución de Clientes por Número de Productos',
                labels={'x': 'Número de Productos', 'y': 'Clientes'},
                text=counts.values
            )
            fig.update_traces(texttemplate='%{text:,}', textposition='outside')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            st.caption("""
            **🔍 Cómo leer este gráfico**:
            - **Eje X**: Número de productos que tiene el cliente
            - **Eje Y**: Cantidad de clientes con ese número
            - **Barras altas a la izquierda**: Muchos clientes con pocos productos (oportunidad)
            - **Barras altas a la derecha**: Clientes muy vinculados (retener)
            """)
        
        with col2:
            st.markdown("**💡 Análisis:**")
            if mono/len(df) > 0.5:
                st.warning(f"""
                ⚠️ **Más del 50%** tiene solo 1 producto.
                
                **Alta oportunidad de cross-sell**
                """)
            st.markdown("---")
            st.markdown("**Distribución:**")
            for n, count in list(counts.items())[:8]:
                pct = count/len(df)*100
                st.markdown(f"- {int(n)} prod: {count:,} ({pct:.1f}%)")
        
        st.divider()
    
    # 2. Tenencia por producto
    st.subheader("📦 Tenencia y Penetración por Producto")
    
    st.info("""
    **📚 ¿Qué mide esta sección?**
    
    - **Tenencia**: Número de clientes que tienen cada producto
    - **Penetración %**: Porcentaje de clientes que tienen el producto (Tenencia / Total Clientes × 100)
    - **Promedio**: Saldo promedio de TODOS los clientes (incluye ceros y negativos)
    - **Suma**: Suma total de saldos de TODOS los clientes
    
    **¿Por qué es importante?**
    - Identificar productos más populares (alta penetración)
    - Detectar productos con baja adopción (oportunidad de marketing)
    - Validar que los valores coincidan con "Análisis de Saldos"
    """)
    
    tenencia_data = []
    for col in cuentas_product_cols:
        product_name = col.replace('Cuentas', '').strip()
        n_clientes = (df[col] > 0).sum()
        penetracion = (n_clientes / len(df) * 100)
        
        # Buscar columna de saldo correspondiente
        saldo_col = f"Saldo {product_name}"
        if saldo_col in saldo_product_cols:
            # REGLA: Suma y Promedio de TODOS (incluye negativos)
            suma_total = df[saldo_col].sum()  # NO usar fillna
            promedio_total = df[saldo_col].mean()  # Promedio de TODOS
        else:
            suma_total = 0
            promedio_total = 0
        
        tenencia_data.append({
            'Producto': product_name,
            'N° Clientes (>0)': n_clientes,
            'Penetración %': penetracion,
            'Promedio': promedio_total,
            'Suma': suma_total
        })
    
    df_tenencia = pd.DataFrame(tenencia_data).sort_values('N° Clientes (>0)', ascending=False)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Gráfico de penetración
        fig = px.bar(
            df_tenencia,
            x='Producto',
            y='Penetración %',
            title='Penetración de Productos (%)',
            text='Penetración %',
            color='Penetración %',
            color_continuous_scale='Blues'
        )
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        st.caption("""
        **🔍 Cómo leer este gráfico**:
        - **Eje X**: Nombre del producto (CA, CC, DP, TC, PR, etc.)
        - **Eje Y**: Porcentaje de clientes que tienen el producto
        - **Barras altas**: Productos muy populares (ej: si CA está alto, muchos tienen cuenta de ahorro)
        - **Barras bajas**: Productos nicho o con baja adopción (oportunidad de marketing)
        """)
    
    with col2:
        st.dataframe(
            df_tenencia.style.format({
                'N° Clientes (>0)': '{:,}',
                'Penetración %': '{:.1f}%',
                'Promedio': '${:,.0f}',
                'Suma': '${:,.0f}'
            }),
            use_container_width=True,
            hide_index=True
        )
        
        st.caption("**Nota**: Suma y Promedio incluyen TODOS los valores (positivos, negativos, ceros). Valores idénticos a pestaña Análisis de Saldos.")
    
    st.divider()
    
    # 3. Distribuciones de saldo por producto
    st.subheader("📈 Distribución de Saldos por Producto")
    
    st.info("""
    **📚 ¿Qué mide esta sección?**
    
    Muestra cómo se distribuyen los **saldos** de un producto específico entre los clientes:
    
    - **Histograma**: Muestra cuántos clientes tienen saldos en cada rango (ej: cuántos tienen entre $1,000-$5,000)
    - **Boxplot**: Muestra la dispersión: mediana (línea central), cuartiles (caja) y valores atípicos (puntos)
    
    **¿Por qué es importante?**
    - Identificar la concentración de saldos (pocos con mucho vs muchos con poco)
    - Detectar outliers (clientes con saldos muy altos o muy bajos)
    - Entender el perfil típico de saldo para cada producto
    
    **Nota**: Las estadísticas incluyen TODOS los clientes (con y sin el producto).
    """)
    
    # Seleccionar producto
    product_names = [col.replace('Saldo', '').strip() for col in saldo_product_cols]
    selected_product = st.selectbox("Seleccionar Producto:", product_names)
    
    saldo_col_selected = f"Saldo {selected_product}"
    if saldo_col_selected in df.columns:
        # REGLA: NO filtrar, usar TODOS los valores
        df_product = df.copy()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Promedio", f"${df_product[saldo_col_selected].mean():,.0f}")
        with col2:
            st.metric("Mediana", f"${df_product[saldo_col_selected].median():,.0f}")
        with col3:
            st.metric("Máximo", f"${df_product[saldo_col_selected].max():,.0f}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Histograma
            fig = px.histogram(
                df_product,
                x=saldo_col_selected,
                title=f'Distribución de {saldo_col_selected}',
                nbins=50,
                log_y=True
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Boxplot
            fig = px.box(
                df_product,
                y=saldo_col_selected,
                title=f'Boxplot de {saldo_col_selected}',
                log_y=True,
                points='outliers'
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

# ==================== TAB 2: MULTIVARIADO ====================
with tab2:
    st.header("🔗 Análisis Multivariado: Productos vs Saldo Total")
    
    # 1. Productos vs Saldo Total
    if total_cuentas_col:
        st.subheader("📈 Relación: Número de Productos vs Saldo Total")
        
        fig = px.scatter(
            df,
            x=total_cuentas_col,
            y=saldo_total_col,
            color=banca_col if banca_col else None,
            title=f'{total_cuentas_col} vs {saldo_total_col}',
            log_y=True,
            trendline='ols',
            opacity=0.6
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Análisis por segmento de productos
        df['Segmento Productos'] = 'Mono'
        df.loc[df[total_cuentas_col] == 2, 'Segmento Productos'] = 'Bi'
        df.loc[df[total_cuentas_col] >= 3, 'Segmento Productos'] = 'Multi'
        
        stats = df.groupby('Segmento Productos')[saldo_total_col].agg(['count', 'mean', 'median', 'sum']).round(0)
        stats.columns = ['N° Clientes', 'Saldo Promedio', 'Saldo Mediano', 'Saldo Total']
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.dataframe(
                stats.style.format({
                    'N° Clientes': '{:,.0f}',
                    'Saldo Promedio': '${:,.0f}',
                    'Saldo Mediano': '${:,.0f}',
                    'Saldo Total': '${:,.0f}'
                }),
                use_container_width=True
            )
        
        with col2:
            mono_avg = df[df[total_cuentas_col] == 1][saldo_total_col].mean()
            multi_avg = df[df[total_cuentas_col] >= 3][saldo_total_col].mean()
            
            if multi_avg > mono_avg * 1.5:
                st.success(f"""
                ✅ **Validado**: Multi-producto tiene **{multi_avg/mono_avg:.1f}x** más saldo promedio
                
                **Recomendación**: Priorizar cross-sell
                """)
        
        st.divider()
    
    # 2. Matriz de tenencia de productos
    st.subheader("🔍 Matriz de Co-tenencia de Productos")
    
    st.markdown("**¿Qué productos se tienen juntos?**")
    
    # Crear matriz de co-tenencia
    products = []
    for col in cuentas_product_cols:
        product_name = col.replace('Cuentas', '').strip()
        products.append(product_name)
        df[f'Tiene_{product_name}'] = (df[col] > 0).astype(int)
    
    # Calcular correlaciones
    tenencia_cols = [f'Tiene_{p}' for p in products]
    corr_matrix = df[tenencia_cols].corr()
    corr_matrix.index = products
    corr_matrix.columns = products
    
    fig = px.imshow(
        corr_matrix,
        title='Correlación de Tenencia entre Productos',
        labels=dict(color="Correlación"),
        text_auto='.2f',
        aspect='auto',
        color_continuous_scale='RdYlGn'
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    **💡 Interpretación:**
    - Valores **altos** (verde): Productos frecuentemente tenidos juntos → Cross-sell natural
    - Valores **bajos** (rojo): Productos raramente combinados → Oportunidad de bundling
    """)
    
    st.divider()
    
    # 3. Composición de cartera por nivel de productos
    st.subheader("🎨 Composición de Cartera según Profundidad")
    
    if total_cuentas_col:
        # Agrupar por segmento de productos
        composition = []
        for segment in ['Mono', 'Bi', 'Multi']:
            df_seg = df[df['Segmento Productos'] == segment]
            for col in saldo_product_cols:
                product_name = col.replace('Saldo', '').strip()
                composition.append({
                    'Segmento': segment,
                    'Producto': product_name,
                    'Saldo': df_seg[col].sum()
                })
        
        df_comp = pd.DataFrame(composition)
        
        fig = px.bar(
            df_comp,
            x='Segmento',
            y='Saldo',
            color='Producto',
            title='Composición de Saldos por Segmento de Profundidad',
            barmode='stack'
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

# ==================== TAB 3: CROSS-SELL ====================
with tab3:
    st.header("🎯 Oportunidades de Cross-Sell")
    
    st.info("""
    **📚 ¿Qué es Cross-Sell?**
    
    **Cross-Sell** (venta cruzada) es ofrecer productos adicionales a clientes existentes.
    
    **Ejemplo**: Un cliente tiene solo cuenta de ahorro → ofrecerle tarjeta de crédito o depósito a plazo.
    
    **¿Por qué es importante?**
    - Aumenta la **profundidad de relación** (más productos por cliente)
    - Incrementa **ingresos** sin costo de adquisición de nuevos clientes
    - Mejora **retención** (clientes con más productos son más leales)
    - Es **5-10x más barato** vender a clientes existentes que captar nuevos
    
    **¿Cómo funciona esta sección?**
    - Identifica clientes con **alto saldo pero pocos productos** (sub-bancarizados)
    - Muestra qué productos tienen **baja penetración** en segmentos de alto valor
    - Detecta **oportunidades específicas** de venta cruzada
    """)
    
    # 1. Clientes sub-bancarizados
    st.subheader("💰 Clientes Sub-Bancarizados (Alto Potencial)")
    
    st.caption("""
    **¿Qué son clientes sub-bancarizados?**
    - Clientes con **saldo alto** (≥ percentil 75) pero **pocos productos** (≤ 2)
    - **Alta oportunidad**: tienen dinero pero no están usando todos nuestros productos
    - **Objetivo**: ofrecerles más productos para aumentar su vinculación
    """)
    
    if total_cuentas_col:
        p75 = df[saldo_total_col].quantile(0.75)
        
        df_sub = df[
            (df[saldo_total_col] >= p75) &
            (df[total_cuentas_col] <= 2)
        ].copy()
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            st.metric(
                "Clientes Sub-Bancarizados",
                f"{len(df_sub):,}",
                help=f"Saldo ≥ ${p75:,.0f} y ≤ 2 productos"
            )
        
        with col2:
            if len(df_sub) > 0:
                st.metric("Saldo Promedio", f"${df_sub[saldo_total_col].mean():,.0f}")
        
        with col3:
            if len(df_sub) > 0:
                saldo_sub = df_sub[saldo_total_col].sum()
                st.metric("Saldo Total", f"${saldo_sub:,.0f}")
        
        if len(df_sub) > 0:
            st.info(f"""
            💰 **Oportunidad**: {len(df_sub)} clientes con alto saldo pero baja profundidad
            
            **Acción**: Campaña de cross-sell focalizada
            """)
            
            # Top 10
            with st.expander("Ver Top 10 Clientes Sub-Bancarizados"):
                cols_show = [saldo_total_col, total_cuentas_col]
                if banca_col:
                    cols_show.append(banca_col)
                
                df_top = df_sub.nlargest(10, saldo_total_col)[cols_show]
                
                st.dataframe(
                    df_top.style.format({
                        saldo_total_col: '${:,.0f}',
                        total_cuentas_col: '{:.0f}'
                    }),
                    use_container_width=True
                )
        
        st.divider()
    
    # 2. Penetración por segmento de valor
    st.subheader("📊 Penetración de Productos por Nivel de Saldo")
    
    with st.expander("📖 ¿Cómo se crearon los segmentos? (clic para expandir)"):
        p50_val = df[saldo_total_col].quantile(0.50)
        p75_val = df[saldo_total_col].quantile(0.75)
        
        st.markdown(f"""
        **🔢 Segmentación basada en: `{saldo_total_col}`**
        
        Los clientes se dividen en 3 grupos usando **percentiles** del Saldo Total:
        
        - **Segmento BAJO**: {saldo_total_col} < **${p50_val:,.0f}** (percentil 50)
          - Son el 50% de clientes con **menor saldo**
        
        - **Segmento MEDIO**: {saldo_total_col} entre **${p50_val:,.0f}** y **${p75_val:,.0f}**
          - Son el 25% de clientes con **saldo medio** (percentil 50 a 75)
        
        - **Segmento ALTO**: {saldo_total_col} ≥ **${p75_val:,.0f}** (percentil 75+)
          - Son el 25% de clientes con **mayor saldo**
        
        ---
        
        **¿Qué muestra el heatmap?**
        
        Para cada segmento, calcula **qué % de clientes tiene cada producto** (penetración).
        
        **Ejemplo práctico**:
        
        Si el heatmap muestra:
        - **Depósito a Plazo (DP)** en segmento **Alto**: 30%
        
        **Significa**: De todos los clientes con Saldo Total ≥ ${p75_val:,.0f}, solo el 30% tiene Depósito a Plazo.
        
        **Oportunidad**: El 70% restante de clientes ricos NO tiene DP → campaña para ofrecerles este producto.
        
        ---
        
        **¿Cómo usar el heatmap?**
        - **Verde**: Alta penetración (muchos ya tienen el producto)
        - **Amarillo**: Penetración media
        - **Rojo**: Baja penetración (OPORTUNIDAD de venta)
        
        **Foco**: Buscar celdas **ROJAS en columna ALTO** = productos para vender a clientes con más dinero.
        """)
    
    
    # Crear segmentos
    p50 = df[saldo_total_col].quantile(0.50)
    p75 = df[saldo_total_col].quantile(0.75)
    
    df['Segmento Valor'] = 'Bajo'
    df.loc[df[saldo_total_col] >= p50, 'Segmento Valor'] = 'Medio'
    df.loc[df[saldo_total_col] >= p75, 'Segmento Valor'] = 'Alto'
    
    # Calcular penetración por segmento
    penetration = []
    for segment in ['Alto', 'Medio', 'Bajo']:
        df_seg = df[df['Segmento Valor'] == segment]
        for col in cuentas_product_cols:
            product_name = col.replace('Cuentas', '').strip()
            pct = (df_seg[col] > 0).sum() / len(df_seg) * 100
            penetration.append({
                'Segmento': segment,
                'Producto': product_name,
                'Penetración %': pct
            })
    
    df_pen = pd.DataFrame(penetration)
    df_pivot = df_pen.pivot(index='Producto', columns='Segmento', values='Penetración %')
    df_pivot = df_pivot[['Alto', 'Medio', 'Bajo']]
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        fig = px.imshow(
            df_pivot,
            title='Heatmap: Penetración de Productos por Segmento (%)',
            text_auto='.1f',
            aspect='auto',
            color_continuous_scale='RdYlGn',
            labels=dict(color="Penetración %")
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        st.caption("""
        **🔍 Cómo leer el heatmap**:
        - **Filas**: Productos (CA, CC, DP, PR, TC, etc.)
        - **Columnas**: Segmentos de valor (Alto, Medio, Bajo)
        - **Color**: Verde = alta penetración, Rojo = baja penetración
        - **Número**: % de clientes del segmento que tienen el producto
        """)
    
    with col2:
        st.markdown("### 💡 Análisis de Oportunidades")
        
        # Identificar oportunidades automáticamente
        alto_seg = df_pivot['Alto']
        bajo_penetracion_alto = alto_seg[alto_seg < 50].sort_values()
        
        if len(bajo_penetracion_alto) > 0:
            st.success(f"""
            **🎯 Productos prioritarios para segmento ALTO**:
            """)
            for producto, pct in bajo_penetracion_alto.head(3).items():
                st.markdown(f"- **{producto}**: solo {pct:.1f}% de penetración")
                st.progress(pct/100)
            
            st.info("""
            **Acción sugerida**: 
            Diseñar campaña de cross-sell enfocada en estos productos para clientes del segmento Alto.
            """)
        
        st.markdown("---")
        
        st.markdown("""
        **📊 Reglas de interpretación**:
        
        - **Penetración < 30% en segmento Alto**: 🔴 Oportunidad crítica
        - **Penetración 30-50% en segmento Alto**: 🟡 Oportunidad moderada  
        - **Penetración > 50% en segmento Alto**: 🟢 Buena adopción
        
        - **Diferencia >20 puntos entre Alto y Medio**: Estrategia diferenciada necesaria
        """)
    

# ==================== TAB 4: EDAD ====================
with tab4:
    if edad_col:
        st.header("👥 Análisis por Ciclo de Vida (Edad)")
        
        st.info("""
        **📚 ¿Qué es el Análisis por Ciclo de Vida?**
        
        El **ciclo de vida financiero** muestra cómo cambian las necesidades y comportamientos bancarios según la edad:
        
        - **<30 años** (Jóvenes): Inician vida financiera, buscan cuentas básicas y tarjetas
        - **30-40 años** (Profesionales jóvenes): Compran casa/auto, necesitan préstamos
        - **40-50 años** (Consolidación): Ahorran más, invierten en depósitos a plazo
        - **50-60 años** (Pre-jubilación): Maximizan ahorros, planifican retiro
        - **60+ años** (Jubilados): Viven de ahorros e inversiones, menos préstamos
        
        **¿Por qué es importante?**
        - **Personalización**: Ofrecer productos según etapa de vida
        - **Predicción**: Anticipar necesidades futuras del cliente
        - **Campañas**: Segmentar marketing por edad
        - **Retención**: Acompañar al cliente en cada etapa
        
        **¿Cómo funciona esta sección?**
        - Divide clientes en **5 tramos de edad**
        - Muestra **saldo promedio** y **número de productos** por tramo
        - Identifica qué productos son más populares en cada edad
        """)
        
        # Crear tramos
        df['Tramo Edad'] = pd.cut(
            df[edad_col],
            bins=[0, 30, 40, 50, 60, 100],
            labels=['<30', '30-40', '40-50', '50-60', '60+']
        )
        
        # Estadísticas por tramo
        st.subheader("📊 Productos y Saldo por Edad")
        
        st.caption("""
        **¿Cómo leer esta tabla?**
        - **N° Clientes**: Cuántos clientes hay en cada tramo de edad
        - **Saldo Promedio/Mediano**: Cuánto dinero tienen en promedio
        - **Productos Prom**: Cuántos productos tienen en promedio
        
        **Patrón esperado**: Saldo aumenta con la edad (acumulan riqueza), productos también aumentan (mayor vinculación).
        """)
        
        agg_dict = {saldo_total_col: ['count', 'mean', 'median']}
        if total_cuentas_col:
            agg_dict[total_cuentas_col] = 'mean'
        
        lifecycle = df.groupby('Tramo Edad').agg(agg_dict).round(1)
        
        cols = ['N° Clientes', 'Saldo Promedio', 'Saldo Mediano']
        if total_cuentas_col:
            cols.append('Productos Prom')
        lifecycle.columns = cols
        
        st.dataframe(
            lifecycle.style.format({
                'N° Clientes': '{:,.0f}',
                'Saldo Promedio': '${:,.0f}',
                'Saldo Mediano': '${:,.0f}',
                'Productos Prom': '{:.1f}' if total_cuentas_col else None
            }),
            use_container_width=True
        )
        
        st.divider()
        
        # Boxplot por edad
        fig = px.box(
            df,
            x='Tramo Edad',
            y=saldo_total_col,
            title=f'{saldo_total_col} por Tramo de Edad',
            log_y=True,
            points='outliers'
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        st.caption("""
        **🔍 Cómo leer el Boxplot**:
        - **Línea central de la caja**: Mediana (saldo típico de ese tramo)
        - **Caja**: Rango intercuartílico (donde está el 50% central de clientes)
        - **Líneas (bigotes)**: Rango normal de saldos
        - **Puntos fuera**: Outliers (clientes con saldos muy altos o bajos)
        - **Escala logarítmica**: Permite ver todos los rangos (de $100 a millones)
        
        **Interpretación**: Si la caja es más alta en 50-60 → ese tramo tiene más saldo.
        """)
        
        st.divider()
        
        # Penetración por edad
        st.subheader("📊 Penetración de Productos por Edad")
        
        st.caption("""
        **¿Qué muestra este gráfico?**
        - Qué **porcentaje** de cada tramo de edad tiene cada producto
        - **Barras agrupadas**: Compara productos dentro del mismo tramo
        
        **Ejemplo de uso**:
        - Si jóvenes (<30) tienen baja penetración de DP → campaña de ahorro para jóvenes
        - Si 60+ tienen baja penetración de TC → ofrecer tarjetas con beneficios para jubilados
        """)
        
        pen_edad = []
        for tramo in ['<30', '30-40', '40-50', '50-60', '60+']:
            df_tramo = df[df['Tramo Edad'] == tramo]
            if len(df_tramo) > 0:
                for col in cuentas_product_cols:
                    product_name = col.replace('Cuentas', '').strip()
                    pct = (df_tramo[col] > 0).sum() / len(df_tramo) * 100
                    pen_edad.append({
                        'Tramo': tramo,
                        'Producto': product_name,
                        'Penetración %': pct
                    })
        
        df_pen_edad = pd.DataFrame(pen_edad)
        
        fig = px.bar(
            df_pen_edad,
            x='Tramo',
            y='Penetración %',
            color='Producto',
            title='Penetración de Productos por Tramo de Edad',
            barmode='group'
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        **💡 Insight**:
        - Identifica qué productos son más relevantes para cada grupo etario
        - Orienta campañas segmentadas por ciclo de vida
        """)
    else:
        st.info("⚠️ No se encontró columna de Edad")

st.divider()
st.caption("🏦 Análisis profesional univariado y multivariado de productos bancarios")
