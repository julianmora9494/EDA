# 🌐 Desplegar el Dashboard

Instrucciones para desplegar la aplicación en producción.

## 1. Streamlit Cloud (Recomendado - Gratis)

### Paso 1: Preparar repositorio Git

```bash
git init
git add .
git commit -m "Initial commit"
```

Subir a GitHub:
```bash
git remote add origin https://github.com/tu-usuario/eda-dashboard.git
git branch -M main
git push -u origin main
```

### Paso 2: Desplegar en Streamlit Cloud

1. Ir a https://streamlit.io/cloud
2. Hacer clic en "Deploy an app"
3. Seleccionar tu repositorio
4. Branch: `main`
5. Main file path: `ui/app.py`
6. Hacer clic en "Deploy"

**Resultado**: Tu app en `https://tu-usuario-eda-dashboard.streamlit.app`

---

## 2. Heroku

### Paso 1: Crear archivos

**Procfile** (crear en raíz):
```
web: python -m streamlit run ui/app.py --server.port=$PORT --server.headless=true
```

**runtime.txt** (crear en raíz):
```
python-3.11.6
```

### Paso 2: Desplegar

```bash
heroku login
heroku create tu-eda-dashboard
git push heroku main
```

**Resultado**: Tu app en `https://tu-eda-dashboard.herokuapp.com`

---

## 3. AWS EC2

### Paso 1: Lanzar instancia

- AMI: Ubuntu 22.04 LTS
- Tipo: t3.micro (free tier)
- Almacenamiento: 20GB
- Security Group: Puertos 22, 80, 443

### Paso 2: Configurar servidor

```bash
ssh -i tu-clave.pem ubuntu@tu-ip-publica

# Actualizar
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install python3 python3-pip python3-venv nginx -y

# Clonar proyecto
git clone https://github.com/tu-usuario/eda-dashboard.git
cd eda-dashboard

# Crear entorno virtual
python3 -m venv venv_eda
source venv_eda/bin/activate
pip install -r requirements.txt
```

### Paso 3: Crear servicio systemd

Crear archivo `/etc/systemd/system/eda-dashboard.service`:

```ini
[Unit]
Description=EDA Dashboard
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/eda-dashboard
Environment="PATH=/home/ubuntu/eda-dashboard/venv_eda/bin"
ExecStart=/home/ubuntu/eda-dashboard/venv_eda/bin/streamlit run ui/app.py --server.port=8503 --server.headless=true

[Install]
WantedBy=multi-user.target
```

Activar servicio:
```bash
sudo systemctl daemon-reload
sudo systemctl enable eda-dashboard
sudo systemctl start eda-dashboard
```

### Paso 4: Configurar Nginx como reverse proxy

Crear `/etc/nginx/sites-available/eda-dashboard`:

```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://localhost:8503;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

Activar:
```bash
sudo ln -s /etc/nginx/sites-available/eda-dashboard /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

---

## 4. Docker

### Paso 1: Crear Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000 8503

CMD python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 &\
    python -m streamlit run ui/app.py --server.port 8503 --server.address 0.0.0.0
```

### Paso 2: Build y Deploy

```bash
docker build -t eda-dashboard .
docker run -p 8000:8000 -p 8503:8503 eda-dashboard
```

---

## 5. On-Premise (Servidor Local)

```bash
# Clonar proyecto
git clone https://repo-corporativo/eda-dashboard.git
cd eda-dashboard

# Crear entorno
python -m venv venv_eda
source venv_eda/bin/activate
pip install -r requirements.txt

# Ejecutar
python iniciar_dashboard.py
```

Acceder en: `http://IP-servidor:8503`

---

## 🔐 Seguridad para Producción

### HTTPS
```bash
sudo certbot certonly --nginx -d tu-dominio.com
```

### Variables de Entorno
Crear `.env`:
```
API_KEY=tu-clave-segura
DATABASE_URL=tu-conexion-db
```

### Monitoreo
- Uptime Robot: https://uptimerobot.com (gratis)
- DataDog o New Relic para observabilidad

---

## ✅ Checklist de Despliegue

- [ ] Código limpio (sin credenciales)
- [ ] requirements.txt actualizado
- [ ] .gitignore configurado
- [ ] Testing local completado
- [ ] HTTPS habilitado
- [ ] Logs configurados
- [ ] Backups automáticos activados
- [ ] Monitoreo configurado

---

## 🆘 Troubleshooting

| Problema | Solución |
|----------|----------|
| App lenta | Usar `@st.cache_data` más agresivamente |
| Error 502 | Revisar logs, reiniciar servicio |
| Datos no cargan | Verificar permisos de archivos |
| Puerto en uso | Cambiar puerto en configuración |

