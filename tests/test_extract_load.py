"""Tests de la ingesta. No usan red ni BigQuery: la API se simula reemplazando requests.get."""

from __future__ import annotations

import json
import os
from unittest import mock

import extract_load as el
import pandas as pd
import pytest
import requests

TOTALES = {"customers": 1000, "products": 80, "orders": 8025, "order_items": 19865}


class RespuestaFalsa:
    def __init__(self, status: int, cuerpo: dict | None = None, headers: dict | None = None):
        self.status_code = status
        self._cuerpo = cuerpo or {}
        self.headers = headers or {}

    def json(self) -> dict:
        return self._cuerpo

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} Error")


def api_falsa(total: int, filas_reales: int | None = None, fallas: dict[int, RespuestaFalsa] | None = None):
    """Devuelve (get, offsets): un requests.get falso que pagina `total` filas y la lista de offsets pedidos.

    `filas_reales` permite que la API anuncie un total distinto de lo que entrega.
    `fallas` mapea un offset a una respuesta de error que se devuelve una sola vez.
    """
    filas_reales = total if filas_reales is None else filas_reales
    fallas = dict(fallas or {})
    offsets: list[int] = []

    def get(url, headers, params, timeout):
        offset, limit = params["offset"], params["limit"]
        offsets.append(offset)
        if offset in fallas:
            return fallas.pop(offset)
        rows = [{"id": i} for i in range(offset, min(offset + limit, filas_reales))]
        return RespuestaFalsa(200, {"total": total, "limit": limit, "offset": offset, "rows": rows})

    return get, offsets


def test_pagina_hasta_la_ultima_pagina_incompleta():
    get, offsets = api_falsa(total=2865)
    with mock.patch.object(requests, "get", get):
        df = el.leer_api("order_items", "http://api", "token")
    assert len(df) == 2865
    assert offsets == [0, 1000, 2000]  # la página de 865 cierra el loop: no hay un pedido vacío de más


def test_429_espera_retry_after_y_repite_el_mismo_offset():
    get, offsets = api_falsa(total=2500, fallas={1000: RespuestaFalsa(429, headers={"Retry-After": "7"})})
    with mock.patch.object(requests, "get", get), mock.patch.object(el.time, "sleep") as dormir:
        df = el.leer_api("orders", "http://api", "token")
    dormir.assert_called_once_with(7.0)
    assert offsets == [0, 1000, 1000, 2000]
    assert len(df) == 2500


def test_error_http_que_no_es_429_corta():
    get, _ = api_falsa(total=10, fallas={0: RespuestaFalsa(401)})
    with mock.patch.object(requests, "get", get), pytest.raises(requests.HTTPError):
        el.leer_api("customers", "http://api", "token-invalido")


def test_falla_si_las_filas_no_coinciden_con_total():
    get, _ = api_falsa(total=1500, filas_reales=1400)
    with mock.patch.object(requests, "get", get), pytest.raises(RuntimeError, match="total=1500"):
        el.leer_api("orders", "http://api", "token")


def test_regla_de_tipos_igual_a_la_api():
    assert el._convertir_columna(["1", "", "3"]) == [1, None, 3]
    assert el._convertir_columna(["1", "2.5"]) == [1.0, 2.5]
    assert el._convertir_columna(["007", "8"]) == ["007", "8"]  # "007" no es entero: toda la columna queda texto
    assert el._convertir_columna(["", ""]) == [None, None]


@pytest.mark.parametrize("tabla", el.TABLAS)
def test_leer_csv_devuelve_lo_mismo_que_la_api(tabla, monkeypatch):
    """Paridad real: la API sirve los mismos CSV con su propia regla de tipos y viaja como JSON."""
    monkeypatch.setenv("API_TOKEN", os.environ.get("API_TOKEN") or "token-de-test")
    from api import main as api

    filas_api = json.loads(json.dumps(api.DATOS[tabla]))  # ida y vuelta por JSON, como en la red

    def get(url, headers, params, timeout):
        o, lim = params["offset"], params["limit"]
        return RespuestaFalsa(200, {"total": len(filas_api), "limit": lim, "offset": o, "rows": filas_api[o : o + lim]})

    with mock.patch.object(requests, "get", get):
        desde_api = el.leer_api(tabla, "http://api", "token")
    desde_csv = el.leer_csv(tabla)

    pd.testing.assert_frame_equal(desde_api, desde_csv)
    assert len(desde_csv) == TOTALES[tabla]


def test_los_acentos_se_leen_bien():
    assert "Lámpara" in set(el.leer_csv("products")["name"])


def test_auto_cae_al_csv_para_todas_las_tablas_si_la_api_falla(capsys):
    with mock.patch.object(el, "leer_api", side_effect=requests.ConnectionError("sin red")) as leer_api:
        tablas = el.elegir_y_leer("auto", "http://api", "token")
    assert leer_api.call_count == 1  # falló en la primera tabla y no siguió insistiendo
    assert {t: len(df) for t, df in tablas.items()} == TOTALES
    assert "uso los CSV" in capsys.readouterr().out


def test_auto_sin_token_no_llama_a_la_api():
    with mock.patch.object(el, "leer_api") as leer_api:
        el.elegir_y_leer("auto", "http://api", "")
    leer_api.assert_not_called()
