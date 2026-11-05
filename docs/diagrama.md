# Diagrama del flujo

El dato sale de los CSV de origen, lo sirve una API con autenticación y límite de pedidos, lo baja la ingesta en Python y lo carga en BigQuery. De `raw` en adelante, todo lo transforma dbt con SQL que corre dentro de BigQuery.

```mermaid
flowchart LR
    subgraph Origen
        CSV[("data/seed<br/>4 CSV")]
        API["API FastAPI<br/>Bearer token · 30 pedidos/min"]
    end

    subgraph Ingesta["Ingesta · Python"]
        EL["extract_load.py<br/>paginación · reintento 429<br/>respaldo CSV · _loaded_at"]
    end

    subgraph BQ["BigQuery · US"]
        RAW[("raw<br/>4 tablas")]
        STG["stg<br/>4 vistas"]
        INT["int<br/>order_items_enriched"]
        MART[("mart<br/>3 tablas")]
    end

    DASH["Dashboard<br/>Streamlit"]

    CSV -->|carga al iniciar| API
    API -->|GET /tables paginado| EL
    CSV -.->|respaldo si la API falla| EL
    EL -->|load job WRITE_TRUNCATE| RAW
    RAW -->|source + freshness| STG
    STG --> INT
    INT --> MART
    MART -->|consultas SQL| DASH

    classDef pendiente stroke-dasharray: 5 5
    class STG,INT,MART,DASH pendiente
```

Los nodos punteados están en desarrollo (ver el estado en el [README](../README.md#estado-del-proyecto)).

| Capa | Dónde vive | Quién la crea | Materialización |
|---|---|---|---|
| `raw` | BigQuery, dataset `raw` | `ingestion/extract_load.py` (Python) | Tablas, reemplazadas en cada corrida |
| `stg` | BigQuery, dataset `stg` | dbt | Vistas: espejo 1 a 1 de `raw` con tipos casteados |
| `int` | BigQuery, dataset `int` | dbt | Vista: limpieza y joins |
| `mart` | BigQuery, dataset `mart` | dbt | Tablas: una por pregunta de negocio |
| Dashboard | Streamlit | `dashboard/app.py` | Lee solo `mart` |

## Adentro de la ingesta

```mermaid
flowchart LR
    GET["GET /tables/{t}<br/>limit=1000 · offset"] --> S{status}
    S -->|429| W["sleep(Retry-After)"]
    W -->|mismo offset| GET
    S -->|401 · 404 · 5xx| E["raise_for_status: corta"]
    S -->|200| A["filas += rows<br/>offset += 1000"]
    A --> C{"¿total alcanzado o<br/>página &lt; 1000?"}
    C -->|no| GET
    C -->|sí| T{"¿filas == total?"}
    T -->|sí| OK["DataFrame"]
    T -->|no| ERR["RuntimeError"]
```
