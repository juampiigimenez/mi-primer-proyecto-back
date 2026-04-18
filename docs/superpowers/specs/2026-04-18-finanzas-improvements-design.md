# Finanzas App - Mejoras y Correcciones

**Fecha:** 2026-04-18  
**Estado:** Aprobado  
**Autor:** Claude Sonnet 4.5

---

## Resumen Ejecutivo

Implementar tres mejoras críticas en la aplicación de finanzas personales:
1. Corregir bug donde transacciones importadas no aparecen en el historial del dashboard
2. Cambiar formato de moneda de USD a pesos argentinos (ARS) en toda la aplicación
3. Agregar historial persistente de archivos importados con notificaciones de éxito

---

## Problema 1: Transacciones Importadas No Aparecen en Dashboard

### Descripción del Problema
Las transacciones confirmadas desde el importador de Mercado Pago se guardan correctamente en el backend, pero no se visualizan en el historial de transacciones del dashboard principal.

### Causa Raíz
El método `loadDashboardData()` en el frontend no se está ejecutando correctamente después de confirmar las importaciones, o hay un problema de sincronización con el backend.

### Solución
1. Verificar que el endpoint `GET /transacciones` retorna las transacciones recién agregadas
2. Asegurar que `loadDashboardData()` se ejecuta completamente ANTES de cambiar de pestaña
3. Agregar un pequeño delay (100-200ms) si es necesario para que el backend termine de persistir
4. Verificar que `renderTransactions()` se ejecuta con los nuevos datos

### Archivos Afectados
- **Frontend:** `c:/proyectos/finanzas-front/js/imports.js` (función `setupConfirmButton`)
- **Frontend:** `c:/proyectos/finanzas-front/js/dashboard.js` (función `loadDashboardData`)

---

## Problema 2: Formato de Moneda USD → ARS

### Descripción del Problema
La aplicación muestra todos los montos en dólares estadounidenses (US$ 1,500.50) cuando debe mostrarlos en pesos argentinos con formato local.

### Formato Requerido
- **Símbolo:** `$` (no ARS, no US$)
- **Miles:** punto (`.`)
- **Decimales:** coma (`,`)
- **Ejemplo:** `$ 1.500,50`

### Áreas Afectadas (TODA LA APLICACIÓN)
1. **Dashboard:**
   - Balance total (header principal)
   - Historial de transacciones (lista)
   - Gráfico de torta (labels y porcentajes)
   - Totales de ingresos/gastos (leyenda del gráfico)

2. **Importador de Mercado Pago:**
   - Tabla de resultados de importación
   - KPIs (total filas, procesadas, duplicadas, fallidas)
   - Resumen de confirmación

3. **Formulario de Nueva Transacción:**
   - Input de monto
   - Vista previa de transacción

### Implementación

#### Backend
No requiere cambios - ya maneja montos como números flotantes sin moneda específica.

#### Frontend

**Archivo:** `c:/proyectos/finanzas-front/js/config.js`
```javascript
export const CONFIG = {
  CURRENCY: 'ARS',  // Cambiar de 'USD' a 'ARS'
  LOCALE: 'es-AR'
};
```

**Archivo:** `c:/proyectos/finanzas-front/js/ui.js`
```javascript
export function formatCurrency(amount) {
  // Usar Intl.NumberFormat con locale es-AR y currency ARS
  // Formato resultante: $ 1.500,50
  return new Intl.NumberFormat('es-AR', {
    style: 'currency',
    currency: 'ARS',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount);
}
```

**Nota:** La función `formatCurrency()` ya se usa en todos los lugares correctos. Solo cambiar la configuración y formato garantiza consistencia global.

---

## Problema 3: Historial de Archivos Importados

### Descripción
Agregar un historial persistente de archivos importados que muestre:
- Qué archivos se importaron
- Cuándo se confirmaron
- Cuántas transacciones contenían
- Totales de ingresos y gastos

### Requerimientos Funcionales

1. **Persistencia en Backend:** Los registros de importación deben guardarse en la base de datos
2. **Formato de Nombre:** Convertir `settlement-x-2024-04-18.csv` a `Semana 16 - 2024`
3. **Cálculo de Semana:** Usar ISO 8601 (semana del año)
4. **Notificación de Éxito:** Toast verde al confirmar importación
5. **Visualización:** Historial al final de la pestaña "Importar Mercado Pago"

