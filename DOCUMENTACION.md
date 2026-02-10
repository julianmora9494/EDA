# 📚 Documentación Completa - Dashboard EDA

Guía completa de instalación, despliegue y uso del Dashboard de Análisis Exploratorio de Datos.

---

## 📋 Contenido

1. [Instalación Local](#-instalación-local)
2. [Despliegue en la Nube](#-despliegue-en-la-nube)
3. [Guía de Uso](#-guía-de-uso)
4. [Arquitectura](#-arquitectura)
5. [Troubleshooting](#-troubleshooting)

---

## 💻 Instalación Local

### Pre-requisitos
- Python 3.9+
- Git
- 500 MB de espacio

### Paso 1: Clonar Repositorio
```bash
git clone https://github.com/julianmora9494/EDA.git
cd EDA_Dashboard
```

### Paso 2: Crear Entorno Virtual
```bash
python -m venv venv_eda
```

### Paso 3: Activar Entorno
**Windows**:
```powershell
.\venv_eda\Scripts\Activate.ps1
```

**Linux/Mac**:
```bash
source venv_eda/bin/activate
```

### Paso 4: Instalar Dependencias
```bash
pip install -r requirements.txt
```

### Paso 5: Ejecutar Backend
**Terminal 1**:
```bash
python -m uvicorn api.main:app --port 8000
```

### Paso 6: Ejecutar Frontend
**Terminal 2**:
```bash
python -m streamlit run ui/app.py --server.port 8503
```

### Paso 7: Abrir Dashboard
Ir a: http://localhost:8503

---

## ☁️ Despliegue en la Nube

### Arquitectura Cloud
- **Frontend**: Streamlit Cloud (gratis)
- **Backend**: Render (gratis)

### Parte 1: Desplegar Backend en Render

1. **Crear cuenta**: https://render.com/
2. **New Web Service** → Conectar GitHub
3. **Configurar**:
   - Name: `eda-dashboard-api`
   - Build: `pip install -r requirements-backend.txt`
   - Start: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
   - Instance: Free
4. **Deploy** → Copiar URL

### Parte 2: Desplegar Frontend en Streamlit Cloud

1. **Crear cuenta**: https://share.streamlit.io/
2. **New app**
3. **Configurar**:
   - Repository: `julianmora9494/EDA`
   - Branch: `main`
   - Main file: `ui/app.py`
4. **Settings → Secrets**:
```toml
API_URL = "https://tu-api.onrender.com"
```
5. **Save → Reboot**

---

## 📖 Guía de Uso

### Cargar Datos

**Opción 1: Datos Demo**
1. Clic en "Cargar Datos Demo"
2. Esperar carga automática
3. Explorar pestañas

**Opción 2: Tus Datos**
1. Clic en "Browse files"
2. Seleccionar CSV o Excel
3. Clic en "Analizar Datos"

### Navegación

#### 1. Resumen
- Overview general
- Tipos de datos
- Estadísticas básicas

#### 2. Calidad
- Valores nulos
- Duplicados
- Insights automáticos

#### 3. Análisis de Saldos
- Activos y Pasivos
- Balance General
- Por producto

#### 4. Análisis de Productos
- Tenencia
- Cross-Sell
- Segmentación

#### 5. Análisis Geográfico
- Mapa interactivo
- Distribución por país

#### 6. Relaciones
- Correlaciones
- Asociaciones

#### 7. Conclusiones
- Hallazgos clave
- Recomendaciones

#### 8. Descargas
- Exportar resultados

---

## 🏗️ Arquitectura

```
EDA_Dashboard/
├── api/              # Backend FastAPI
│   ├── main.py
│   ├── routes/
│   └── services/
├── ui/               # Frontend Streamlit
│   ├── app.py
│   ├── pages/
│   └── components/
├── eda/              # Motor análisis
│   ├── typing.py
│   ├── quality.py
│   └── profiling.py
└── requirements.txt
```

### Tecnologías
- **Backend**: FastAPI, Pandas, NumPy
- **Frontend**: Streamlit, Plotly
- **Deploy**: Render, Streamlit Cloud

---

## 🐛 Troubleshooting

### Error: "No se puede conectar con la API"
**Solución**: Esperar 30s (backend despertando)

### Error: "ModuleNotFoundError"
**Solución**: `pip install -r requirements.txt --upgrade`

### Error: Puerto ocupado
**Solución**: Usar otro puerto
```bash
python -m streamlit run ui/app.py --server.port 8504
```

### Error: Archivo no carga
**Solución**: Verificar encoding UTF-8

---

## 📊 Reglas de Cálculo

### Contabilidad
- **ACTIVOS**: TC, PR (lo que deben)
- **PASIVOS**: CA, CC, DP (lo que depositan)
- **Total**: ACTIVOS + PASIVOS

### Estadísticas
- **Suma**: Todos los valores
- **Promedio**: Todos los registros
- **N° Clientes**: Solo > 0

---

## 🔄 Actualización

### Local
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

### Cloud
```bash
git push origin main
# Auto-deploy en 2-3 min
```

---

## 💰 Costos

| Servicio | Plan | Costo |
|----------|------|-------|
| Streamlit Cloud | Community | $0 |
| Render | Free | $0 |
| **TOTAL** | | **$0/mes** |

---

## 📞 Soporte

- **GitHub**: Issues
- **Docs**: Este archivo
- **Demo**: https://at34w5x8lgjfwtq2odczbm.streamlit.app

---

**Última actualización**: Febrero 2026  
**Versión**: 1.0.0
