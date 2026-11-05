# Día 4 · Responder las preguntas de negocio

**Objetivo:** los 3 marts construidos, con tests que prueben que los números cierran y la documentación de dbt generada.
**Tiempo estimado:** 4 a 6 horas.
**Entregás:** `mart_sales_monthly`, `mart_product_performance`, `mart_customer_value`, el test de reconciliación y `dbt docs`.

## Pasos

1. **Un mart por pregunta.** Cada archivo en `models/marts/` dice qué pregunta responde, su granularidad y sus métricas. Antes de escribir SQL, decidí qué es una fila de cada mart.
2. **Las definiciones van escritas.** En `models/marts/schema.yml`, describí cada mart y cada columna. La definición de ventas netas va textual: es lo primero que te van a preguntar cuando alguien no entienda un número.
3. **Funciones que cambian entre motores.** Truncar una fecha al mes no se escribe igual en DuckDB que en BigQuery. Usá las macros multi-base de dbt (`dbt.date_trunc`, `dbt.type_numeric` y otras) para que el mismo código corra en los dos carriles.
4. **Reconciliación.** Escribí el test singular de `tests/README.md`: las ventas netas de cada mart tienen que coincidir con las de int. Si no coinciden, algo se perdió o se duplicó en el camino. Ese test vale más que todos los demás juntos.
5. **Al menos 12 tests en verde** sumando las tres capas. Contá solo los de severidad `error`.
6. **Documentación:**

```bash
python run.py docs
```

Recorré el linaje (el gráfico de abajo a la derecha): tiene que verse el camino de cada mart hasta raw.

## Cómo saber que quedó

- `python run.py run` hace todo el flujo sin errores: ingesta, frescura y build.
- Ningún modelo tiene `tags=['todo']` y el CI está en verde.
- La suma de ventas netas da lo mismo en los 3 marts.

## Si se rompe

| Síntoma | Qué mirar |
|---|---|
| La reconciliación falla por poco | Redondeos. Compará con una tolerancia (por ejemplo 0,01) |
| La reconciliación falla por mucho | Un join que duplica filas o un filtro que se aplicó en un mart y no en otro |
| Un mart da más ventas que int | Estás uniendo algo de a muchos sin agrupar antes |
| El margen % da error de división | Productos sin ventas: dividir por cero. Mirá `nullif` |

## Checkpoint

1. ¿Qué es una fila de `mart_sales_monthly`? ¿Y de `mart_customer_value`?
2. ¿Qué prueba exactamente tu test de reconciliación, y qué problema detectaría que los demás tests no ven?
3. Si mañana el negocio decide que los pedidos pendientes tampoco cuentan como venta, ¿cuántos archivos cambiás y dónde?

<details>
<summary>Respuestas de referencia</summary>

1. Una combinación de mes y canal; un cliente. Si dudás, el `unique` sobre esas columnas te lo confirma.
2. Que ningún mart perdió ni duplicó ventas respecto de int. Detecta joins que multiplican filas y filtros aplicados en un solo mart, problemas en los que cada modelo "pasa" sus tests por separado.
3. Idealmente uno: la regla que define qué pedidos son válidos vive en int, y los tres marts la heredan. Si tenés que tocar los tres marts, la regla está repetida en el lugar equivocado.

</details>

<details>
<summary>Números de control</summary>

🔜 Los publicamos cuando terminemos de validar el proyecto: ventas netas totales, pedidos válidos y cantidad de tests en verde.

</details>
