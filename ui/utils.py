"""
Utilidades para el frontend de Streamlit.
"""
from datetime import datetime
from typing import Dict, Any


def generate_simple_html_report(profile: Dict[str, Any], filename: str = "reporte") -> str:
    """
    Generar reporte HTML simple sin dependencias del backend.
    """
    overview = profile.get("overview", {})
    quality = profile.get("quality", {})
    columns = profile.get("columns", [])
    insights = profile.get("insights", [])
    
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
    
    n_rows = fmt_num(overview.get("n_rows", 0))
    n_columns = fmt_num(overview.get("n_columns", 0))
    memory_mb = overview.get("memory_mb", 0)
    memory_str = f"{memory_mb:.2f} MB" if isinstance(memory_mb, (int, float)) else "N/A"
    
    missing_info = quality.get("missing", {})
    pct_missing = fmt_pct(missing_info.get("pct_missing_global", 0))
    cols_with_missing = fmt_num(missing_info.get("columns_with_missing", 0))
    duplicates = fmt_num(overview.get("n_duplicate_rows", 0))
    pct_duplicates = fmt_pct(overview.get("pct_duplicate_rows", 0))
    
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte EDA - {filename}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
            padding: 20px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        header {{
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            text-align: center;
        }}
        header h1 {{ color: #667eea; font-size: 3rem; margin-bottom: 15px; }}
        header p {{ color: #666; font-size: 1.2rem; }}
        .timestamp {{ color: #999; font-size: 1rem; margin-top: 15px; }}
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
        }}
        .metric-card h3 {{
            color: #667eea;
            font-size: 0.95rem;
            text-transform: uppercase;
            margin-bottom: 12px;
        }}
        .metric-value {{
            font-size: 2.5rem;
            font-weight: bold;
            color: #333;
            margin: 10px 0;
        }}
        .metric-unit {{ font-size: 0.95rem; color: #666; margin-top: 8px; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            margin: 20px 0;
        }}
        table th {{
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
        }}
        table td {{ padding: 12px 15px; border-bottom: 1px solid #eee; }}
        table tr:hover {{ background: #f5f7fa; }}
        footer {{
            text-align: center;
            padding: 30px;
            color: white;
            margin-top: 40px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Análisis Exploratorio de Datos</h1>
            <p>Reporte Completo del Dashboard</p>
            <div class="timestamp">
                📅 Generado: {datetime.now().strftime("%d/%m/%Y - %H:%M:%S")}
            </div>
        </header>
        
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
        
        <div class="section">
            <h2>🔍 Calidad de Datos</h2>
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
        
        <div class="section">
            <h2>📚 Diccionario de Datos</h2>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Nombre</th>
                        <th>Tipo</th>
                        <th>Valores Únicos</th>
                        <th>Nulos</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for idx, col in enumerate(columns[:50], 1):  # Limitar a 50 columnas
        name = col.get('name', 'N/A')
        role = col.get('role', 'unknown')
        n_unique = fmt_num(col.get('n_unique', 0))
        n_missing = fmt_num(col.get('n_missing', 0))
        
        html += f"""
                    <tr>
                        <td>{idx}</td>
                        <td><strong>{name}</strong></td>
                        <td>{role}</td>
                        <td>{n_unique}</td>
                        <td>{n_missing}</td>
                    </tr>
        """
    
    html += """
                </tbody>
            </table>
        </div>
        
        <footer>
            <p><strong>EDA Dashboard</strong> | Generado automáticamente</p>
            <p>© 2026 EDA Dashboard</p>
        </footer>
    </div>
</body>
</html>
    """
    
    return html
