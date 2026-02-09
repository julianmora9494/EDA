# 🚀 Guía Completa de Despliegue - EDA Dashboard

Esta guía te llevará paso a paso para publicar tu dashboard y compartirlo por correo.

---

## 📋 Resumen

Vamos a desplegar:
1. **Backend (API)** en **Render** (gratis)
2. **Frontend (Dashboard)** en **Streamlit Cloud** (gratis)

**Tiempo estimado**: 15-20 minutos

---

## ✅ Pre-requisitos

- [x] Código subido a GitHub
- [x] Cuenta de GitHub activa
- [ ] Cuenta en Streamlit Cloud (se crea en el paso 1)
- [ ] Cuenta en Render (se crea en el paso 2)

---

## 🎯 PASO 1: Desplegar Frontend en Streamlit Cloud

### 1.1 Crear cuenta en Streamlit Cloud

1. **Ir a**: https://share.streamlit.io/
2. **Hacer clic en** "Sign up" o "Continue with GitHub"
3. **Autorizar** Streamlit a acceder a tu GitHub
4. **Completar perfil** (nombre, email)

### 1.2 Desplegar la aplicación

1. **Hacer clic en** "New app" (botón azul arriba a la derecha)

2. **Configurar el deployment**:
   ```
   Repository: jfelipemora/EDA_Dashboard
   Branch: main
   Main file path: ui/app.py
   ```

3. **App URL** (personalizar):
   ```
   Subdomain: eda-bancario-panama
   Domain: streamlit.app
   ```
   Tu URL será: `https://eda-bancario-panama.streamlit.app`

4. **Advanced settings** (hacer clic):
   - **Python version**: `3.11`
   - **Secrets**: (dejar vacío por ahora, lo configuraremos después)

5. **Hacer clic en "Deploy!"**

6. **Esperar 3-5 minutos** mientras se despliega
   - Verás logs en tiempo real
   - Al final dirá "Your app is live!"

### 1.3 Verificar el deployment

- Tu dashboard estará en: `https://eda-bancario-panama.streamlit.app`
- **NOTA**: Por ahora mostrará error "No se puede conectar con la API" (es normal, falta desplegar el backend)

---

## 🎯 PASO 2: Desplegar Backend en Render

### 2.1 Crear cuenta en Render

1. **Ir a**: https://render.com/
2. **Hacer clic en** "Get Started"
3. **Sign up with GitHub**
4. **Autorizar** Render a acceder a tu GitHub

### 2.2 Crear Web Service

1. **En el Dashboard de Render**, hacer clic en **"New +"** → **"Web Service"**

2. **Conectar repositorio**:
   - Buscar: `EDA_Dashboard`
   - Hacer clic en **"Connect"**

3. **Configurar el servicio**:

   ```
   Name: eda-dashboard-api
   Region: Oregon (US West)
   Branch: main
   Root Directory: (dejar vacío)
   Runtime: Python 3
   Build Command: pip install -r requirements-backend.txt
   Start Command: uvicorn api.main:app --host 0.0.0.0 --port $PORT
   ```

4. **Instance Type**: Seleccionar **"Free"**

5. **Environment Variables** (hacer clic en "Add Environment Variable"):
   ```
   PYTHON_VERSION = 3.11.0
   ```

6. **Hacer clic en "Create Web Service"**

7. **Esperar 5-10 minutos** mientras se despliega
   - Verás logs en tiempo real
   - Al final dirá "Your service is live at https://..."

### 2.3 Copiar la URL de tu API

Una vez desplegado, verás algo como:
```
https://eda-dashboard-api-xxxx.onrender.com
```

**COPIAR ESTA URL** (la necesitarás en el siguiente paso)

---

## 🎯 PASO 3: Conectar Frontend con Backend

### 3.1 Configurar Secrets en Streamlit Cloud

1. **Ir a**: https://share.streamlit.io/
2. **Hacer clic en tu app** (`eda-bancario-panama`)
3. **Hacer clic en** ⚙️ **Settings** (arriba a la derecha)
4. **Hacer clic en** "Secrets" (en el menú lateral)
5. **Pegar este código** (reemplazar con TU URL de Render):

   ```toml
   API_URL = "https://eda-dashboard-api-xxxx.onrender.com"
   ```

6. **Hacer clic en "Save"**
7. **Hacer clic en "Reboot app"** (para que tome los cambios)

### 3.2 Verificar que todo funciona

1. **Abrir tu dashboard**: `https://eda-bancario-panama.streamlit.app`
2. **Esperar 30 segundos** (el backend en Render se "despierta")
3. **Cargar un archivo** Excel o CSV
4. **Verificar que el análisis funciona**

---

## 🎉 ¡LISTO! Tu Dashboard está Publicado

### 🔗 Links Finales

**Tu Dashboard Público**:
```
https://eda-bancario-panama.streamlit.app
```

