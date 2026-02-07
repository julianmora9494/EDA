# 📊 Dashboard EDA - Análisis Exploratorio de Datos Bancarios

Dashboard interactivo profesional para análisis exploratorio de datos bancarios, construido con **Streamlit** (frontend) y **FastAPI** (backend).

---

## 🎯 Descripción

Sistema completo de análisis exploratorio de datos que permite:
- Cargar archivos Excel o CSV
- Análisis automático de calidad de datos
- Visualizaciones interactivas de saldos, productos y geografía
- Conclusiones ejecutivas automáticas
- Exportación de reportes

---

## ✨ Características Principales

### 📈 Análisis de Saldos
- Distribución de Activos y Pasivos
- Balance General consolidado
- Análisis por productos (CA, CC, DP, TC, PR)
- Estadísticas descriptivas completas

### 🛍️ Análisis de Productos
- Profundidad de relación (Mono/Bi/Multi-producto)
- Tenencia y penetración por producto
- Oportunidades de Cross-Sell por segmento
- Análisis por ciclo de vida (edad)

### 🗺️ Análisis Geográfico
- Mapa interactivo choropleth por país
- Distribución de clientes y saldos
- Top 15 países con mayor concentración

### 🔍 Calidad de Datos
- Detección de valores nulos
- Identificación de duplicados
- Análisis de cardinalidad
- Insights automáticos

### 📊 Conclusiones Ejecutivas
- Concentración de saldos (top 10%, top 1%)
- Profundidad de productos
- Segmentación por Banca
- Distribución por edad
- Recomendaciones estratégicas

### 💾 Exportación
- Descargar perfil completo (JSON)
- Exportar datos procesados (CSV)
- Reportes ejecutivos (HTML)

---

## 🏗️ Arquitectura

```
EDA_Dashboard/
│
├── api/                      # Backend FastAPI
│   ├── main.py              # Aplicación principal
│   ├── routes/              # Endpoints REST
│   │   ├── upload.py       # Carga de archivos
│   │   ├── profile.py      # Perfilado de datos
│   │   ├── data.py         # Recuperación de datos
│   │   └── export.py       # Exportación
│   └── services/            # Lógica de negocio
│       ├── profiler.py     # Motor de análisis
│       └── file_handler.py # Manejo de archivos
│
├── ui/                      # Frontend Streamlit
│   ├── app.py              # Página principal
│   ├── components/         # Componentes reutilizables
│   └── pages/              # Páginas del dashboard
│       ├── 1_Resumen.py
│       ├── 2_Calidad.py
│       ├── 3_Analisis_Saldos.py
│       ├── 4_Analisis_Productos.py
│       ├── 5_Analisis_Geografico.py
│       ├── 6_Relaciones.py
│       ├── 7_Conclusiones.py
│       └── 8_Descargas.py
│
├── eda/                     # Motor de análisis
│   ├── typing.py           # Inferencia de tipos
│   ├── quality.py          # Calidad de datos
│   ├── associations.py     # Correlaciones
│   └── profiling.py        # Perfilado completo
│
├── data/                    # Datos cargados (git-ignored)
├── reports/                 # Reportes exportados
│
├── requirements.txt         # Dependencias frontend
├── requirements-backend.txt # Dependencias backend
├── .streamlit/config.toml  # Configuración Streamlit
│
├── README.md               # Este archivo
└── DESPLIEGUE.md          # Guía de despliegue
```

---

## 🚀 Inicio Rápido

### Requisitos Previos
- Python 3.9 o superior
- pip (gestor de paquetes)
- ~500 MB de espacio en disco

### Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/julianmora9494/EDA.git
cd EDA_Dashboard

# 2. Crear entorno virtual
python -m venv venv_eda

