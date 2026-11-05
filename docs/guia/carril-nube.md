# Carril nube · El mismo proyecto en BigQuery

Hacelo **después** de terminar el carril local. La idea es mostrar que tu proyecto corre en la nube cambiando solo la conexión, sin tocar un modelo.

## 1. BigQuery sandbox (gratis, sin tarjeta)

1. Entrá a [console.cloud.google.com/bigquery](https://console.cloud.google.com/bigquery) con tu cuenta de Google y creá un proyecto nuevo. Usá uno propio: así nadie te rompe el trabajo, ni vos a nadie.
2. Sin activar la facturación quedás en el **sandbox**. Tiene tres límites que te importan:
   - Las tablas se borran solas a los **60 días**.
   - No acepta `INSERT`, `UPDATE` ni `MERGE` (DML) ni inserciones por streaming.
   - Tiene una cuota mensual gratis de consultas, que con este proyecto no vas a tocar.

## 2. Cuenta de servicio

1. En IAM → Cuentas de servicio, creá una (por ejemplo `dbt-proyecto`) con dos roles: **BigQuery Data Editor** y **BigQuery Job User**. Nada más.
2. Creale una clave JSON y guardala **fuera** del repo.
3. Completá en `.env`: `GCP_PROJECT`, `BQ_LOCATION=US` y `GOOGLE_APPLICATION_CREDENTIALS` con la ruta al JSON.

Si ya usás `gcloud`, podés evitar la clave: corré `gcloud auth application-default login` y poné `BQ_METHOD=oauth` en `.env`.

## 3. Ingesta a BigQuery

Completá `escribir_bigquery` en `ingestion/extract_load.py`. Tiene que crear el dataset `raw` si no existe y reemplazar cada tabla en cada corrida. Pista: por los límites del sandbox, `insert_rows` no te va a servir. Buscá cómo cargar un DataFrame con un *load job*.

```bash
python run.py run --target bq
```

## 4. dbt contra BigQuery

El target `bq` ya está en `dbt_project/profiles.yml`. Si tus modelos usan las macros multi-base, `dbt build --target bq` corre sin cambios. Si algo falla, casi siempre es una función propia de DuckDB que se coló en un modelo: pasala por una macro.

Al terminar tenés que ver los datasets `raw`, `stg`, `int` y `mart`, con esos nombres exactos, y los mismos números que en local.

## 5. Looker Studio

1. Entrá a [lookerstudio.google.com](https://lookerstudio.google.com) → Crear → Fuente de datos → BigQuery.
2. Conectá **solo** las tablas del dataset `mart`.
3. Armá las tres visuales con la pregunta como título y un control de fecha.

## Si se rompe

| Síntoma | Qué mirar |
|---|---|
| `Dataset not found in location` | La ubicación de la ingesta y la de `profiles.yml` no coinciden. Usá la misma (`US`) |
| `Access Denied` | A la cuenta de servicio le falta uno de los dos roles |
| `DML statements are not allowed in the sandbox` | Estás usando una materialización incremental o un `insert`. En el sandbox, tablas completas |

## Paso siguiente (avanzado)

Correr `dbt build --target bq` en cada push a main con Cloud Build. Requiere activar la facturación: fuera del sandbox, con costo. No es parte del proyecto.