---

## Arquitectura - Backend

### Nuevo Modelo de Datos

**Archivo:** `c:/proyectos/finanzas-back/app/models/import_history.py` (crear nuevo)

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ImportHistory(BaseModel):
    id: str  # UUID
    filename: str  # Nombre original: "settlement-x-2024-04-18.csv"
    uploaded_at: datetime  # Fecha/hora de carga del archivo
    confirmed_at: datetime  # Fecha/hora de confirmación
    batch_id: str  # Referencia al batch importado
    status: str  # "confirmed" (por ahora solo confirmados)
    total_transactions: int  # Cantidad total de transacciones
    total_ingresos: float  # Total de ingresos confirmados
    total_gastos: float  # Total de gastos confirmados
    week_number: int  # Número de semana ISO 8601 (1-53)
    display_name: str  # "Semana 16 - 2024" (precalculado)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "hist-abc123",
                "filename": "settlement-x-2024-04-18.csv",
                "uploaded_at": "2024-04-18T14:25:00",
                "confirmed_at": "2024-04-18T14:30:00",
                "batch_id": "batch-xyz789",
                "status": "confirmed",
                "total_transactions": 24,
                "total_ingresos": 15000.50,
                "total_gastos": 8500.75,
                "week_number": 16,
                "display_name": "Semana 16 - 2024"
            }
        }
```

### Modificación del Schema de Base de Datos

**Archivo:** `c:/proyectos/finanzas-back/app/repositories/json_repository.py`

Agregar nueva colección en el método `_initialize_schema()`:

```python
def _initialize_schema(self) -> Dict[str, Any]:
    return {
        '_metadata': {...},
        'accounts': {},
        'credit_cards': {},
        'categories': {},
        'transactions': {},
        'transaction_import_batches': {},
        'raw_import_rows': {},
        'import_history': {},  # NUEVO - Historial de importaciones confirmadas
        'recurring_expenses': {},
        'budgets': {},
        'assets': {},
        'liabilities': {},
        'net_worth_snapshots': {},
        'crypto_wallets': {},
        'crypto_positions': {},
        'processed_source_ids': {},
    }
```

### Endpoints

#### 1. GET /api/v1/imports/history

**Propósito:** Obtener el historial completo de archivos importados y confirmados.

**Request:**
```http
GET /api/v1/imports/history HTTP/1.1
Host: localhost:8000
```

**Response (200 OK):**
```json
{
  "success": true,
  "history": [
    {
      "id": "hist-abc123",
      "filename": "settlement-x-2024-04-18.csv",
      "confirmed_at": "2024-04-18T14:30:00",
      "display_name": "Semana 16 - 2024",
      "total_transactions": 24,
      "total_ingresos": 15000.50,
      "total_gastos": 8500.75,
      "status": "confirmed"
    },
    {
      "id": "hist-def456",
      "filename": "settlement-x-2024-04-11.csv",
      "confirmed_at": "2024-04-11T16:45:00",
      "display_name": "Semana 15 - 2024",
      "total_transactions": 18,
      "total_ingresos": 12000.00,
      "total_gastos": 6500.25,
      "status": "confirmed"
    }
  ]
}
```

**Ordenamiento:** Por `confirmed_at` descendente (más recientes primero).

**Manejo de Errores:**
- **500:** Error al leer la base de datos

**Implementación:**
1. Leer la colección `import_history` del JSONDatabase
2. Convertir a lista de objetos ImportHistory
3. Ordenar por `confirmed_at` DESC
4. Retornar JSON

**Archivo:** `c:/proyectos/finanzas-back/app/routers/imports.py`

---

#### 2. POST /api/v1/imports/batches/{batch_id}/confirm (Modificar Existente)

**Cambios:**
1. Después de confirmar las transacciones exitosamente
2. Extraer el `filename` del batch
3. Parsear la fecha del filename (formato: `settlement-x-YYYY-MM-DD.csv`)
4. Calcular el número de semana ISO 8601
5. Crear el `display_name` (formato: `Semana {week} - {year}`)
6. Crear un registro `ImportHistory`
7. Guardar en la colección `import_history`
8. Retornar el `history_id` en la respuesta

**Response Modificado (200 OK):**
```json
{
  "success": true,
  "batch_id": "batch-xyz789",
  "history_id": "hist-abc123",  // NUEVO CAMPO
  "summary": {
    "ingresos_confirmados": 5,
    "gastos_confirmados": 19,
    "total_ingresos_ars": 15000.50,
    "total_gastos_ars": 8500.75,
    "total_transacciones": 24
  }
}
```

**Lógica de Parsing del Filename:**

```python
import re
from datetime import datetime

