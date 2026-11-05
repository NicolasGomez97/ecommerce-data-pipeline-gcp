"""Atajos del proyecto. Funcionan igual en Windows, Mac y Linux (no hace falta make).

    python run.py setup        copia .env y profiles.yml de ejemplo (una sola vez) y prueba la conexión
    python run.py ingest       ingesta: API -> BigQuery raw
    python run.py build        dbt build en BigQuery (modelos + tests)
    python run.py run          el flujo completo: ingesta, frescura de raw y dbt build
    python run.py docs         genera la documentación de dbt y la abre en el navegador
    python run.py dashboard    abre el dashboard de Streamlit
    python run.py check        lint, formato, tests y dbt parse (lo mismo que corre GitHub Actions)

Opción: --source auto|api|csv (default auto).
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
DBT_DIR = RAIZ / "dbt_project"


def preparar_entorno() -> None:
    """Carga .env y deja a dbt mirando el profiles.yml de este proyecto."""
    os.environ["PYTHONIOENCODING"] = "utf-8"  # acentos legibles también en la ingesta (proceso hijo)
    try:
        from dotenv import load_dotenv

        load_dotenv(RAIZ / ".env")
    except ImportError:
        pass
    os.environ["DBT_PROFILES_DIR"] = str(DBT_DIR)
    os.environ["DBT_PROJECT_DIR"] = str(DBT_DIR)


def dbt(*args: str) -> bool:
    from dbt.cli.main import dbtRunner

    print(f"\n$ dbt {' '.join(args)}")
    resultado = dbtRunner().invoke([*args, "--project-dir", str(DBT_DIR), "--profiles-dir", str(DBT_DIR)])
    return resultado.success


def ingest(source: str) -> int:
    cmd = [sys.executable, str(RAIZ / "ingestion" / "extract_load.py"), "--source", source]
    print(f"\n$ python ingestion/extract_load.py --source {source}")
    return subprocess.call(cmd, cwd=RAIZ)


def comando(*cmd: str) -> bool:
    print(f"\n$ {' '.join(cmd)}")
    return subprocess.call([sys.executable, "-m", *cmd], cwd=RAIZ) == 0


def setup() -> None:
    for ejemplo, destino in [
        (RAIZ / ".env.example", RAIZ / ".env"),
        (DBT_DIR / "profiles.yml.example", DBT_DIR / "profiles.yml"),
    ]:
        if destino.exists():
            print(f"= {destino.relative_to(RAIZ)} ya existe, no lo toco")
        else:
            shutil.copy(ejemplo, destino)
            print(f"+ creado {destino.relative_to(RAIZ)}")
    preparar_entorno()
    ok = dbt("debug")
    print("\nListo." if ok else "\nRevisá el error de arriba: casi siempre es una variable de .env.")


def check() -> bool:
    """Validaciones sin credenciales: no se conecta ni a la API ni a BigQuery."""
    # dbt parse solo renderiza el profile, no abre conexión: alcanza con un proyecto de relleno.
    os.environ.setdefault("GCP_PROJECT", "sin-conexion")
    pasos = [
        lambda: comando("ruff", "check", "."),
        lambda: comando("ruff", "format", "--check", "."),
        lambda: comando("pytest"),
        lambda: dbt("parse"),
    ]
    return all(paso() for paso in pasos)  # all() corta en el primer paso que falla


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # la consola de Windows no siempre usa UTF-8
    parser = argparse.ArgumentParser(description="Atajos del proyecto de datos")
    parser.add_argument("comando", choices=["setup", "ingest", "build", "run", "docs", "dashboard", "check"])
    parser.add_argument("--source", choices=["auto", "api", "csv"], default="auto")
    args = parser.parse_args()

    if args.comando == "setup":
        setup()
        return
    preparar_entorno()

    if args.comando == "ingest":
        sys.exit(ingest(args.source))

    if args.comando == "build":
        sys.exit(0 if dbt("build") else 1)

    if args.comando == "run":
        codigo = ingest(args.source)
        if codigo != 0:
            sys.exit(codigo)
        if not dbt("source", "freshness"):
            sys.exit("raw no está fresca o hay un error en las sources (ver arriba).")
        sys.exit(0 if dbt("build") else 1)

    if args.comando == "docs":
        if dbt("docs", "generate"):
            dbt("docs", "serve")
        return

    if args.comando == "dashboard":
        sys.exit(
            subprocess.call([sys.executable, "-m", "streamlit", "run", str(RAIZ / "dashboard" / "app.py")], cwd=RAIZ)
        )

    if args.comando == "check":
        sys.exit(0 if check() else 1)


if __name__ == "__main__":
    main()
