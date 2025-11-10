# CSA - Control de Seguridad Asistido (Versión en desarrollo, sujeta a cambios.)

**CSA** es un sistema para el registro y visualización de incidentes urbanos.  
Permite registrar incidentes por tipo, gravedad y ubicación, tanto con coordenadas como con direcciones geográficas, que el sistema convierte automáticamente en coordenadas mediante geocodificación.


## Características principales

✅ Registro de incidentes con descripción, gravedad y localización  
✅ Posibilidad de usar **dirección o coordenadas**  
✅ Visualización en un **mapa interactivo (Folium + Streamlit)**  
✅ Filtros por **tipo de delito** y **nivel de gravedad**  
✅ Estadísticas básicas con gráficos  
✅ Botón para **borrar todos los incidentes registrados**  
✅ Interfaz simple y adaptable a cualquier pantalla  


## Instalación y ejecución

### 1️) Clonar el repositorio

git clone https://github.com/Exxo05/CSA---Control-de-Seguridad-Asistido-.git

cd CSA

### 2️) Crear entorno virtual
⚠️ Este paso es importante para mantener las dependencias separadas del sistema.
```
python -m venv venv
```

### 3️) Activar el entorno virtual

En Windows (CMD o PowerShell):
```
venv\Scripts\activate
```
En Linux / macOS:
```
source venv/bin/activate
```

## 4️) Instalar dependencias
```
pip install -r requirements.txt
```
Si no tienes el archivo requirements.txt, puedes generarlo con:
```
pip freeze > requirements.txt
```

### 5️) Ejecutar la aplicación
```
streamlit run main.py
```
Esto abrirá la aplicación en tu navegador (por defecto en
👉 http://localhost:8501)


## Cómo probar el sistema

#### 1️) Abre la app (streamlit run app.py)
#### 2️) En el menú lateral selecciona “Registrar incidente”
#### 3️) Introduce un tipo de delito, descripción y gravedad
#### 4️) Puedes elegir entre:

- Marcar “Usar dirección” y escribir algo como Puerta del Sol, Madrid
- Introducir manualmente latitud y longitud

#### 5️) Pulsa Registrar incidente
#### 6️) Ve a la pestaña “Mapa” para verlo en el mapa
#### 7️) Usa los filtros de la barra lateral para mostrar solo ciertos tipos o niveles de gravedad
#### 8️) En “Incidentes” puedes listar o borrar todos los registros

💡 ##Tecnologías utilizadas

- 🐍 Python 3.12+:	  Lenguaje principal del proyecto. Potente, flexible y con una amplia comunidad científica y de desarrollo.
- 🖥️ Streamlit:    	Framework que permite crear aplicaciones web interactivas para ciencia de datos de forma rápida y sencilla.
- 🗺️ Folium	:       Librería basada en Leaflet.js para generar mapas interactivos en Python. Usada para mostrar los incidentes geolocalizados.
- 📊 Pandas:	        Herramienta esencial para manejar, filtrar y analizar datos en formato tabular (CSV).
- 📍 Geopy:        	Utilizada para convertir direcciones en coordenadas geográficas (geocodificación) y viceversa.
