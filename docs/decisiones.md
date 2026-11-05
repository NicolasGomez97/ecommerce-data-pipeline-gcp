# Decisiones

> Cada vez que elijas entre dos caminos (una regla de limpieza, la severidad de un test, cómo modelar un mart), anotalo acá.
> Es lo que vas a usar para el README, para `story.md` y para responder "¿por qué lo hiciste así?".

## Plantilla

### {NNN} — {Título corto}

- **Qué encontré / qué tenía que decidir:** {con la cantidad de filas afectadas, si aplica}
- **Alternativas:** {al menos dos}
- **Qué decidí y por qué:**
- **Qué impacto tiene:** {en qué número del tablero se nota}

---

### Ejemplo: lo que no sirve y lo que sí

❌ "Limpié los datos."

✅ **001 — Precios con IVA mezclados.** *(Ejemplo inventado: no pasa en este dataset.)* Encontré 120 productos con el precio cargado con IVA y el resto sin IVA. Alternativas: descontar el IVA en int o pedir que lo corrijan en el origen. Lo descuento en int y lo aviso, porque el origen no se puede tocar y mezclar los dos infla el margen. Impacto: el margen % de esas categorías baja unos puntos.

---

<!-- Tus decisiones, de acá para abajo -->

### 001 — Un solo origen por corrida

- **Qué tenía que decidir:** con `--source auto`, qué hacer si la API falla a mitad de la ingesta (por ejemplo, después de bajar `customers` y `products`).
- **Alternativas:** decidir el origen tabla por tabla (seguir con la API y usar el CSV solo en la tabla que falló) o decidirlo una vez para toda la corrida.
- **Qué decidí y por qué:** una vez para toda la corrida. Si la API falla en cualquier tabla, se releen las 4 del CSV. Así `raw` nunca mezcla `orders` de un momento con `order_items` de otro.
- **Qué impacto tiene:** una caída de la API cuesta releer los CSV (menos de 1 segundo), pero los joins de `int` siempre trabajan sobre una foto consistente.

### 002 — Reemplazar `raw` completa en cada corrida

- **Qué tenía que decidir:** cómo cargar en BigQuery sin duplicar filas al correr la ingesta dos veces.
- **Alternativas:** `insert_rows` (streaming), `MERGE` incremental o load job con `WRITE_TRUNCATE`.
- **Qué decidí y por qué:** load job con `WRITE_TRUNCATE`. Con ~29 mil filas, recargar todo es más simple y barato que mantener una lógica incremental, y un load job no tiene el costo ni las restricciones del streaming.
- **Qué impacto tiene:** la ingesta es idempotente. Se verificó corriéndola dos veces seguidas: los conteos quedaron iguales (1.000 · 80 · 8.025 · 19.865).

### 003 — El CSV de respaldo usa la misma regla de tipos que la API

- **Qué tenía que decidir:** cómo lograr que `leer_csv` devuelva exactamente el mismo DataFrame que `leer_api`.
- **Alternativas:** dejar que `pd.read_csv` infiera los tipos o leer todo como texto y aplicar la regla de la API (una columna es numérica solo si **todos** sus valores lo son; vacío → null).
- **Qué decidí y por qué:** aplicar la regla de la API. Con los datos actuales los dos caminos coinciden, pero la inferencia de pandas no es la misma que la de la API. Un valor como `"007"` haría que difieran, y `raw` cambiaría de tipo según el origen.
- **Qué impacto tiene:** un test (`tests/test_extract_load.py`) compara las 4 tablas entre ambos orígenes con `assert_frame_equal`.

### 004 — Esperar lo que dice `Retry-After`, no un tiempo fijo

- **Qué encontré:** la API limita a 30 pedidos por minuto con una ventana deslizante. Una corrida completa son 31 pedidos, así que el último siempre recibe un 429.
- **Alternativas:** esperar 60 segundos fijos o esperar lo que indica el header `Retry-After`.
- **Qué decidí y por qué:** respetar `Retry-After` y repetir el mismo pedido sin avanzar el offset. En las pruebas, la espera fue de 9 a 60 segundos según cuántos pedidos quedaban en la ventana.
- **Qué impacto tiene:** la ingesta nunca falla por el límite y no espera de más.
