"""
Módulo para exportar análisis completo a HTML.
Genera un reporte HTML completo con TODAS las secciones del dashboard.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd


def generate_html_report(profile: Dict[str, Any], filename: str = None, dataset: Optional[Dict] = None) -> str:
    """
    Generar reporte HTML COMPLETO del análisis.
    
    Args:
        profile: Diccionario con el análisis completo del perfil
        filename: Nombre del archivo (sin extensión)
        dataset: Datos completos del dataset (opcional)
        
    Returns:
        str: Contenido HTML del reporte
    """
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Analisis_EDA_{timestamp}"
    
    # Extraer información del perfil
    overview = profile.get("overview", {})
    quality = profile.get("quality", {})
    columns = profile.get("columns", [])
    insights = profile.get("insights", [])
    
    # Formatear números
    def fmt_num(value):
        if value is None: return "N/A"
        if isinstance(value, (int, float)):
            try: return f"{value:,}"
            except: return str(value)
        return str(value)
    
    def fmt_pct(value):
        if value is None: return "N/A"
        if isinstance(value, (int, float)):
            try: return f"{value:.1f}%"
            except: return str(value)
        return str(value)
    
    def fmt_money(value):
        if value is None: return "$0"
        if isinstance(value, (int, float)):
            try: return f"${value:,.2f}"
            except: return str(value)
        return str(value)
    
    # Valores básicos
    n_rows = fmt_num(overview.get("n_rows", 0))
    n_columns = fmt_num(overview.get("n_columns", 0))
    memory_mb = overview.get("memory_mb", 0)
    memory_str = f"{memory_mb:.2f} MB" if isinstance(memory_mb, (int, float)) else "N/A"
    
    # Calidad
    missing_info = quality.get("missing", {})
    pct_missing = fmt_pct(missing_info.get("pct_missing_global", 0))
    cols_with_missing = fmt_num(missing_info.get("columns_with_missing", 0))
    duplicates = fmt_num(overview.get("n_duplicate_rows", 0))
    pct_duplicates = fmt_pct(overview.get("pct_duplicate_rows", 0))
    
    # Análisis de productos y patrimonio (si hay datos)
    productos_html = ""
    patrimonial_html = ""
    geografico_html = ""
    
    if dataset and isinstance(dataset, dict):
        df_data = dataset.get("data", [])
        if df_data:
            df = pd.DataFrame(df_data)
            
            # ANÁLISIS DE PRODUCTOS
            producto_cols = [col for col in df.columns if col.startswith("Tiene ") or col.startswith("Saldo ")]
            if producto_cols:
                productos_html = "<div class='section'><h2>🏦 Análisis de Productos Bancarios</h2>"
                productos_html += "<div class='metrics-grid'>"
                
                # Analizar cada producto
                for col in producto_cols[:10]:  # Primeros 10 productos
                    if col in df.columns:
                        if df[col].dtype in ['int64', 'float64']:
                            total = df[col].sum()
                            promedio = df[col].mean()
                            clientes = (df[col] > 0).sum()
                            
                            productos_html += f"""
                                <div class='metric-card'>
                                    <h3>{col}</h3>
                                    <div class='metric-value'>{fmt_money(total)}</div>
                                    <div class='metric-unit'>Total | Promedio: {fmt_money(promedio)}</div>
                                    <div class='metric-unit'>Clientes: {clientes}</div>
                                </div>
                            """
                
                productos_html += "</div></div>"
            
            # ANÁLISIS PATRIMONIAL
            if "Saldo Activos" in df.columns and "Saldo Pasivos" in df.columns:
                total_activos = df["Saldo Activos"].sum()
                total_pasivos = df["Saldo Pasivos"].sum()
                patrimonio = total_activos - total_pasivos
                
                patrimonial_html = f"""
                <div class='section'>
                    <h2>💰 Análisis Patrimonial</h2>
                    <p><strong>Ecuación:</strong> ACTIVOS - PASIVOS = PATRIMONIO NETO</p>
                    
                    <div class='metrics-grid'>
                        <div class='metric-card' style='border-left-color: #2ecc71;'>
                            <h3>Total ACTIVOS</h3>
                            <div class='metric-value'>{fmt_money(total_activos)}</div>
                            <div class='metric-unit'>Lo que clientes deben al banco</div>
                        </div>
                        <div class='metric-card' style='border-left-color: #e74c3c;'>
                            <h3>Total PASIVOS</h3>
                            <div class='metric-value'>{fmt_money(total_pasivos)}</div>
                            <div class='metric-unit'>Lo que clientes depositan</div>
                        </div>
                        <div class='metric-card' style='border-left-color: #3498db;'>
                            <h3>PATRIMONIO NETO</h3>
                            <div class='metric-value'>{fmt_money(patrimonio)}</div>
                            <div class='metric-unit'>Balance final</div>
                        </div>
                    </div>
                </div>
                """
            
            # ANÁLISIS GEOGRÁFICO
            if "País" in df.columns:
                paises = df["País"].value_counts().head(10)
                geografico_html = "<div class='section'><h2>🌎 Distribución Geográfica</h2>"
                geografico_html += "<h3>Top 10 Países por Cantidad de Clientes</h3>"
                geografico_html += "<div class='table-wrapper'><table><thead><tr><th>País</th><th>Clientes</th><th>%</th></tr></thead><tbody>"
                
                for pais, cantidad in paises.items():
                    porcentaje = (cantidad / len(df)) * 100
                    geografico_html += f"<tr><td><strong>{pais}</strong></td><td>{cantidad}</td><td>{porcentaje:.1f}%</td></tr>"
                
                geografico_html += "</tbody></table></div></div>"
    
    # Tipos de variables
    roles_count = {}
    for col in columns:
        role = col.get('role', 'unknown')
        roles_count[role] = roles_count.get(role, 0) + 1
    
    # HTML
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte EDA Completo - {filename}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        header {{
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            text-align: center;
        }}
        
        header h1 {{
            color: #667eea;
            font-size: 3rem;
            margin-bottom: 15px;
        }}
        
        header p {{
            color: #666;
            font-size: 1.2rem;
        }}
        
        .timestamp {{
            color: #999;
            font-size: 1rem;
            margin-top: 15px;
        }}
        
        .section {{
            background: white;
            padding: 35px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        
        .section h2 {{
            color: #667eea;
            font-size: 2rem;
            margin-bottom: 25px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 12px;
        }}
        
        .section h3 {{
            color: #764ba2;
            font-size: 1.5rem;
            margin: 25px 0 15px;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
            margin: 25px 0;
        }}
        
        .metric-card {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 3px 6px rgba(0,0,0,0.1);
            border-left: 5px solid #667eea;
            transition: transform 0.2s;
        }}
        
        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }}
        
        .metric-card h3 {{
            color: #667eea;
            font-size: 0.95rem;
            text-transform: uppercase;
            margin-bottom: 12px;
            letter-spacing: 1.2px;
            font-weight: 600;
        }}
        
        .metric-value {{
            font-size: 2.5rem;
            font-weight: bold;
            color: #333;
            margin: 10px 0;
        }}
        
        .metric-unit {{
            font-size: 0.95rem;
            color: #666;
            margin-top: 8px;
        }}
        
        .table-wrapper {{
            overflow-x: auto;
            margin: 25px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
        }}
        
        table th {{
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            font-size: 1rem;
        }}
        
        table td {{
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
        }}
        
        table tr:hover {{
            background: #f5f7fa;
        }}
        
        table tr:last-child td {{
            border-bottom: none;
        }}
        
        .insight-card {{
            background: #fff8e1;
            border-left: 4px solid #ffa726;
            padding: 20px;
            margin: 15px 0;
            border-radius: 6px;
        }}
        
        .insight-card h4 {{
            color: #e65100;
            margin-bottom: 10px;
            font-size: 1.1rem;
        }}
        
        .insight-card p {{
            color: #555;
            line-height: 1.6;
        }}
        
        .alert {{
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        
        .alert-warning {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            color: #856404;
        }}
        
        .alert-info {{
            background: #d1ecf1;
            border-left: 4px solid #17a2b8;
            color: #0c5460;
        }}
        
        .alert-success {{
            background: #d4edda;
            border-left: 4px solid #28a745;
            color: #155724;
        }}
        
        ul {{
            margin: 15px 0 15px 25px;
        }}
        
        ul li {{
            margin: 8px 0;
            line-height: 1.5;
        }}
        
        footer {{
            text-align: center;
            padding: 30px;
            color: white;
            margin-top: 40px;
            font-size: 1rem;
        }}
        
        .badge {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.85rem;
            font-weight: 600;
            margin: 3px;
        }}
        
        .badge-numeric {{
            background: #e3f2fd;
            color: #1976d2;
        }}
        
        .badge-categorical {{
            background: #f3e5f5;
            color: #7b1fa2;
        }}
        
        .badge-text {{
            background: #fff3e0;
            color: #e65100;
        }}
        
        .badge-id {{
            background: #e0f2f1;
            color: #00695c;
        }}
        
        @media print {{
            body {{
                background: white;
            }}
            .metric-card:hover {{
                transform: none;
            }}
        }}
        
        @media (max-width: 768px) {{
            .metrics-grid {{
                grid-template-columns: 1fr;
            }}
            header h1 {{
                font-size: 2rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Análisis Exploratorio de Datos (EDA)</h1>
            <p>Reporte Completo del Dashboard</p>
            <div class="timestamp">
                📅 Generado: {datetime.now().strftime("%d de %B, %Y - %H:%M:%S")}
            </div>
        </header>
        
        <!-- RESUMEN EJECUTIVO -->
        <div class="section">
            <h2>📈 Resumen Ejecutivo</h2>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <h3>Total de Registros</h3>
                    <div class="metric-value">{n_rows}</div>
                    <div class="metric-unit">filas procesadas</div>
                </div>
                <div class="metric-card">
                    <h3>Total de Columnas</h3>
                    <div class="metric-value">{n_columns}</div>
                    <div class="metric-unit">características analizadas</div>
                </div>
                <div class="metric-card">
                    <h3>Memoria Utilizada</h3>
                    <div class="metric-value">{memory_str}</div>
                    <div class="metric-unit">espacio en memoria</div>
                </div>
                <div class="metric-card">
                    <h3>Insights Detectados</h3>
                    <div class="metric-value">{len(insights)}</div>
                    <div class="metric-unit">hallazgos automáticos</div>
                </div>
            </div>
        </div>
        
        <!-- ANÁLISIS PATRIMONIAL -->
        {patrimonial_html}
        
        <!-- ANÁLISIS DE PRODUCTOS -->
        {productos_html}
        
        <!-- ANÁLISIS GEOGRÁFICO -->
        {geografico_html}
        
        <!-- CALIDAD DE DATOS -->
        <div class="section">
            <h2>🔍 Análisis de Calidad de Datos</h2>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <h3>Datos Faltantes</h3>
                    <div class="metric-value">{pct_missing}</div>
                    <div class="metric-unit">del total de celdas</div>
                </div>
                <div class="metric-card">
                    <h3>Columnas con Nulos</h3>
                    <div class="metric-value">{cols_with_missing}</div>
                    <div class="metric-unit">de {n_columns} columnas</div>
                </div>
                <div class="metric-card">
                    <h3>Registros Duplicados</h3>
                    <div class="metric-value">{duplicates}</div>
                    <div class="metric-unit">{pct_duplicates} del total</div>
                </div>
            </div>
        </div>
        
        <!-- DICCIONARIO DE DATOS -->
        <div class="section">
            <h2>📚 Diccionario de Datos Completo</h2>
            
            <p style="margin-bottom: 20px;">Información detallada de todas las columnas analizadas:</p>
            
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Nombre</th>
                            <th>Tipo</th>
                            <th>Únicos</th>
                            <th>Nulos</th>
                            <th>Completitud</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    # Agregar todas las columnas
    for idx, col in enumerate(columns, 1):
        name = col.get('name', 'N/A')
        role = col.get('role', 'unknown')
        n_unique = fmt_num(col.get('n_unique', 0))
        n_missing = fmt_num(col.get('n_missing', 0))
        pct_valid = col.get('pct_valid', 100)
        pct_valid_str = f"{pct_valid:.1f}%" if isinstance(pct_valid, (int, float)) else "N/A"
        
        badge_class = 'badge-numeric' if 'numeric' in role else \
                     'badge-categorical' if 'categorical' in role else \
                     'badge-id' if role == 'id' else \
                     'badge-text'
        
        html += f"""
                        <tr>
                            <td>{idx}</td>
                            <td><strong>{name}</strong></td>
                            <td><span class="badge {badge_class}">{role}</span></td>
                            <td>{n_unique}</td>
                            <td>{n_missing}</td>
                            <td>{pct_valid_str}</td>
                        </tr>
        """
    
    html += """
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- INSIGHTS -->
        <div class="section">
            <h2>💡 Hallazgos Automáticos e Insights</h2>
    """
    
    if insights:
        for insight in insights[:15]:
            title = insight.get('title', 'Sin título')
            description = insight.get('description', '')
            html += f"""
            <div class="insight-card">
                <h4>🔍 {title}</h4>
                <p>{description}</p>
            </div>
            """
    else:
        html += '<div class="alert alert-info">No se detectaron insights en este análisis.</div>'
    
    html += """
        </div>
        
        <footer>
            <p><strong>EDA Dashboard v1.0</strong> | FastAPI + Streamlit + Pandas</p>
            <p>© 2026 EDA Dashboard. Reporte generado automáticamente.</p>
            <p style="margin-top: 10px; font-size: 0.9rem;">
                Archivo HTML independiente para compartir sin dependencias.
            </p>
        </footer>
    </div>
</body>
</html>
    """
    
    return html


def save_html_report(profile: Dict[str, Any], output_dir: str = "reports") -> str:
    """Guardar reporte HTML en disco."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Analisis_EDA_{timestamp}"
    html_content = generate_html_report(profile, filename)
    output_path = Path(output_dir) / f"{filename}.html"
    output_path.write_text(html_content, encoding="utf-8")
    return str(output_path)
