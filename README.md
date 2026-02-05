# Juan Valdez API

## Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone https://github.com/JoseB007/API_juan_Valdez.git
cd API_juan_Valdez
```

### 2. Crear y activar el entorno virtual

**Linux / macOS:**
```bash
python3 -m venv env
source env/bin/activate
```

**Windows:**
```bash
python -m venv env
.\env\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
Crea un archivo `.env` en la raíz del proyecto basándote en la siguiente lista.

#### Variables requeridas:
- `SECRET_KEY`: Llave secreta de Django.
- `GEMINI_API_KEY`: API Key de Google Gemini.
- `CORS_ALLOWED_ORIGINS`: Dominios permitidos (ej: http://localhost:5173).
- `CSRF_TRUSTED_ORIGINS`: Dominios confiables para CSRF.
- `ENVIRONMENT`: Entorno de ejecución (`desarrollo` o `produccion`).
- `ALLOWED_HOSTS`: Hosts permitidos (ej: `localhost,127.0.0.1`).
- `API_KEY_ONOGRAPH`: Llave para el servicio externo Onograph (https://forebears.io.)

---

## Generar la SECRET_KEY de Django

Ejecutar el siguiente comando para obtener una nueva llave:
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

**Copiar el resultado y pegarlo en el archivo `.env`:**
```env
SECRET_KEY=llave_generada
```

---

## Base de Datos y Ejecución

### 1. Aplicar migraciones
```bash
python manage.py migrate
```

### 2. Iniciar el servidor de desarrollo
```bash
python manage.py runserver
```

La API estará disponible en `http://127.0.0.1:8000/`.