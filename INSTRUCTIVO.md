# Instructivo — Calculadora KIA PPM

## Estructura de archivos

| Archivo | Qué contiene | ¿Cuándo tocarlo? |
|---|---|---|
| `index.html` | Estructura de pantallas (botones, tabs, formularios) + lógica de cálculos y guardado en Airtable | Solo si cambia algo visual o de comportamiento |
| `styles.css` | Todos los estilos: colores, tipografía, tarjetas de planes, tablas | Solo si cambia el diseño |
| `contracts.js` | Generación de contratos PDF: textos, tablas de servicios, formato de impresión | Solo si cambia la estructura del contrato/PDF |
| `data.js` | Precios, modelos y cascadas de selección — codificados en base64 | **Nunca editar a mano.** Solo modificar con `update_prices.py` o `manage_models.py` |
| `actualizar_precios.bat` | Doble clic — instala dependencias y actualiza precios | Cada vez que cambien precios en el Excel |
| `gestionar_modelos.bat` | Doble clic — menú para agregar, eliminar o listar modelos | Cuando se añade o retira un modelo del catálogo |
| `update_prices.py` | Script Python que corre `actualizar_precios.bat` internamente | No se toca directamente |
| `manage_models.py` | Script Python que corre `gestionar_modelos.bat` internamente | No se toca directamente |

Los cuatro archivos desplegados en GitHub Pages (`index.html`, `styles.css`, `contracts.js`, `data.js`) deben estar todos en la **misma carpeta** del repositorio.

---

## Organización interna del código

### index.html — secciones del script principal

El código JavaScript en `index.html` está dividido en dos bloques `<script>`:

**Bloque 1** — Utilidades y cálculos:
```
// === VARIABLES GLOBALES ===          Config Airtable, getNextCotNum
// === REVISIONES Y DETALLE ===        getRevisionesHTML  (tablas de operaciones)
// === IMPRESIÓN DE COTIZACIÓN ===     printCotizacion  (PDF cliente)
// === UTILIDADES DOM ===              gel, fmt, showToast, setOpts, hideField, switchTab
// === AUTENTICACIÓN Y SESIÓN ===      checkLogin, sanitizeFilter, forceLogout, showApp
// === HISTORIAL DE COTIZACIONES ===   renderMisTable, filterMisTable, reprCotMis
// === PLANES: FULL SERVICE Y UL ===   populateFS, populateUL, svcTable, saveForm, planCard
// === CÁLCULO FULL SERVICE ===        calcFS
// === CÁLCULO UNLIMITED ===           calcUL
// === PLAN 2 SERVICIOS (DS) ===       populateDS, dsResetFrom, dsOnMotor
// === CÁLCULO DS ===                  calcDS, dsSaveForm, dsAttachSave
```

**Bloque 2** — Contratos y event listeners:
```
// (ya tiene sus propios comentarios de sección)
// Tabla de contratos, generarContrato, buildContratoFS/UL/DS
// Al final: event listeners de las cascadas y DOMContentLoaded
```

### contracts.js — funciones disponibles

`findAnnexTable`, `kmToLabel`, `kmToMeses`, `mesesLabel`, `getDSServices`, `buildAnexoDS`, `getRevisionesContratoHTML`, `buildContratoDS`

---

## Cómo actualizar precios

Cuando cambian precios en el Excel:

1. Guardar el archivo `Planes MPP KIA - Postventa.xlsx` con los nuevos precios
2. Hacer doble clic en `actualizar_precios.bat`
3. Revisar el resumen impreso:
   - `[ALERTA] SIN PRECIO EN EXCEL` → modelos en la calculadora que no están en el Excel (verificar si se renombraron o eliminaron)
   - `[INFO] precios que subieron` → confirmar que el alza es correcta
5. Hacer **commit y push** únicamente de `data.js` al repositorio GitHub. Pages publica el cambio en segundos.

`index.html`, `styles.css` y `contracts.js` no cambian al actualizar precios.

---

## Cómo agregar un modelo nuevo

### Full Service (FS)

1. Agregar la fila del modelo en la hoja Excel correspondiente (5K, 10K o 15K) con sus precios
2. Hacer doble clic en `gestionar_modelos.bat` → opción **7**
3. Ingresar la clave y el nombre de display cuando lo pida
4. Hacer doble clic en `actualizar_precios.bat` para llenar los precios desde el Excel
5. Commit y push de `data.js`

### Unlimited (UL)

1. Hacer doble clic en `gestionar_modelos.bat` → opción **8**
2. Repetir para cada rango (ej: una vez para `20K - 50K`, otra para `30K - 60K`)
3. Hacer doble clic en `actualizar_precios.bat` para llenar los precios
4. Commit y push de `data.js`

### 2 Servicios DS

1. Hacer doble clic en `gestionar_modelos.bat` → opción **9**
2. Ingresar la clave y los pares de KM separados por coma (ej: `5K-10K, 10K-20K, 20K-30K`)
3. Hacer doble clic en `actualizar_precios.bat` para llenar los precios
4. Commit y push de `data.js`

---

## Cómo eliminar un modelo

1. Hacer doble clic en `gestionar_modelos.bat` → opción **1, 2 o 3** para ver las claves exactas
2. Elegir la opción de eliminar correspondiente (**4, 5 o 6**) e ingresar la clave
3. Commit y push de `data.js`

---

## Cómo buscar código específico

| Necesidad | Dónde buscar |
|---|---|
| Cambiar color o estilo visual | `styles.css` |
| Cambiar texto o layout de un contrato PDF | `contracts.js` — buscar `buildContratoFS`, `buildContratoUL`, `buildContratoDS` |
| Cambiar la lógica de cálculo de precios | `index.html` — buscar `calcFS`, `calcUL` o `calcDS` |
| Cambiar el comportamiento de un desplegable | `index.html` — buscar `// === PLANES` o la sección `// === AUTENTICACIÓN` |
| Ver/depurar datos de un modelo | `python manage_models.py list-fs` (no editar `data.js` a mano) |

---

## Formato de claves

Las claves usan `|` como separador. Campos vacíos dejan el segmento vacío.

| Plan | Formato clave |
|---|---|
| Full Service | `MODELO\|motor\|trans\|freq\|combustible` |
| Unlimited | `MODELO\|motor\|trans\|freq\|combustible\|rango` |
| 2 Servicios DS | `Modelo\|motor\|trans\|freq\|combustible` |

Campos:
- `MODELO` — nombre en mayúsculas tal como aparece en la calculadora (ej: `SPORTAGE NQ5 HEV`)
- `motor` — cifra con un decimal (ej: `1.6`) o vacío para EVs
- `trans` — `MT`, `AT`, `DCT` o vacío para EVs
- `freq` — `5K`, `10K` o `15K`
- `combustible` — `GLP`, `GNV` o vacío
- `rango` (solo UL) — ej: `20K - 50K`, `30K - 60K`, `45K - 75K`

---

## Notas importantes

- Los modelos EV (sin motor ni transmisión) usan cadenas vacías: `EV9 OV||`
- Para modelos de frecuencia 15K, los planes FS se llaman **Plan 45K** y **Plan 60K** (no 20K/30K)
- Los rangos UL de frecuencia 15K son múltiplos de 15K: `30K - 60K`, `45K - 75K`, `60K - 90K`, `75K - 105K`
- `update_prices.py` solo sube precios — nunca los baja (tiene alerta si un precio sube, para confirmar)
- Después de cualquier cambio en `data.js`, hacer commit y push para que GitHub Pages lo publique