def parse_settlement_filename(filename: str) -> dict:
    """
    Parsea filename tipo: settlement-x-2024-04-18.csv
    Retorna: {date: datetime, week: int, year: int, display_name: str}
    """
    # Regex para extraer la fecha: YYYY-MM-DD
    pattern = r'settlement-x-(\d{4})-(\d{2})-(\d{2})'
    match = re.search(pattern, filename)
    
    if not match:
        raise ValueError(f"Formato de filename inválido: {filename}")
    
    year, month, day = match.groups()
    date = datetime(int(year), int(month), int(day))
    
    # Calcular semana ISO 8601
    week_number = date.isocalendar()[1]  # Retorna (year, week, weekday)
    
    # Crear display name
    display_name = f"Semana {week_number} - {year}"
    
    return {
        "date": date,
        "week": week_number,
        "year": int(year),
        "display_name": display_name
    }
```

**Archivo:** `c:/proyectos/finanzas-back/app/routers/imports.py`

---

## Arquitectura - Frontend

### Cambios en API Client

**Archivo:** `c:/proyectos/finanzas-front/js/api.js`

Agregar nuevo método:

```javascript
class APIClient {
  // ... métodos existentes ...
  
  async getImportHistory() {
    return this.request('/api/v1/imports/history');
  }
}
```

---

### Modificaciones en Tabla de Resultados de Importación

**Archivo:** `c:/proyectos/finanzas-front/index.html`

**Columnas ANTES (9):**
```html
<th>Fecha</th>
<th>Descripción</th>
<th>Comercio</th>
<th>Monto</th>
<th>Moneda</th>
<th>Tipo</th>
<th>Categoría</th>
<th>Estado</th>
<th>Método Pago</th>
```

**Columnas DESPUÉS (4):**
```html
<th>Fecha</th>
<th>Monto</th>
<th>Tipo</th>
<th>Método Pago</th>
```

**Columnas Eliminadas:**
- Descripción
- Comercio  
- Moneda
- Categoría
- Estado

**Archivo:** `c:/proyectos/finanzas-front/js/imports.js`

Modificar la función `renderImportedTransactions()` para generar solo las 4 columnas en el HTML.

---

### Notificación Toast de Éxito

**Ubicación:** Parte superior de la pantalla, centrado

**Diseño:**
```
┌────────────────────────────────────────────┐
│  ✓  Importación completada - 24           │
│     transacciones registradas             │
└────────────────────────────────────────────┘
```

**Estilos CSS:**
- Fondo: Verde (#2ed573)
- Borde: Verde más oscuro (#26a65b)
- Texto: Blanco
- Icono: ✓ blanco
- Posición: Fixed, top: 20px, center
- Animación: Slide down + fade in
- Duración: 5 segundos, luego fade out

**Implementación:**

**Archivo:** `c:/proyectos/finanzas-front/css/components.css`

Agregar estilos:

```css
.toast-notification {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--color-success);
  border: 2px solid var(--color-success-dark);
  color: var(--text-white);
  padding: var(--spacing-md) var(--spacing-lg);
  border-radius: var(--radius-md);
  box-shadow: 0 4px 12px rgba(46, 213, 115, 0.4);
  z-index: var(--z-modal);
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-weight: 600;
  animation: slideDownFadeIn 0.3s ease;
}

.toast-notification.fade-out {
  animation: fadeOut 0.3s ease;
}

@keyframes slideDownFadeIn {
  from {
    opacity: 0;
    transform: translate(-50%, -20px);
  }
  to {
    opacity: 1;
    transform: translate(-50%, 0);
  }
}