# 3. Activar entorno virtual
# Windows:
.\venv_eda\Scripts\Activate.ps1
# Linux/Mac:
source venv_eda/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt
```

### Ejecución Local

**Terminal 1 - Backend (FastAPI)**:
```bash
cd EDA_Dashboard
.\venv_eda\Scripts\Activate.ps1
python -m uvicorn api.main:app --port 8000 --reload
```

**Terminal 2 - Frontend (Streamlit)**:
```bash
cd EDA_Dashboard
.\venv_eda\Scripts\Activate.ps1
python -m streamlit run ui/app.py --server.port 8503
```

**Abrir navegador**: http://localhost:8503

---

## 🌐 Despliegue en la Nube

Ver **[DESPLIEGUE.md](DESPLIEGUE.md)** para instrucciones detalladas de cómo desplegar en:
- **Streamlit Cloud** (frontend - gratis)
- **Render** (backend - gratis)

**Dashboard público**: https://at34w5x8lgjfwtq2odczbm.streamlit.app

---

## 📚 Tecnologías Utilizadas

### Backend
- **FastAPI** 0.115.0 - API REST de alto rendimiento
- **Pandas** 2.2.0 - Procesamiento de datos
- **NumPy** 1.26.4 - Computación numérica
- **SciPy** 1.12.0 - Estadísticas avanzadas

### Frontend
- **Streamlit** 1.31.0 - Framework de dashboards
- **Plotly** 5.18.0 - Visualizaciones interactivas
- **Matplotlib** 3.8.2 - Gráficos estáticos

---

## 📖 Uso del Dashboard

### 1. Cargar Datos
- Soporta archivos: CSV, Excel (.xlsx, .xls)
- Tamaño máximo: 200 MB
- Encoding: UTF-8 recomendado

### 2. Navegación
- **Resumen**: Overview general del dataset
- **Calidad**: Missing values, duplicados, insights
- **Análisis de Saldos**: Activos, Pasivos, Balance
- **Análisis de Productos**: Tenencia, Cross-Sell, Edad
- **Análisis Geográfico**: Mapa interactivo por país
- **Relaciones**: Correlaciones y asociaciones
- **Conclusiones**: Hallazgos clave y recomendaciones
- **Descargas**: Exportar resultados

### 3. Interpretación
Cada sección incluye:
- 📚 Explicación de qué mide
- 💡 Interpretación de resultados
- 🎯 Recomendaciones accionables

---

## 🔧 Configuración

### Variables de Entorno

**Local** (desarrollo):
- No requiere configuración adicional
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:8503`

**Producción** (Streamlit Cloud):
- Configurar en Settings → Secrets:
```toml
API_URL = "https://eda-dashboard-api.onrender.com"
```

---

## 📊 Reglas de Cálculo

### Contabilidad Bancaria
- **ACTIVOS**: Lo que clientes deben al banco (TC, PR)
- **PASIVOS**: Lo que clientes depositan en el banco (CA, CC, DP)
- **Total Balance**: ACTIVOS + PASIVOS (suma simple)

### Estadísticas
- **Suma**: Incluye TODOS los valores (positivos, negativos, ceros)
- **Promedio**: Calculado sobre TODOS los registros
- **N° Clientes**: Cuenta solo registros con saldo > 0

---

## 🐛 Solución de Problemas

### Error: "No se puede conectar con la API"
**Causa**: El backend no está corriendo
**Solución**: Verificar que FastAPI esté ejecutándose en puerto 8000

### Error: "ModuleNotFoundError"
**Causa**: Dependencias no instaladas
**Solución**: 
```bash
pip install -r requirements.txt --upgrade
```

### Error: Archivo no se carga
**Causa**: Encoding incorrecto
**Solución**: Guardar CSV como UTF-8 con BOM

---

## 📂 Datos de Ejemplo

El proyecto incluye:
- `base_panama.xlsx` - Datos originales
- `base_panama_mejorada.csv` - Datos procesados

**Estructura esperada**:
- Columnas de saldos (numéricos)
- Columnas de productos (numéricos o categóricos)
- Información demográfica (edad, país, banca)

---

## 🤝 Contribuciones

Para contribuir:
1. Fork del repositorio
2. Crear rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit: `git commit -m "Agregar nueva funcionalidad"`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

---

## 📄 Licencia

Proyecto privado - Uso interno.

---

## 📞 Soporte

Para preguntas o problemas:
- Crear issue en GitHub
- Contactar al equipo de Data Science

---

## 🎯 Roadmap Futuro

- [ ] Autenticación de usuarios
- [ ] Múltiples datasets simultáneos
- [ ] Comparación temporal (mes a mes)
- [ ] Modelos predictivos (churn, LTV)
- [ ] Exportación a PowerPoint
- [ ] Integración con bases de datos SQL

---

## 📈 Versión

**Versión actual**: 1.0.0  
**Última actualización**: Febrero 2026  
**Estado**: ✅ Producción

---

## 🙏 Agradecimientos

Desarrollado con ❤️ por el equipo de Data Science.

Tecnologías: Streamlit, FastAPI, Plotly, Pandas, NumPy, SciPy.
