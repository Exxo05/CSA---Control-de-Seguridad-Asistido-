# CSA v2.0 — Changelog de mejoras

## 🎨 UI/UX — Rediseño visual completo

### `gui/styles.py`
- Sistema de diseño centralizado con paleta semántica (crítica/alta/media/baja)
- Colores consistentes en toda la app (antes había hardcoding de `#1c2b46` por todos lados)
- Función `make_button()` para botones estilizados sin repetir código
- Función `make_header()` para encabezados uniformes en todas las pantallas
- Función `color_por_tipo()` para colorear filas según gravedad automáticamente

### `gui/sidebar.py`
- Indicador visual de pantalla activa (resaltado azul claro)
- Hover suave al pasar el ratón por los botones
- Icono 🛡️ y versión en el pie del sidebar
- Separadores visuales entre secciones

### `gui/main_window.py`
- Sincronización automática del sidebar al cambiar pantalla
- Fondo unificado con el tema

---

## 🤖 IA — Clasificador de incidentes mejorado

### `servicios/clasificador.py` (reescrito)
- De 12 categorías básicas a **18 categorías** con subcategorías
- Detección de **arma blanca** que sube la gravedad automáticamente
- Campo `confianza` → lista de palabras clave que activaron la clasificación
- Campo `emoji` y `color_tag` para integración directa en UI
- Estructura de datos más rica para el frontend

### `gui/screens/registrar.py` (reescrito)
- **Clasificación en tiempo real** mientras el operador escribe (debounce 400ms)
- Muestra tipo, gravedad con color, unidades recomendadas Y palabras clave detectadas
- Detección automática de zona mientras se escribe la dirección
- Layout en tarjetas (cards) con scroll
- Validaciones más robustas

---

## 🗺️ Mapa — Visor mejorado

### `mapas/mapa_principal.py` (reescrito)
- **Capas separadas** por gravedad (Críticos / Alta / Media-Baja / Finalizados)
- Control de capas (LayerControl) para activar/desactivar grupos
- **Popups HTML ricos** con tipo, descripción, zona, hora y estado
- Círculos suaves de zona con etiquetas
- Offset aleatorio para evitar solapamiento de marcadores en la misma zona
- Panel de resumen flotante (activos / finalizados)
- Parámetro `solo_activos` para filtrar desde la UI

### `gui/screens/mapa.py` (reescrito)
- Checkbox para filtrar activos / todos
- Botón "Abrir en navegador" como alternativa siempre disponible
- Soporte opcional para `tkinterweb` (mapa embebido)

---

## 📊 Estadísticas — Gráficos reales

### `gui/screens/estadisticas.py` (reescrito)
- **4 pestañas** (Resumen / Por Zonas / Por Tipo / Temporal)
- KPIs con tarjetas de color (total, activos, finalizados, zonas)
- **Gráfico de pastel** para distribución de estados
- **Gráfico de barras horizontales** por zona
- **Gráfico de barras verticales** por tipología (top 10)
- **Gráfico temporal** horario con área rellena (distribución de incidentes por hora del día)

---

## 🏗️ Código — Arquitectura y calidad

### `servicios/geo_logic.py` (reescrito)
- De 6 zonas a **8 zonas** con muchas más palabras clave (antes solo 30, ahora 70+)
- `COORDS_ZONAS` centralizado y usado tanto por el mapa como por el clasificador
- Función `listar_zonas()` para usar en dropdowns
- Compatibilidad hacia atrás con código antiguo

### `gui/screens/incidentes.py` (reescrito)
- **Búsqueda en tiempo real** por tipo, descripción o zona
- **Filtro por estado** (Todos / Solo activos / Solo finalizados)
- **Coloreado de filas por gravedad** usando tags de Treeview
- Leyenda visual de colores
- Contador de resultados visibles / total
- Diálogo de edición mejorado en `EditorIncidente` (Toplevel separado)

### `gui/screens/unidades.py` (reescrito)
- Tabla con colores por estado operativo
- Diálogo de cambio de estado como ventana separada limpia
- Contador de unidades en servicio en toolbar

### `gui/screens/recomendacion.py` (reescrito)
- Layout en **dos columnas** (incidente | unidades)
- Preselección automática de unidades según número recomendado
- Panel de análisis con color dinámico según gravedad

### `gui/screens/prevencion.py` (reescrito)
- KPIs en tarjetas de colores (zona crítica, franja horaria, tipo frecuente)
- **Ranking visual** de zonas con barra de progreso proporcional
- Cuadro de texto para la orden de servicio generada

---

## 📋 Buenas prácticas aplicadas
- Eliminado todo hardcoding de colores (`#1c2b46`) → ahora usan constantes de `styles.py`
- Separación clara de responsabilidades: servicios vs. GUI
- Imports organizados (stdlib → terceros → proyecto)
- Docstrings en funciones de servicio
- Manejo de excepciones en operaciones DB con `finally` para cerrar conexiones
