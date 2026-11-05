# La semana, día por día

Cinco días de trabajo y un fin de semana para cerrar. Cada día tiene un objetivo, los pasos, cómo saber que quedó y un **checkpoint**: tres preguntas que tenés que poder responder sin mirar el código. Si no te salen, el día no terminó.

| Día | Qué hacés | Entregás |
|---|---|---|
| [Día 1](dia-1.md) | Entender el problema antes de tocar código | Requerimiento, tickets y diagrama del flujo |
| [Día 2](dia-2.md) | Traer los datos de la API a raw | `ingestion/extract_load.py` funcionando |
| [Día 3](dia-3.md) | Ordenar (stg) y limpiar (int) | Modelos stg e int con sus tests |
| [Día 4](dia-4.md) | Responder las preguntas de negocio | Los 3 marts, tests y documentación de dbt |
| [Día 5](dia-5.md) | Mostrar y automatizar | Dashboard y scheduler diario |
| [Fin de semana](fin-de-semana.md) | Contarlo | README y `docs/story.md` |
| [Carril nube](carril-nube.md) | El mismo proyecto en BigQuery | Opcional, cuando terminaste lo anterior |

## Cómo usar los checkpoints

Las respuestas de referencia y los números de control están plegados. Abrilos **después** de intentar responder: la gracia es descubrir qué no entendiste mientras todavía estás a tiempo de arreglarlo.

## Cómo saber cuánto avanzaste

Cada modelo que todavía no hiciste tiene la línea `{{ config(tags=['todo']) }}`. El CI (`.github/workflows/ci.yml`) deja afuera todo lo que tiene ese tag. Cuando terminás un modelo, le borrás esa línea: desde ese momento entra al CI y tiene que pasar en verde. Al final de la semana no tiene que quedar ningún `todo`.

```bash
# ¿Cuánto me falta?
grep -rl "tags=\['todo'\]" dbt_project/models
```
