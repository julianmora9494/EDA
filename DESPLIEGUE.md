# 🚀 Guía Completa de Despliegue - Dashboard EDA

Guía paso a paso para desplegar el Dashboard EDA tanto en **local** como en la **nube** (Streamlit Cloud + Render).

---

## 📋 Tabla de Contenidos

1. [Despliegue Local](#-despliegue-local)
2. [Despliegue en la Nube](#-despliegue-en-la-nube)
3. [Configuración de Secrets](#-configuración-de-secrets)
4. [Troubleshooting](#-troubleshooting)
5. [Mantenimiento](#-mantenimiento)

---

## 💻 Despliegue Local

### Pre-requisitos

- **Python 3.9+** instalado
- **Git** instalado
- **PowerShell** o **Terminal**
- **500 MB** de espacio libre

### Paso 1: Clonar el Repositorio

```bash
# Opción A: HTTPS
git clone https://github.com/julianmora9494/EDA.git

# Opción B: SSH
git clone git@github.com:julianmora9494/EDA.git

# Entrar al directorio
cd EDA_Dashboard
```

### Paso 2: Crear Entorno Virtual

```bash
# Crear entorno virtual
python -m venv venv_eda

# Verificar que se creó
ls venv_eda  # Debería mostrar: Scripts, Lib, Include, etc.
```

### Paso 3: Activar Entorno Virtual

**Windows (PowerShell)**:
```powershell
.\venv_eda\Scripts\Activate.ps1
```

**Windows (CMD)**:
```cmd
.\venv_eda\Scripts\activate.bat
```

**Linux/Mac**:
```bash
source venv_eda/bin/activate
```

**Verificar activación**: El prompt debería mostrar `(venv_eda)` al inicio.

### Paso 4: Instalar Dependencias

```bash
# Instalar todas las dependencias
pip install -r requirements.txt

# Verificar instalación
pip list | grep streamlit  # Debería mostrar streamlit 1.31.0
```

### Paso 5: Ejecutar Backend (FastAPI)

**Abrir Terminal 1**:
```bash
cd EDA_Dashboard
.\venv_eda\Scripts\Activate.ps1
python -m uvicorn api.main:app --port 8000 --reload
```

**Verificar**: Deberías ver:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**Probar**: Abrir http://localhost:8000/docs (Swagger UI)

### Paso 6: Ejecutar Frontend (Streamlit)

**Abrir Terminal 2** (nueva ventana):
```bash
cd EDA_Dashboard
.\venv_eda\Scripts\Activate.ps1
python -m streamlit run ui/app.py --server.port 8503
```

**Verificar**: Deberías ver:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8503
```

**Probar**: Abrir http://localhost:8503

### Paso 7: Usar el Dashboard

1. El navegador debería abrirse automáticamente
2. Cargar un archivo Excel o CSV
3. Explorar las diferentes pestañas
4. Exportar resultados si necesitas

---

## ☁️ Despliegue en la Nube

### Arquitectura Cloud

```
┌─────────────────┐
│  Streamlit Cloud│  ← Frontend (UI)
│  (GRATIS)       │
└────────┬────────┘
         │ API calls
         ↓
┌─────────────────┐
│     Render      │  ← Backend (API)
│  (GRATIS)       │
└─────────────────┘
```

---

## 🎯 Parte 1: Desplegar Backend en Render

### Paso 1.1: Crear Cuenta en Render

1. Ir a: https://render.com/
2. Clic en **"Get Started"**
3. **"Sign up with GitHub"**
4. Autorizar Render a acceder a tu GitHub

### Paso 1.2: Crear Web Service

1. En el Dashboard de Render, clic en **"New +"** → **"Web Service"**

2. **Conectar repositorio**:
   - Buscar: `EDA` o `EDA_Dashboard`
   - Clic en **"Connect"**

3. **Configurar el servicio**:

| Campo | Valor |
|-------|-------|
| **Name** | `eda-dashboard-api` |
| **Region** | `Oregon (US West)` |
| **Branch** | `main` |
| **Root Directory** | (dejar vacío) |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements-backend.txt` |
| **Start Command** | `uvicorn api.main:app --host 0.0.0.0 --port $PORT` |

4. **Instance Type**: Seleccionar **"Free"**

5. **Environment Variables** (opcional):
   - Clic en "Add Environment Variable"
   - `PYTHON_VERSION` = `3.11.0`

6. **Clic en "Create Web Service"**

### Paso 1.3: Esperar Despliegue

- Verás logs en tiempo real
- Espera 5-10 minutos
- Al finalizar verás: **"Your service is live at https://..."**

### Paso 1.4: Copiar URL del Backend

Tu API estará en algo como:
```
https://eda-dashboard-api.onrender.com
```

**COPIAR ESTA URL** (la necesitarás en el siguiente paso)

### Paso 1.5: Verificar que Funciona

Abrir en navegador:
```
https://eda-dashboard-api.onrender.com/health
```

Debería mostrar:
```json
{"status": "healthy"}
```

✅ **Backend desplegado exitosamente**

---

## 🎨 Parte 2: Desplegar Frontend en Streamlit Cloud

### Paso 2.1: Crear Cuenta en Streamlit Cloud

1. Ir a: https://share.streamlit.io/
2. Clic en **"Sign up"** o **"Continue with GitHub"**
3. Autorizar Streamlit a acceder a tu GitHub
4. Completar perfil (nombre, email)

### Paso 2.2: Crear Nueva App

1. Clic en **"New app"** (botón azul arriba a la derecha)

2. **Configurar el deployment**:

| Campo | Valor |
|-------|-------|
| **Repository** | `julianmora9494/EDA` (o tu usuario) |
| **Branch** | `main` |
| **Main file path** | `ui/app.py` |

3. **App URL** (personalizar):
   - **Subdomain**: `eda-bancario` (o el que prefieras)
   - **Domain**: `streamlit.app`
   - Tu URL será: `https://eda-bancario.streamlit.app`

4. **Advanced settings** (clic para expandir):
   - **Python version**: `3.11`

5. **Clic en "Deploy!"**

### Paso 2.3: Esperar Despliegue

- Verás logs en tiempo real
- Espera 3-5 minutos
- Al finalizar verás: **"Your app is live!"**

### Paso 2.4: Configurar Secrets (IMPORTANTE)

**El dashboard NO funcionará sin este paso**

1. En Streamlit Cloud, clic en tu app
2. Clic en el menú **⋮** (tres puntos) → **"Settings"**
3. En el menú lateral, clic en **"Secrets"**
4. Pegar este código (reemplazar con TU URL de Render):

```toml
API_URL = "https://eda-dashboard-api.onrender.com"
```

5. Clic en **"Save"**
6. Clic en **"Reboot app"** (para que tome los cambios)

### Paso 2.5: Verificar que Funciona

1. Abrir tu dashboard: `https://eda-bancario.streamlit.app`
2. Esperar 30-60 segundos (el backend en Render puede estar "dormido")
3. Debería mostrar: "✅ Conectado al servidor correctamente"
4. Cargar un archivo de prueba
5. Explorar las pestañas

✅ **Frontend desplegado exitosamente**

---

## 🔐 Configuración de Secrets

### ¿Qué son los Secrets?

Los Secrets son variables de entorno seguras que Streamlit Cloud usa para guardar información sensible (como URLs de APIs, passwords, etc.) sin exponerla en el código.

### Cómo Configurar Secrets

**Método 1: Desde la UI de Streamlit Cloud** (recomendado)

1. Ir a https://share.streamlit.io/
2. Clic en tu app → Settings → Secrets
3. Pegar:
```toml
API_URL = "https://tu-api.onrender.com"
```
4. Save → Reboot app

**Método 2: Archivo Local (solo para testing)**

Crear `.streamlit/secrets.toml` (git-ignored):
```toml
API_URL = "http://localhost:8000"
```

---

## 🐛 Troubleshooting

### Problema 1: "Oh no." en Streamlit Cloud

**Causa**: Error en el código o imports incorrectos

**Solución**:
1. Ir a Settings → Logs
2. Revisar el error específico
3. Si dice "ModuleNotFoundError", agregar el módulo a `requirements.txt`
4. Hacer `git push` (se redespliega automáticamente)

---

### Problema 2: "No se puede conectar con la API"

**Causa**: Backend en Render está "dormido" (plan gratis)

**Solución**:
1. Esperar 30-60 segundos
2. Recargar la página (F5)
3. Si persiste, verificar que la URL en Secrets sea correcta

---

### Problema 3: Backend en Render falla al desplegar

**Causa**: Error en `requirements-backend.txt` o comando de inicio

**Solución**:
1. Revisar logs de build en Render
2. Verificar que `requirements-backend.txt` exista
3. Verificar Start Command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

---

### Problema 4: Imports fallan en Streamlit Cloud

**Causa**: Imports absolutos no funcionan en Cloud

**Solución**: Ya está corregido con imports relativos + fallback:
```python
try:
    from components.charts import plot_chart
except ImportError:
    from ui.components.charts import plot_chart
```

---

### Problema 5: "Address already in use" (local)

**Causa**: Puerto 8000 o 8503 ya está ocupado

**Solución**:
```bash
# Matar proceso en puerto 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# O usar otro puerto
python -m uvicorn api.main:app --port 8001
python -m streamlit run ui/app.py --server.port 8504
```

---

## 🔄 Mantenimiento

### Actualizar el Dashboard

**Local**:
```bash
git pull origin main
pip install -r requirements.txt --upgrade
# Reiniciar backend y frontend
```

**Cloud** (automático):
```bash
git add .
git commit -m "Actualización"
git push origin main
# Streamlit Cloud y Render se actualizan solos en 2-5 min
```

### Monitorear Logs

**Streamlit Cloud**:
- Settings → Logs
- Ver errores en tiempo real

**Render**:
- Dashboard → Tu servicio → Logs
- Ver requests y errores

### Reiniciar Servicios

**Streamlit Cloud**:
- Settings → Reboot app

**Render**:
- Manual Deployment → Deploy latest commit

---

## 💰 Costos

| Servicio | Plan | Costo | Limitaciones |
|----------|------|-------|--------------|
| **Streamlit Cloud** | Community | **$0/mes** | 1 app pública, 1GB RAM |
| **Render** | Free | **$0/mes** | Se duerme después de 15 min sin uso |
| **GitHub** | Free | **$0/mes** | Repositorios públicos ilimitados |
| **TOTAL** | | **$0/mes** | |

### Upgrades Opcionales

| Servicio | Plan | Costo | Beneficios |
|----------|------|-------|------------|
| Streamlit Cloud | Pro | $20/mes | 3 apps privadas, 2GB RAM |
| Render | Starter | $7/mes | Sin sleep, siempre activo |

---

## 📊 Comparación Local vs Cloud

| Aspecto | Local | Cloud |
|---------|-------|-------|
| **Velocidad** | ⚡ Muy rápido | 🐢 Más lento (plan gratis) |
| **Acceso** | 🔒 Solo tu PC | 🌐 Público (compartible) |
| **Disponibilidad** | ⏰ Solo cuando está prendida tu PC | ✅ 24/7 |
| **Costo** | $0 | $0 (plan gratis) |
| **Actualizaciones** | ⚙️ Manual | 🔄 Automático (git push) |
| **Debugging** | ✅ Fácil | ❌ Más difícil |

---

## 🎯 Recomendaciones

### Para Desarrollo
✅ Usar **local** (más rápido, fácil de debuggear)

### Para Demos/Presentaciones
✅ Usar **Streamlit Cloud** (compartible, profesional)

### Para Producción con Datos Sensibles
✅ Considerar **AWS/Azure/GCP** con autenticación robusta

---

## 📞 Soporte

**Documentación Oficial**:
- Streamlit: https://docs.streamlit.io/
- Render: https://render.com/docs
- FastAPI: https://fastapi.tiangolo.com/

**Problemas del Proyecto**:
- Crear issue en GitHub
- Contactar al equipo de Data Science

---

## ✅ Checklist de Despliegue

### Local
- [ ] Python 3.9+ instalado
- [ ] Repositorio clonado
- [ ] Entorno virtual creado y activado
- [ ] Dependencias instaladas
- [ ] Backend corriendo en puerto 8000
- [ ] Frontend corriendo en puerto 8503
- [ ] Dashboard accesible en http://localhost:8503

### Cloud
- [ ] Cuenta en Render creada
- [ ] Backend desplegado en Render
- [ ] URL del backend copiada
- [ ] Cuenta en Streamlit Cloud creada
- [ ] Frontend desplegado en Streamlit Cloud
- [ ] Secrets configurados con URL del backend
- [ ] App reiniciada después de configurar secrets
- [ ] Dashboard accesible públicamente
- [ ] Prueba de carga de archivo exitosa

---

## 🎉 ¡Listo!

Tu dashboard está desplegado y funcionando. Ahora puedes:
- ✅ Compartir el link por correo/Teams/Slack
- ✅ Cargar tus propios datos
- ✅ Generar reportes ejecutivos
- ✅ Tomar decisiones basadas en datos

---

**Última actualización**: Febrero 2026  
**Versión**: 1.0.0  
**Autor**: Equipo de Data Science
