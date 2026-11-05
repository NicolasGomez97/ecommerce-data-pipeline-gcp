# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).

## [Sin publicar]

### Agregado
- Ingesta `API -> BigQuery raw` en `ingestion/extract_load.py`: paginación, reintento ante 429 con `Retry-After`, control de filas contra `total` y respaldo en CSV con los mismos tipos que la API.
- Columna `_loaded_at` (TIMESTAMP UTC, una por corrida) en todas las tablas de `raw`.
- Carga en BigQuery con load jobs `WRITE_TRUNCATE` y validación de la ubicación del dataset.
- Tests de la ingesta con pytest (12 casos, sin red).
- Lint y formato con ruff (`pyproject.toml`), auditoría de dependencias con pip-audit.
- Workflow de GitHub Actions: ruff, pytest, `dbt parse` y pip-audit en cada push a `main` y en cada pull request.
- `python run.py check` para correr las mismas validaciones localmente.
- Diagrama del flujo (`docs/diagrama.md`) y registro de decisiones técnicas (`docs/decisiones.md`).

### Cambiado
- El proyecto usa solo BigQuery: se quitó el carril DuckDB (dependencias, target de dbt y código).
- El dashboard se conecta a BigQuery en vez de a un archivo local.
- Streamlit 1.66.0 → 1.67.0 y Pillow fijado en 13.0.0 para cerrar 39 avisos de seguridad de Pillow 12.3.0.

### Pendiente
- Modelos dbt `stg`, `int` y `mart`, tests de datos y test de frescura de `raw`.
- Visualizaciones del dashboard.
