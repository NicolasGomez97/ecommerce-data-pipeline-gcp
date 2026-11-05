{{ config(tags=['todo']) }}
-- TODO (día 3): stg_customers
-- Espejo 1 a 1 de raw.customers: una fila de stg por cada fila de raw.
-- Nombres de columna consistentes y tipos casteados (ids a entero, fechas a fecha).
-- Sin filtros, sin deduplicar y sin joins: eso es trabajo de int.
-- Leé raw con source(), nunca con el nombre de la tabla escrito a mano.
-- Cuando termines, borrá la línea del config(tags=['todo']) para que el modelo entre al CI.
select 1 as pendiente
