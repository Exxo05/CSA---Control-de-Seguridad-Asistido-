# CSA - Control de Seguridad Asistido (Versión media, sujeta a cambios)
**CSA** es un sistema integral para el registro, despliegue táctico y visualización de incidentes urbanos.

Permite gestionar la seguridad en tiempo real, clasificando incidentes por gravedad, recomendando el envío de patrullas y visualizando el estado de la ciudad en un mapa dinámico sincronizado con una base de datos SQL.

## Características principales
✅ Registro inteligente de incidentes con clasificación automática de gravedad 

✅ Asistente de Recomendación de Despliegue según nivel de riesgo

✅ Gestión de patrullas con estados (Patrullando / Intervención)

✅ Visualización en un mapa interactivo (Folium) con botón de refresco

✅ Sistema de estados: los incidentes pasan a Finalizados sin borrarse

✅ Panel de Estadísticas Operativas con gráficos de puntos calientes y delitos

✅ Persistencia de datos profesional mediante SQLite ## Instalación y ejecución

## Instalacion y ejecucion

 ### 1️) Clonar el repositorio
 ```
git clone https://github.com/Exxo05/CSA---Control-de-Seguridad-Asistido-.git
cd CSA
```
### 2️) Crear entorno virtual
⚠️ Este paso es importante para mantener las dependencias separadas del sistema. 
```
python -m venv .venv
```
### 3️) Activar el entorno virtual
Recuerda comprobar tu ruta, tienes que estar en ../CSA

En Windows (CMD o PowerShell):
```
.venv\Scripts\activate
```
En Linux / macOS:
```
source .venv/bin/activate
```
### 4️) Instalar dependencias
```
pip install -r requirements.txt
```
Si no tienes el archivo requirements.txt, puedes instalar las necesarias con:
```
pip install pandas folium geopy openpyxl pywebview tkintermapview matplotlib sqlite3
```
### 5️) Ejecutar la aplicación
```
python run_gui.py
```
Esto abrirá la interfaz profesional de escritorio (GUI) del sistema CSA.
La primera vez tarda un poco.

## Cómo probar el sistema
### 1️) Abre la app (python run_gui.py)
### 2️) En "Registrar Incidente" introduce un suceso; el sistema detectará la gravedad automáticamente.
### 3️) En el menú "Recomendación" selecciona el incidente para ver cuántas unidades sugiere enviar.
### 4️) Pulsa "Enviar Patrullas" para asignar unidades disponibles al sector.
### 5️) Ve a la pestaña “Mapa”, pulsa "Guardar Cambios" y visualiza los puntos críticos en el navegador.
### 6️) Usa el botón "Actualizar Mapa" dentro del mapa para ver los cambios en tiempo real.
### 7️) En "Unidades", finaliza una intervención para marcar el incidente como resuelto (✅).
### 8️) Consulta "Estadísticas" para ver el análisis histórico de delitos por barrio.

 ## 💡 Tecnologías utilizadas

🐍 Python 3.13+: Lenguaje principal del proyecto. Potente, flexible y con una amplia comunidad.

🖥️ Tkinter: Framework para la creación de la interfaz de escritorio profesional y reactiva.

🗺️ Folium: Librería basada en Leaflet.js para generar mapas interactivos sincronizados con la operativa.

📊 Pandas & Matplotlib: Herramientas esenciales para el manejo de la base de datos y generación de gráficos estadísticos.

📍 Geopy: Utilizada para convertir direcciones en coordenadas geográficas (geocodificación).

🗄️ SQLite3: Motor de base de datos relacional para la gestión persistente de incidentes y patrullas.
