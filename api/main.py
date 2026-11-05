"""API de lectura propia: sirve los CSV de data/seed con el contrato que espera la ingesta.

Simula el origen de datos para poder probar paginación, autenticación y límite de pedidos.
Los datos se sirven tal cual, con sus problemas: limpiarlos es trabajo de dbt, no de la API.

Levantarla, desde la raíz del proyecto:
    python -m uvicorn api.main:app --port 8000

Configuración (.env):
    API_TOKEN                   token que se exige en Authorization: Bearer (obligatorio)
    API_RATE_LIMIT_POR_MINUTO   pedidos por minuto antes de responder 429 (default 30)
"""

from __future__ import annotations

import csv
import math
import os
import re
import secrets
import time
from collections import deque
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, Query

RAIZ = Path(__file__).resolve().parent.parent
SEED = RAIZ / "data" / "seed"
TABLAS = ["customers", "products", "orders", "order_items"]
VENTANA_SEGUNDOS = 60

ENTERO = re.compile(r"-?(0|[1-9]\d*)")
DECIMAL = re.compile(r"-?(0|[1-9]\d*)\.\d+")

load_dotenv(RAIZ / ".env")
TOKEN = os.environ.get("API_TOKEN", "").strip()
if not TOKEN:
    raise RuntimeError("Falta API_TOKEN en .env: es el token que va a exigir esta API.")
LIMITE_POR_MINUTO = int(os.environ.get("API_RATE_LIMIT_POR_MINUTO", "30"))


def convertir_columna(valores: list[str]) -> list[str | int | float | None]:
    """Vacío pasa a null. La columna es numérica solo si TODOS sus valores lo son."""
    presentes = [v for v in valores if v != ""]
    if presentes and all(ENTERO.fullmatch(v) for v in presentes):
        convertir = int
    elif presentes and all(ENTERO.fullmatch(v) or DECIMAL.fullmatch(v) for v in presentes):
        convertir = float
    else:
        convertir = str
    return [None if v == "" else convertir(v) for v in valores]


def cargar_tabla(tabla: str) -> list[dict]:
    with open(SEED / f"{tabla}.csv", encoding="utf-8-sig", newline="") as archivo:
        filas = list(csv.DictReader(archivo))
    if not filas:
        return []
    columnas = {nombre: convertir_columna([fila[nombre] for fila in filas]) for nombre in filas[0]}
    return [{nombre: valores[i] for nombre, valores in columnas.items()} for i in range(len(filas))]


DATOS = {tabla: cargar_tabla(tabla) for tabla in TABLAS}
pedidos_recientes: deque[float] = deque()

app = FastAPI(title="API de datos e-commerce", version="1.0.0")


def exigir_token(authorization: str | None = Header(default=None)) -> None:
    esquema, _, token = (authorization or "").partition(" ")
    if esquema.lower() != "bearer" or not secrets.compare_digest(token.strip().encode(), TOKEN.encode()):
        raise HTTPException(
            status_code=401,
            detail="Token inválido o ausente",
            headers={"WWW-Authenticate": "Bearer"},
        )


def aplicar_limite() -> None:
    """Ventana deslizante en memoria: alcanza para un solo proceso."""
    ahora = time.monotonic()
    while pedidos_recientes and ahora - pedidos_recientes[0] >= VENTANA_SEGUNDOS:
        pedidos_recientes.popleft()
    if len(pedidos_recientes) >= LIMITE_POR_MINUTO:
        espera = VENTANA_SEGUNDOS - (ahora - pedidos_recientes[0])
        raise HTTPException(
            status_code=429,
            detail="Demasiados pedidos",
            headers={"Retry-After": str(max(1, math.ceil(espera)))},
        )
    pedidos_recientes.append(ahora)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/tables/{tabla}", dependencies=[Depends(exigir_token), Depends(aplicar_limite)])
async def leer_tabla(
    tabla: str,
    limit: int = Query(default=1000, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
) -> dict:
    if tabla not in DATOS:
        raise HTTPException(status_code=404, detail=f"La tabla '{tabla}' no existe")
    filas = DATOS[tabla]
    return {
        "table": tabla,
        "total": len(filas),
        "limit": limit,
        "offset": offset,
        "rows": filas[offset : offset + limit],
    }
