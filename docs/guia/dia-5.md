# Día 5 · Mostrar y automatizar

**Objetivo:** un dashboard que responda las tres preguntas leyendo solo de mart, y el flujo corriendo solo todos los días.
**Tiempo estimado:** 4 a 5 horas.
**Entregás:** `dashboard/app.py` sin TODOs y `.github/workflows/daily.yml` activado.

## Parte 1 · Dashboard

1. Abrilo con `python run.py dashboard`. Ya trae la conexión a DuckDB y los tres títulos.
2. **Una visual por pregunta**, con la pregunta como título. Elegí el gráfico que mejor responde cada una: una serie en el tiempo no se lee igual que un ranking.
3. **Filtro por fecha.** Pensá a qué visuales afecta y cómo, según la granularidad de cada mart. Si a alguna no la puede afectar, decilo en pantalla.
4. **Solo mart.** Ninguna consulta del dashboard lee `raw`, `stg` ni `int`. Verificalo:

```bash
grep -nE "raw\.|stg\.|int\." dashboard/app.py   # no tiene que devolver nada
```

5. Sacale una captura y guardala en `docs/dashboard.png`.

Si preferís otra herramienta (Power BI, Metabase, Looker Studio), vale, siempre que lea solo de los marts.

## Parte 2 · Scheduler

1. Seguí los pasos del comentario de arriba de `.github/workflows/daily.yml`: secretos en GitHub, descomentar el `schedule` y probarlo a mano.
2. El workflow corre lo mismo que `python run.py run`. Si local anda y en GitHub no, la diferencia casi siempre está en los secretos.
3. Nunca pongas el token en el archivo del workflow. Va en Settings → Secrets.

## Cómo saber que quedó

- El dashboard muestra las tres visuales y el filtro cambia lo que corresponde.
- En la pestaña Actions de tu repo hay una corrida de `daily` en verde.

## Si se rompe

| Síntoma | Qué mirar |
|---|---|
| `dbt build` falla con "Could not set lock on file" mientras el dashboard está abierto | La conexión del dashboard tiene que ser `read_only=True` (ya viene así: no la cambies) |
| El dashboard dice "Todavía no hay datos" | Corré `python run.py run` antes |
| `daily` falla con 401 | El secreto `API_TOKEN` no está cargado o tiene un espacio de más |

## Checkpoint

1. ¿Por qué la conexión del dashboard es de solo lectura?
2. ¿Qué visual no puede filtrarse por fecha tal como está el mart, y qué cambiarías para que sí?
3. ¿Dónde viven las credenciales cuando el flujo corre en GitHub Actions, y por qué no en el repo?

<details>
<summary>Respuestas de referencia</summary>

1. DuckDB admite un solo proceso escribiendo el archivo. Si el dashboard lo abre para escribir, `dbt build` no puede actualizar las tablas mientras el tablero está abierto.
2. La de productos, si el mart tiene una fila por producto sin fecha. Opciones: explicarlo en pantalla, o cambiar la granularidad del mart (producto × mes), lo que es una decisión de modelado que se anota en `decisiones.md`.
3. En GitHub Secrets. Todo lo que está en el repo lo puede ver cualquiera que tenga acceso, y queda en el historial aunque lo borres después.

</details>

<details>
<summary>Números de control</summary>

🔜 Los publicamos cuando terminemos de validar el proyecto: el total de ventas netas de 2026 que tiene que mostrar el dashboard sin filtros.

</details>
