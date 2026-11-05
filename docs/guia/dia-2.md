# Día 2 · Traer los datos a raw

**Objetivo:** que `python run.py ingest` deje las 4 tablas en el schema `raw` de DuckDB, iguales vengan de la API o del CSV.
**Tiempo estimado:** 4 a 6 horas.
**Entregás:** `ingestion/extract_load.py` sin TODOs.

## Antes de empezar

- Sacá tu token en [mauroprystupa.com/proyecto](https://mauroprystupa.com/proyecto/) (sección "Arrancá"). Es personal: no lo compartas ni lo subas al repo. Si lo perdés, pedí otro: el anterior deja de funcionar.
- Ponelo en `.env` junto con la URL (`API_URL` y `API_TOKEN`). `.env` está en el `.gitignore`.

Probá la API a mano antes de escribir código:

```bash
curl -H "Authorization: Bearer TU_TOKEN" "TU_API_URL/tables/products?limit=5"
```

Mirá la forma de la respuesta: `table`, `total`, `limit`, `offset` y `rows`. Probá también sin el header y con una tabla que no existe, para ver qué devuelve en cada caso.

## Pasos

1. **`leer_api`**: pedí páginas de 1.000 filas hasta juntar `total`. Ojo con el último lote, que viene incompleto.
2. **El límite de pedidos.** La API acepta una cantidad de pedidos por minuto por token. Si te pasás, responde `429` con un header `Retry-After`. Tu código tiene que esperar y reintentar, no explotar.
3. **`leer_csv`**: el respaldo para cuando la API no responde. Tiene que devolver **exactamente** lo mismo que la API: mismas columnas, valores y tipos. Esto es más difícil de lo que parece. Fijate qué tipo infiere pandas en cada columna, y si todas las filas de una misma columna tienen el mismo formato.
4. **`escribir_duckdb`**: cada tabla como `raw.<tabla>`. Correr la ingesta dos veces no puede duplicar filas.
5. **`main`**: armá el flujo con `--source auto|api|csv` y agregá `_loaded_at` a cada tabla.
6. **Compará los dos caminos.** Cargá raw desde la API, guardá una copia, cargá desde el CSV y compará. Si hay una sola diferencia, la vas a arrastrar hasta el tablero.

## Reglas de raw

- raw no se limpia. Si un valor viene raro, se queda raro: lo vas a arreglar en int, a la vista de todos.
- Lo único que se agrega es `_loaded_at`, para saber de cuándo es el dato.

## Cómo saber que quedó

```bash
python run.py ingest                 # desde la API
python run.py ingest --source csv    # desde el CSV
```

Las dos tienen que terminar con las 4 tablas cargadas y mostrar, por tabla, filas, origen y tiempo. Para mirar adentro de DuckDB:

```bash
python -c "import duckdb; print(duckdb.connect('data/proyecto.duckdb', read_only=True).sql('select count(*) from raw.orders'))"
```

## Si se rompe

| Síntoma | Qué mirar |
|---|---|
| `401` | Falta el token, está mal copiado o tiene espacios. Revisá `.env` |
| `429` todo el tiempo | Estás pidiendo en un loop sin esperar el `Retry-After` |
| Faltan filas | Mirá cómo avanzás el `offset` y cuándo cortás el loop |
| "Could not set lock on file" | Otro programa tiene abierto el DuckDB (el dashboard, un notebook). Cerralo |
| `403 Forbidden` | Estás usando `urllib`: Cloudflare bloquea su identificación por defecto. Usá `requests` (ya está instalado) |
| La API no responde | Probá con `--source csv`: es justamente para eso |

## Checkpoint

1. ¿Por qué raw no se limpia, si total después hay que limpiar igual?
2. ¿Qué pasa si corrés la ingesta dos veces seguidas? ¿Cómo lo comprobaste?
3. ¿Cómo sabés que bajaste todas las filas y no te faltó la última página?

<details>
<summary>Respuestas de referencia</summary>

1. Porque raw es la evidencia de lo que mandó el origen. Si limpiás en la ingesta, cuando un número no cierre no vas a poder saber si el error vino de la fuente o de tu limpieza. Además, la limpieza en Python queda escondida; en dbt queda documentada y testeada.
2. Si reemplazás la tabla completa, queda igual: la ingesta es idempotente. Se comprueba contando filas antes y después de la segunda corrida.
3. Comparando la cantidad de filas que juntaste con el `total` que devuelve la API, y fallando si no coinciden. Contar "hasta que venga una página vacía" funciona, pero no te avisa si se perdió algo en el medio.

</details>

<details>
<summary>Números de control</summary>

Filas en raw, iguales desde la API y desde el CSV:

| Tabla | Filas |
|---|---|
| customers | 1.000 |
| products | 80 |
| orders | 8.025 |
| order_items | 19.865 |

Si tu `raw.orders` tiene otra cantidad, el problema está en la ingesta, no en los datos.

</details>