**Tu API Backend**:
```
https://eda-dashboard-api-xxxx.onrender.com
```

**Documentación de la API**:
```
https://eda-dashboard-api-xxxx.onrender.com/docs
```

---

## 📧 Cómo Compartir por Correo

### Opción 1: Link directo

```
Hola [Nombre],

Te comparto el dashboard de análisis exploratorio de datos:

🔗 https://eda-bancario-panama.streamlit.app

Instrucciones:
1. Abrir el link
2. Cargar tu archivo Excel o CSV
3. Explorar los análisis automáticos

Saludos,
[Tu nombre]
```

### Opción 2: Con contexto

```
Asunto: Dashboard de Análisis Patrimonial - Listo para usar

Hola equipo,

Les comparto el nuevo dashboard interactivo para análisis exploratorio:

📊 Dashboard: https://eda-bancario-panama.streamlit.app

Características:
✅ Análisis de saldos (activos/pasivos)
✅ Análisis de productos y cross-sell
✅ Mapas geográficos interactivos
✅ Conclusiones automáticas
✅ Exportación de reportes

Pueden cargar cualquier archivo Excel o CSV y obtener insights automáticos.

¿Preguntas? Respondo con gusto.

Saludos,
[Tu nombre]
```

---

## ⚠️ Limitaciones del Plan Gratis

### Streamlit Cloud (Frontend)
- ✅ **Gratis para siempre**
- ✅ Siempre activo (no se duerme)
- ⚠️ 1 GB de RAM
- ⚠️ 1 app pública gratis (más apps = $20/mes)

### Render (Backend)
- ✅ **Gratis para siempre**
- ⚠️ Se "duerme" después de 15 minutos sin uso
- ⚠️ Tarda ~30 segundos en "despertar"
- ⚠️ 750 horas/mes gratis (suficiente para uso moderado)

**Solución**: Si necesitas que esté siempre activo, upgrade a Render Starter ($7/mes)

---

## 🔧 Troubleshooting

### Error: "No se puede conectar con la API"

**Causa**: El backend en Render está "dormido"

**Solución**:
1. Esperar 30-60 segundos
2. Recargar la página (F5)
3. Si persiste, verificar que la URL en Secrets sea correcta

---

### Error: "Application error" en Streamlit

**Causa**: Error en el código o falta de dependencias

**Solución**:
1. Ir a Settings → Logs
2. Revisar el error específico
3. Si falta un módulo, agregarlo a `requirements.txt`
4. Hacer push a GitHub (se redespliega automáticamente)

---

### Error: "Build failed" en Render

**Causa**: Error al instalar dependencias

**Solución**:
1. Verificar que `requirements-backend.txt` esté correcto
2. Revisar logs de build en Render
3. Si falta algo, actualizar y hacer push

---

## 🔐 Seguridad y Privacidad

### ⚠️ Importante

- El dashboard es **PÚBLICO** (cualquiera con el link puede acceder)
- Los datos que cargues **NO se guardan** (solo en memoria temporal)
- Cada sesión es independiente

### Si necesitas privacidad:

1. **Agregar autenticación** (usuario/password)
2. **Hacer el repositorio privado** (requiere Streamlit Cloud Pro - $20/mes)
3. **Desplegar en servidor privado** (AWS, Azure, GCP)

---

## 📊 Monitoreo

### Streamlit Cloud

- **Ver analytics**: https://share.streamlit.io/ → Tu app → Analytics
- **Ver logs**: Settings → Logs
- **Ver uso**: Settings → Usage

### Render

- **Ver logs**: Dashboard → Tu servicio → Logs
- **Ver métricas**: Dashboard → Tu servicio → Metrics
- **Ver uso**: Dashboard → Account → Usage

---

## 🚀 Actualizaciones

Cada vez que hagas `git push` a GitHub:
- ✅ Streamlit Cloud se **actualiza automáticamente**
- ✅ Render se **actualiza automáticamente**

No necesitas hacer nada más. 🎉

---

## 💰 Costos Mensuales

| Servicio | Plan | Costo |
|----------|------|-------|
| **Streamlit Cloud** | Community (1 app pública) | **$0** |
| **Render** | Free (con sleep) | **$0** |
| **GitHub** | Free (repositorio público) | **$0** |
| **TOTAL** | | **$0/mes** |

### Upgrades opcionales:

| Servicio | Plan | Costo | Beneficio |
|----------|------|-------|-----------|
| Streamlit Cloud | Pro | $20/mes | 3 apps privadas |
| Render | Starter | $7/mes | Sin sleep, siempre activo |

---

## 📞 Soporte

**Streamlit Cloud**: https://docs.streamlit.io/streamlit-community-cloud  
**Render**: https://render.com/docs

---

**¡Felicidades! Tu dashboard está en producción.** 🎉

Ahora puedes compartirlo con quien quieras por correo, Teams, WhatsApp, etc.
