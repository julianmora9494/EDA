# 📊 EDA Dashboard - Análisis Exploratorio de Datos

Dashboard profesional para análisis exploratorio de datos bancarios, construido con **Streamlit** y **FastAPI**.

## 🚀 Inicio Rápido

### Requisitos
- Python 3.9+
- pip (gestor de paquetes)
- ~500 MB de espacio en disco

### Instalación (Primera vez)

```bash
# 1. Crear entorno virtual
python -m venv venv_eda

# 2. Activar entorno virtual
.\venv_eda\Scripts\Activate.ps1  # Windows
source venv_eda/bin/activate      # Linux/Mac

# 3. Instalar dependencias
python -m pip install -r requirements.txt
```

### Ejecutar Dashboard

**Doble clic en:** `iniciar_dashboard.bat`

Se abrirán automáticamente:
- Backend (FastAPI - Puerto 8000)
- Frontend (Streamlit - Puerto 8503)
- Tu navegador

## 📊 Características

- **Análisis Patrimonial**: Balance general e indicadores financieros
- **Análisis de Productos**: Penetración y cross-sell
- **Análisis Geográfico**: Mapas interactivos
- **Análisis de Calidad**: Detección de nulos y duplicados
- **Conclusiones Automáticas**: Hallazgos e insights
- **Exportación**: Reportes en HTML, Excel, CSV

## 🏗️ Arquitectura

```
EDA_Dashboard/
├── api/              # Backend FastAPI
├── ui/               # Frontend Streamlit
├── eda/              # Motor de análisis
├── data/             # Datos procesados
├── reports/          # Reportes generados
├── requirements.txt  # Dependencias
└── iniciar_dashboard.bat
```

## 📂 Archivos Principales

- **iniciar_dashboard.bat** - Ejecutable para iniciar (doble clic)
- **README.md** - Este archivo
- **DESPLEGAR.md** - Instrucciones de despliegue
- **requirements.txt** - Dependencias del proyecto

## 🔗 URLs

**Local:**
- **Dashboard**: http://localhost:8503
- **API Docs**: http://localhost:8000/docs

**Producción (Streamlit Cloud):**
- Dashboard: https://cmlrxnzf5swzomwluzgibh.streamlit.app
- API Backend: https://eda-dashboard-api.onrender.com

## Troubleshooting

### Error: "No se puede conectar con la API"
1. Espera 10 segundos desde que abriste el dashboard
2. Recarga la página (F5)
3. Si persiste, cierra ambas ventanas y vuelve a ejecutar iniciar_dashboard.bat

### Error: "Python no está instalado"
Descarga Python desde: https://www.python.org/downloads/
Asegúrate de marcar "Add Python to PATH" en la instalación

### Error: Módulo no encontrado
```powershell
# En PowerShell:
.\venv_eda\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## 📄 Licencia

Proyecto privado - Uso interno.
