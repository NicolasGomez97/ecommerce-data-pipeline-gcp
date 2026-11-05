{{ config(tags=['todo']) }}
-- TODO (día 4): mart_sales_monthly
-- Pregunta: ¿Cómo evolucionan las ventas por mes y por canal?
-- Granularidad: una fila por mes y canal.
-- Métricas: pedidos, unidades, ventas netas, ticket promedio.
-- Ventas netas = suma de quantity * unit_price * (1 - discount) sobre pedidos que no estén cancelados ni devueltos.
-- El descuento es una proporción entre 0 y 1.
-- Para truncar la fecha al mes usá la macro dbt.date_trunc(): corre igual en DuckDB y en BigQuery.
-- Cuando termines, borrá la línea del config(tags=['todo']).
select 1 as pendiente
