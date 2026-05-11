# CSA - Control de Seguridad Asistido (Versión Beta, sujeta a cambios)
**CSA** es un sistema integral para el registro, despliegue táctico y visualización de incidentes urbanos.

Permite gestionar la seguridad en tiempo real, clasificando incidentes por gravedad, recomendando el envío de patrullas y visualizando el estado de la ciudad en un mapa dinámico sincronizado con una base de datos SQL.

## 🚀 Características principales
✅ Registro inteligente de incidentes con clasificación automática de gravedad

✅ Asistente de Recomendación de Despliegue según nivel de riesgo

✅ Gestión de patrullas con estados (Patrullando / Intervención)

✅ Visualización en un mapa interactivo (Folium) con botón de refresco

✅ Sistema de estados: los incidentes pasan a Finalizados sin borrarse

✅ Panel de Estadísticas Operativas con gráficos de puntos calientes y delitos

✅ Persistencia de datos profesional mediante SQLite

## 🆕 Nuevas funcionalidades (última actualización)

### 🔐 Sistema de login
Ventana de acceso con usuario, contraseña y selección de turno.

### 📋 Log de auditoría
Registro completo de acciones (crear, editar, finalizar, etc.) indicando quién y cuándo.
Visible directamente en el dashboard.

### 🏠 Dashboard de turno
Pantalla inicial con:
KPIs en tiempo real (activos, finalizados hoy, unidades en servicio, en intervención)
Tabla de incidentes activos con tiempo transcurrido
Estado visual de todas las unidades
Últimas 5 acciones del sistema

### 📝 Notas internas por incidente
Sistema de anotaciones con historial.
Cada nota guarda autor y timestamp.

### 🔔 Alertas sonoras

3 pitidos → incidente crítico
1 pitido → alta gravedad
Funciona en Windows con winsound.

### 💾 Backup automático

Copia de la base de datos al iniciar
Ubicación: datos/backups/
Retención automática de 30 días

### 👮 Usuario activo visible
Nombre y rol del operador visibles en el sidebar.

## ⚙️ Instalación y ejecución
## 1) Clonar el repositorio
```
git clone https://github.com/Exxo05/CSA---Control-de-Seguridad-Asistido-.gitcd ../CSA---Control-de-Seguridad-Asistido-/CSA
```
### 2) Instalar dependencias
```
pip install -r requirements.txt
```
Si no tienes el archivo:
```
pip install pandas folium geopy openpyxl pywebview tkintermapview matplotlib brancaMostrar más líneas
```
⚠️ Nota: En algunos casos requirements.txt no instala todo correctamente (especialmente folium o pandas).
Instálalos manualmente si aparece algún error.

### 3) Ejecutar la aplicación
```
python run_gui.py
```
Se abrirá la interfaz de escritorio del sistema CSA.
⏳ La primera ejecución puede tardar unos segundos.

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

### 🐍 Python 3.13+ — Lenguaje principal

### 🖥️ Tkinter — Interfaz de escritorio

### 🗺️ Folium — Mapas interactivos

### 📊 Pandas & Matplotlib — Análisis y gráficos

### 📍 Geopy — Geocodificación

### 🗄️ SQLite3 — Persistencia de datos

### 🔊 Winsound — Alertas sonoras (Windows)