@keyframes fadeOut {
  to {
    opacity: 0;
  }
}
```

**Archivo:** `c:/proyectos/finanzas-front/js/ui.js`

Agregar función:

```javascript
export function showToast(message, duration = 5000) {
  // Crear elemento toast
  const toast = document.createElement('div');
  toast.className = 'toast-notification';
  toast.innerHTML = `<span style="font-size: 1.5rem;">✓</span> ${message}`;
  
  // Agregar al DOM
  document.body.appendChild(toast);
  
  // Remover después del duration
  setTimeout(() => {
    toast.classList.add('fade-out');
    setTimeout(() => {
      document.body.removeChild(toast);
    }, 300);
  }, duration);
}
```

**Uso en imports.js:**

```javascript
import { showToast } from './ui.js';

// Después de confirmar exitosamente:
showToast(`Importación completada - ${registeredCount} transacciones registradas`);
```

---

### Componente: Historial de Importaciones

**Ubicación:** Al final de la pestaña "Importar Mercado Pago", después de la sección de resultados de importación.

**HTML Structure:**

**Archivo:** `c:/proyectos/finanzas-front/index.html`

Agregar antes del cierre del `<div id="import">`:

```html
<!-- Import History Section -->
<div id="importHistorySection" class="card import-section" style="margin-top: 30px; display: none;">
  <h2>Historial de Importaciones</h2>
  <div id="importHistoryList" class="import-history-list">
    <!-- Items generados dinámicamente -->
  </div>
</div>
```

**CSS Styles:**

**Archivo:** `c:/proyectos/finanzas-front/css/components.css`

Agregar estilos:

```css
.import-history-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.history-item {
  background: rgba(15, 52, 96, 0.4);
  border-left: 4px solid var(--color-success);
  border-radius: var(--radius-sm);
  padding: var(--spacing-md);
  transition: all var(--transition-base);
}

.history-item:hover {
  background: rgba(15, 52, 96, 0.6);
  transform: translateX(5px);
}

.history-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-xs);
}

.history-icon {
  color: var(--color-success);
  font-size: 1.5rem;
  font-weight: bold;
}

.history-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
}

.history-stats {
  display: flex;
  gap: var(--spacing-lg);
  color: var(--text-primary);
  font-size: var(--font-size-md);
  margin-bottom: var(--spacing-xs);
}

