# Día 3 · Ordenar (stg) y limpiar (int)

**Objetivo:** que los datos de raw queden con tipos correctos en stg y limpios y unidos en int, con tests que lo prueben.
**Tiempo estimado:** el día más largo. 6 horas o más.
**Entregás:** `_sources.yml`, los 4 modelos stg, tus modelos int, sus `schema.yml` y un test singular.

## Parte 1 · stg: el espejo ordenado

1. **Sources.** Declará las 4 tablas de raw en `models/staging/_sources.yml`, con un test de frescura sobre `_loaded_at`. Desde ahora, los modelos leen raw con `source()`, nunca con el nombre de la tabla escrito a mano.
2. **Los 4 modelos stg.** Una fila de stg por cada fila de raw, con nombres de columna consistentes y tipos correctos. Nada de filtrar, deduplicar ni unir tablas.
3. **Fechas.** Castear una fecha parece trivial. Revisá que **todas** las fechas queden convertidas y ninguna quede nula sin que te des cuenta. Si un formato no te sirve para todas las filas, vas a necesitar algo más que un `cast`, y lo que escribas tiene que correr igual en DuckDB y en BigQuery. Las macros de dbt sirven para eso.
4. **Tests de stg.** `unique` y `not_null` en cada clave primaria, `relationships` entre las tablas y `accepted_values` en el `status` de orders.

### Tests que fallan

Algunos de esos tests van a fallar, y es lo esperado: stg muestra el dato como vino, y el dato tiene problemas. Antes de "arreglarlos", entendé esto:

- Si un test falla con severidad `error`, `dbt build` **no construye** nada de lo que depende de ese modelo. Un test rojo en stg te deja sin int y sin mart.
- dbt permite que un test avise sin frenar (`severity: warn`).

Decidí la severidad de cada test y anotá por qué en `docs/decisiones.md`. Lo que no puede pasar es que un problema quede sin test: si avisa en stg, en int tiene que haber una regla que lo resuelva y un test estricto que lo pruebe.

## Parte 2 · int: donde vive la limpieza

1. **Explorá antes de limpiar.** Usá DuckDB para mirar cada tabla de stg. Algunas preguntas que conviene hacerle a cualquier dato:
   - ¿La clave primaria es única de verdad?
   - ¿Hay valores que significan lo mismo pero están escritos distinto?
   - ¿Hay vacíos? ¿Qué significan?
   - ¿Hay filas que apuntan a otra tabla y no encuentran a quién?
   - ¿Hay números fuera de la escala o del rango esperado?
   - ¿Hay cantidades o importes que no tienen sentido?
2. **Una regla por problema.** Por cada cosa que encuentres, escribí en `docs/decisiones.md` qué encontraste, cuántas filas afecta y qué decidiste hacer. "Lo borré" también es una decisión, y tiene un costo que hay que anotar.
3. **El orden importa.** Algunas reglas cambian el resultado según se apliquen antes o después de otras, o antes o después de un join. Pensalo antes de escribir el SQL.
4. **`int_order_items_enriched`**: una fila por línea de pedido válida, con lo que necesitan los marts del pedido, del producto y del cliente.
5. **Tests estrictos de int.** Lo que en stg avisaba, en int tiene que pasar en verde con severidad `error`. Sumá el test singular de `tests/README.md` (sin pedidos duplicados ni items con `quantity` en cero).

```sql
-- Explorar en DuckDB (desde Python o desde la CLI de duckdb)
summarize stg.stg_orders;
select status, count(*) from stg.stg_orders group by 1 order by 2 desc;
```

## Cómo saber que quedó

- `python run.py build` termina **sin errores**. Puede haber avisos (`WARN`) de stg, pero cada uno tiene que estar explicado en `docs/decisiones.md`.
- Los modelos stg e int ya no tienen `tags=['todo']` y el CI está en verde.

## Si se rompe

| Síntoma | Qué mirar |
|---|---|
| Aparecen schemas `main_stg` o `main_int` | No se está usando `macros/generate_schema_name.sql`. No lo borres |
| `Compilation Error ... source not found` | El nombre en `source('raw', '...')` no coincide con `_sources.yml` |
| `dbt build` saltea int y mart ("SKIP") | Un test de stg falló con severidad error. Releé "Tests que fallan" |
| Una fecha quedó nula | Tu casteo no entiende todos los formatos de esa columna |

## Checkpoint

1. ¿Por qué stg no deduplica ni filtra, si sería más cómodo hacerlo ahí?
2. Contá un problema que encontraste en los datos, qué regla aplicaste y qué habría pasado en las ventas si no lo resolvías.
3. ¿Qué cambia entre un test con `severity: warn` en stg y uno con `error` en int?

<details>
<summary>Respuestas de referencia</summary>

1. Porque stg es un contrato simple: "esto es raw, pero con tipos". Si empieza a tener lógica, ya no sabés dónde vive cada regla. Toda la limpieza junta en int se puede leer, testear y discutir en un solo lugar.
2. Depende de lo que encontraste. Una buena respuesta tiene las tres partes: qué viste (con la cantidad de filas), qué decidiste y el impacto en un número del tablero. Por ejemplo, un pedido repetido que se une con sus items hace que esas ventas cuenten dos veces.
3. El warn de stg documenta que el dato de origen viene con ese problema, sin frenar el build. El error en int garantiza que tu limpieza lo resolvió: si algún día el problema vuelve a pasar a int, el build se frena antes de llegar al tablero.

</details>

<details>
<summary>Números de control</summary>

🔜 Los publicamos cuando terminemos de validar el proyecto: filas de stg (iguales a raw), cantidad de avisos esperados en stg y filas de `int_order_items_enriched`.

</details>
