"""Dashboard: responde las tres preguntas de negocio leyendo SOLO el dataset mart de BigQuery.

Correlo con: python run.py dashboard
"""

import os
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from google.cloud import bigquery

RAIZ = Path(__file__).resolve().parent.parent
load_dotenv(RAIZ / ".env")
PROYECTO = os.environ.get("GCP_PROJECT", "")
UBICACION = os.environ.get("BQ_LOCATION", "US")

st.set_page_config(page_title="Proyecto de datos", layout="wide")


@st.cache_resource
def conectar() -> bigquery.Client:
    # Credenciales: GOOGLE_APPLICATION_CREDENTIALS (o gcloud application-default login).
    return bigquery.Client(project=PROYECTO, location=UBICACION)


@st.cache_data(ttl=600)
def consultar(sql: str) -> pd.DataFrame:
    """Corre una consulta en BigQuery. Cacheada 10 minutos para no repetir el costo en cada interacción."""
    return conectar().query(sql).to_dataframe()


if not PROYECTO:
    st.warning("Falta GCP_PROJECT en .env.")
    st.stop()

st.title("Proyecto de datos")

# TODO (día 5): filtro por fecha (st.date_input o st.slider) que afecte a las visuales.

# TODO (día 5): visual 1, leyendo de `{PROYECTO}.mart.mart_sales_monthly`
st.header("¿Cómo evolucionan las ventas por mes y por canal?")
st.info("Pendiente (día 5)")

# TODO (día 5): visual 2, leyendo de `{PROYECTO}.mart.mart_product_performance`
st.header("¿Qué categorías y productos dejan más margen?")
st.info("Pendiente (día 5)")

# TODO (día 5): visual 3, leyendo de `{PROYECTO}.mart.mart_customer_value`
st.header("¿Qué clientes compran de nuevo y cuánto valen?")
st.info("Pendiente (día 5)")