.history-stat {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.history-timestamp {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
}

.history-empty {
  text-align: center;
  color: var(--text-secondary);
  padding: var(--spacing-xl);
  font-style: italic;
}
```

**JavaScript Implementation:**

**Archivo:** `c:/proyectos/finanzas-front/js/imports.js`

Agregar funciones:

```javascript
// Al inicializar el módulo
export function initImports() {
  setupFileUpload();
  setupImportButton();
  setupConfirmButton();
  loadImportHistory();  // NUEVO
}

async function loadImportHistory() {
  try {
    const response = await api.getImportHistory();
    
    if (response.success && response.history.length > 0) {
      renderImportHistory(response.history);
      document.getElementById('importHistorySection').style.display = 'block';
    }
  } catch (error) {
    console.error('Error loading import history:', error);
    // No mostrar error al usuario, simplemente no mostrar el historial
  }
}

function renderImportHistory(historyItems) {
  const listElement = document.getElementById('importHistoryList');
  
  if (historyItems.length === 0) {
    listElement.innerHTML = '<div class="history-empty">No hay importaciones registradas aún</div>';
    return;
  }
  
  const html = historyItems.map(item => `
    <div class="history-item">
      <div class="history-header">
        <span class="history-icon">✓</span>
        <span class="history-title">${escapeHtml(item.display_name)}</span>
      </div>
      <div class="history-stats">
        <span class="history-stat">
          ${item.total_transactions} transacciones
        </span>
        <span class="history-stat">
          ${formatCurrency(item.total_ingresos)}
        </span>
        <span class="history-stat">
          ${formatCurrency(item.total_gastos)}
        </span>
      </div>
      <div class="history-timestamp">
        Confirmado el ${formatDateTime(item.confirmed_at)}
      </div>
    </div>
  `).join('');
  
  listElement.innerHTML = html;
}

function formatDateTime(isoString) {
  const date = new Date(isoString);
  return date.toLocaleDateString('es-AR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}
```

**Recarga del Historial:**

Después de confirmar exitosamente una importación, recargar el historial:

```javascript
// En setupConfirmButton(), después de switchTab('dashboard'):
await loadImportHistory();
```

---

## Flujo de Usuario Completo

### Escenario: Importar Archivo de Mercado Pago

1. **Usuario carga archivo** `settlement-x-2024-04-18.csv`
2. **Sistema procesa** y muestra resultados con 4 columnas (Fecha, Monto, Tipo, Método Pago)
3. **Usuario hace clic en "Confirmar y Registrar en Dashboard"**
4. **Sistema:**
   - Registra transacciones en el backend
   - Crea registro en `import_history` con display name "Semana 16 - 2024"
   - Retorna `history_id` en la respuesta
5. **Frontend:**
   - Muestra toast verde: "✓ Importación completada - 24 transacciones registradas"
   - Recarga datos del dashboard
   - Cambia a pestaña Dashboard
   - Recarga historial de importaciones
6. **Usuario ve:**
   - Toast de éxito (5 segundos)
   - Dashboard con nuevas transacciones en el historial (formato `$ 1.500,50`)
   - Balance actualizado
   - Gráfico actualizado
7. **Usuario vuelve a pestaña Importador:**
   - Ve el nuevo registro en "Historial de Importaciones"
   - Con icono verde ✓
   - "Semana 16 - 2024"
   - Estadísticas de la importación

---

## Testing

### Backend

**Archivo:** `c:/proyectos/finanzas-back/tests/test_import_history.py` (crear nuevo)

Tests requeridos:
1. `test_get_import_history_empty()` - Historial vacío
2. `test_get_import_history_with_data()` - Retorna historial ordenado
3. `test_confirm_batch_creates_history()` - Confirmar batch crea registro
4. `test_parse_settlement_filename()` - Parsing correcto del filename
5. `test_parse_settlement_filename_invalid()` - Manejo de errores
6. `test_week_number_calculation()` - Semana ISO correcta

### Frontend

**Manual Testing:**
1. Importar archivo y verificar 4 columnas en tabla
2. Confirmar importación y verificar:
   - Toast verde aparece
   - Dashboard muestra transacciones
   - Formato de moneda es `$ X.XXX,XX`
   - Historial se actualiza
3. Verificar historial persiste después de recargar página
4. Verificar formato "Semana X - YYYY"

---

## Consideraciones de Implementación

### Orden de Implementación Recomendado

1. **Fase 1: Backend - Modelo e Historial**
   - Crear modelo `ImportHistory`
   - Agregar colección `import_history` al schema
   - Implementar endpoint `GET /api/v1/imports/history`
   - Implementar función `parse_settlement_filename()`

2. **Fase 2: Backend - Modificar Confirmación**
   - Modificar endpoint `POST /batches/{batch_id}/confirm`
   - Agregar lógica de creación de historial
   - Retornar `history_id` en respuesta

3. **Fase 3: Frontend - Formato de Moneda**
   - Cambiar `config.js` (CURRENCY: 'ARS')
   - Modificar `ui.js` (formatCurrency con locale es-AR)
   - Verificar en toda la app

4. **Fase 4: Frontend - Tabla de Resultados**
   - Modificar HTML (eliminar columnas)
   - Modificar `renderImportedTransactions()` en imports.js

5. **Fase 5: Frontend - Toast de Éxito**
   - Agregar estilos CSS
   - Implementar función `showToast()` en ui.js
   - Integrar en `setupConfirmButton()`

6. **Fase 6: Frontend - Componente de Historial**
   - Agregar HTML structure
   - Agregar estilos CSS
   - Implementar `loadImportHistory()` y `renderImportHistory()`
   - Integrar recarga después de confirmar

7. **Fase 7: Bug Fix - Dashboard**
   - Revisar y corregir `loadDashboardData()`
   - Agregar delay si es necesario
   - Verificar recarga completa de datos

8. **Fase 8: Testing**
   - Tests de backend
   - Testing manual de frontend
   - Verificación end-to-end

### Migraciones de Base de Datos

No se requiere migración formal ya que JSONDatabase agrega colecciones automáticamente. Sin embargo:

1. **Primera ejecución:** La colección `import_history` se creará vacía
2. **Datos existentes:** Los batches ya importados NO aparecerán en el historial (solo los nuevos)
3. **Backfill opcional:** Si se desea, se puede crear un script para analizar `transaction_import_batches` existentes y crear registros históricos

### Manejo de Errores

1. **Filename inválido:** Capturar excepción en `parse_settlement_filename()` y usar fallback "Importación - {fecha_hora}"
2. **Historial no disponible:** Frontend no muestra la sección si falla la carga
3. **Confirmación parcial:** Si algunas transacciones fallan, el historial registra solo las exitosas

---

## Notas de Diseño

### ¿Por qué persistencia en backend?

- **Auditoría:** Registro permanente de qué se importó y cuándo
- **Sincronización:** Disponible en cualquier dispositivo
- **Análisis futuro:** Base para estadísticas y reportes
- **Confiabilidad:** No se pierde con caché del navegador

### ¿Por qué calcular display_name en backend?

- **Consistencia:** El mismo filename siempre produce el mismo display name
- **Performance:** Cálculo una sola vez al confirmar, no cada render
- **Mantenibilidad:** Cambiar formato solo requiere modificar backend

### ¿Por qué eliminar columnas de la tabla?

- **Simplicidad:** Menos información = más fácil de escanear visualmente
- **Relevancia:** Usuario solo necesita verificar montos, tipos y método de pago
- **Espacio:** Más legible en pantallas pequeñas

---

## Apéndice: Estructura de Archivos

### Backend (Nuevos/Modificados)

```
finanzas-back/
├── app/
│   ├── models/
│   │   └── import_history.py          [NUEVO]
│   ├── repositories/
│   │   └── json_repository.py         [MODIFICAR]
│   └── routers/
│       └── imports.py                  [MODIFICAR]
├── tests/
│   └── test_import_history.py         [NUEVO]
└── docs/
    └── superpowers/
        └── specs/
            └── 2026-04-18-finanzas-improvements-design.md [ESTE ARCHIVO]
```

### Frontend (Modificados)

```
finanzas-front/
├── css/
│   └── components.css                  [MODIFICAR]
├── js/
│   ├── config.js                       [MODIFICAR]
│   ├── api.js                          [MODIFICAR]
│   ├── ui.js                           [MODIFICAR]
│   ├── dashboard.js                    [MODIFICAR]
│   └── imports.js                      [MODIFICAR]
└── index.html                          [MODIFICAR]
```

---

## Criterios de Aceptación

### ✅ Problema 1: Transacciones en Dashboard
- [ ] Las transacciones confirmadas aparecen inmediatamente en el historial del dashboard
- [ ] El balance se actualiza correctamente
- [ ] El gráfico refleja los nuevos datos

### ✅ Problema 2: Formato de Moneda
- [ ] Todos los montos se muestran con formato `$ 1.500,50`
- [ ] Dashboard: balance, historial, gráfico, totales
- [ ] Importador: tabla de resultados, KPIs
- [ ] Ningún monto muestra US$ o formato con coma para miles

### ✅ Problema 3: Historial de Importaciones
- [ ] Endpoint `GET /api/v1/imports/history` funciona correctamente
- [ ] Endpoint `POST /batches/{batch_id}/confirm` crea registro en historial
- [ ] Display name se calcula correctamente: "Semana X - YYYY"
- [ ] Toast verde aparece al confirmar importación
- [ ] Historial se muestra al final de la pestaña Importador
- [ ] Cada registro muestra: icono verde, nombre, estadísticas, timestamp
- [ ] Historial se ordena de más reciente a más antiguo
- [ ] Historial persiste entre recargas de página

### ✅ Tabla de Resultados
- [ ] Solo muestra 4 columnas: Fecha, Monto, Tipo, Método Pago
- [ ] Descripción, Comercio, Moneda, Categoría, Estado están ocultas

---

## Fin del Documento de Diseño

**Estado:** Listo para implementación  
**Próximo paso:** Crear plan de implementación detallado con `writing-plans` skill
