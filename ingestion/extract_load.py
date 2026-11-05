"""Ingesta: baja las 4 tablas de la API y las carga tal cual en el dataset raw de BigQuery.

Uso:
    python ingestion/extract_load.py                 # API y, si falla, CSV de respaldo
    python ingestion/extract_load.py --source api    # solo API: si falla, corta con error
    python ingestion/extract_load.py --source csv    # sin API: usa data/seed/

Configuración (.env): API_URL, API_TOKEN, GCP_PROJECT, BQ_LOCATION y GOOGLE_APPLICATION_CREDENTIALS.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import time
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parent.parent
SEED = RAIZ / "data" / "seed"

TABLAS = ["customers", "products", "orders", "order_items"]
LIMITE_PAGINA = 1000  # máximo que acepta la API por pedido

# Regla de tipos de la API (api/main.py): una columna es numérica solo si TODOS sus valores lo son.
ENTERO = re.compile(r"-?(0|[1-9]\d*)")
DECIMAL = re.compile(r"-?(0|[1-9]\d*)\.\d+")


def leer_api(tabla: str, api_url: str, token: str) -> pd.DataFrame:
    """Baja una tabla completa de la API, página por página.

    - Pagina con limit/offset hasta tener `total` filas o recibir una página incompleta.
    - Ante un 429 espera lo que indica Retry-After y repite el mismo pedido (sin avanzar el offset).
    - Cualquier otro error HTTP (401, 404, 5xx) corta con una excepción.
    - Verifica al final que la cantidad de filas sea exactamente `total`.
    """
    url = f"{api_url.rstrip('/')}/tables/{tabla}"
    headers = {"Authorization": f"Bearer {token}"}
    offset = 0
    filas: list[dict] = []
    total: int | None = None

    while True:
        r = requests.get(url, headers=headers, params={"limit": LIMITE_PAGINA, "offset": offset}, timeout=30)

        if r.status_code == 429:
            espera = float(r.headers.get("Retry-After", 1))
            print(f"  {tabla}: 429, espero {espera:g}s y reintento offset={offset}")
            time.sleep(espera)
            continue  # mismo pedido: el offset no avanza

        r.raise_for_status()
        datos = r.json()
        total = datos["total"]
        pagina = datos["rows"]
        filas.extend(pagina)
        offset += LIMITE_PAGINA

        # Una página incompleta es la última (la de order_items trae 865):
        # pedir otra sería un viaje de más.
        if len(filas) >= total or len(pagina) < LIMITE_PAGINA:
            break

    if len(filas) != total:
        raise RuntimeError(f"{tabla}: se bajaron {len(filas)} filas pero la API dice total={total}")

    return pd.DataFrame(filas)


def leer_csv(tabla: str) -> pd.DataFrame:
    """Lee data/seed/{tabla}.csv y devuelve exactamente el mismo DataFrame que leer_api.

    Todo se lee como texto y los tipos se infieren con la misma regla que la API,
    para que valores como "007" no se conviertan en número de un lado y no del otro.
    """
    crudo = pd.read_csv(SEED / f"{tabla}.csv", dtype=str, keep_default_na=False, encoding="utf-8-sig")
    columnas = {nombre: _convertir_columna(crudo[nombre].tolist()) for nombre in crudo.columns}
    # Armado igual que leer_api (lista de dicts) para que pandas infiera los mismos dtypes.
    filas = [{nombre: valores[i] for nombre, valores in columnas.items()} for i in range(len(crudo))]
    return pd.DataFrame(filas, columns=list(crudo.columns))


def _convertir_columna(valores: list[str]) -> list[str | int | float | None]:
    """Vacío -> None; la columna es numérica solo si TODOS los valores presentes lo son."""
    presentes = [v for v in valores if v != ""]
    if presentes and all(ENTERO.fullmatch(v) for v in presentes):
        convertir = int
    elif presentes and all(ENTERO.fullmatch(v) or DECIMAL.fullmatch(v) for v in presentes):
        convertir = float
    else:
        convertir = str
    return [None if v == "" else convertir(v) for v in valores]


def escribir_bigquery(tablas: dict[str, pd.DataFrame]) -> None:
    """Carga cada DataFrame en {GCP_PROJECT}.raw.{tabla}, reemplazando la tabla completa."""
    from google.cloud import bigquery

    proyecto = os.environ["GCP_PROJECT"]
    ubicacion = os.environ.get("BQ_LOCATION", "US")
    # Sin credenciales explícitas: la librería las toma de GOOGLE_APPLICATION_CREDENTIALS
    # (o de `gcloud auth application-default login` si esa variable no está).
    client = bigquery.Client(project=proyecto, location=ubicacion)

    dataset = bigquery.Dataset(f"{proyecto}.raw")
    dataset.location = ubicacion
    dataset = client.create_dataset(dataset, exists_ok=True)
    # exists_ok no avisa si el dataset ya existía en otra región: dbt fallaría después
    # con "Dataset not found in location". Mejor cortar acá con un mensaje claro.
    if dataset.location != ubicacion:
        raise RuntimeError(f"El dataset raw está en {dataset.location}, no en {ubicacion} (BQ_LOCATION)")

    # Load job (no insert_rows) que reemplaza datos y schema: correr dos veces no duplica filas.
    job_config = bigquery.LoadJobConfig(write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE)
    for tabla, df in tablas.items():
        tabla_id = f"{proyecto}.raw.{tabla}"
        job = client.load_table_from_dataframe(df, tabla_id, job_config=job_config)
        job.result()  # el job es asíncrono: espero a que termine (y si falló, el error sale acá)
        print(f"  {tabla_id}: {job.output_rows} filas")


def leer_todas(origen: str, api_url: str, token: str) -> dict[str, pd.DataFrame]:
    """Lee las 4 tablas desde un mismo origen ("api" o "csv") e informa filas y segundos por tabla."""
    tablas: dict[str, pd.DataFrame] = {}
    for tabla in TABLAS:
        inicio = time.perf_counter()
        df = leer_api(tabla, api_url, token) if origen == "api" else leer_csv(tabla)
        print(f"  {tabla:<12} {len(df):>6} filas  origen={origen}  {time.perf_counter() - inicio:6.2f}s")
        tablas[tabla] = df
    return tablas


def elegir_y_leer(source: str, api_url: str, token: str) -> dict[str, pd.DataFrame]:
    """Decide el origen una sola vez para toda la corrida y devuelve las 4 tablas.

    Con "auto", si la API falla en cualquier tabla se releen las 4 del CSV:
    así raw nunca mezcla una foto de la API con otra del CSV.
    """
    if source == "csv":
        return leer_todas("csv", api_url, token)
    if source == "api":
        if not token:
            sys.exit("Error: --source api pero falta API_TOKEN en .env")
        return leer_todas("api", api_url, token)  # cualquier error corta la corrida
    if not (api_url and token):
        print("Aviso: falta API_URL o API_TOKEN en .env; uso los CSV de data/seed/")
        return leer_todas("csv", api_url, token)
    try:
        return leer_todas("api", api_url, token)
    except (requests.RequestException, RuntimeError, KeyError, ValueError) as error:
        print(f"Aviso: la API falló ({error}); uso los CSV de data/seed/ para todas las tablas")
        return leer_todas("csv", api_url, token)


def main() -> None:
    load_dotenv(RAIZ / ".env")
    parser = argparse.ArgumentParser(description="Ingesta API -> BigQuery raw")
    parser.add_argument("--source", choices=["auto", "api", "csv"], default="auto")
    args = parser.parse_args()

    api_url, token = os.environ.get("API_URL", ""), os.environ.get("API_TOKEN", "")

    # Un único instante para toda la corrida, con zona horaria (BigQuery lo guarda como TIMESTAMP).
    loaded_at = pd.Timestamp.now(tz="UTC")
    tablas = elegir_y_leer(args.source, api_url, token)
    for df in tablas.values():
        df["_loaded_at"] = loaded_at

    print(f"Cargando en BigQuery (_loaded_at={loaded_at.isoformat()})")
    escribir_bigquery(tablas)
    print("Listo.")


if __name__ == "__main__":
    main()
