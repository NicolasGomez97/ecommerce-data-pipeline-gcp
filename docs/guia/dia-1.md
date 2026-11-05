# Día 1 · Entender el problema antes de tocar código

**Objetivo:** saber qué vas a construir, para qué y cómo te vas a dar cuenta de que terminaste.
**Tiempo estimado:** 3 a 4 horas.
**Entregás:** `tickets/requerimiento.md`, un ticket por tarea en `tickets/` y `docs/diagrama.md`.

En un trabajo de verdad nadie te da el SQL: te dan una pregunta de negocio. El primer día es para convertir esa pregunta en un plan. Parece tiempo perdido, y es el que más se nota en una entrevista.

## El pedido

Una tienda online quiere un tablero que responda tres preguntas:

1. ¿Cómo evolucionan las ventas por mes y por canal?
2. ¿Qué categorías y productos dejan más margen?
3. ¿Qué clientes compran de nuevo y cuánto valen?

Los datos están en 4 tablas (`customers`, `products`, `orders`, `order_items`) detrás de una API de solo lectura. El dato tiene que pasar por cuatro capas antes de llegar al tablero:

| Capa | La crea | Qué tiene |
|---|---|---|
| raw | Tu script de Python | Copia fiel de lo que devuelve la API, más `_loaded_at` |
| stg | dbt | Lo mismo que raw, con nombres consistentes y tipos correctos. Sin joins ni lógica |
| int | dbt | La limpieza y los joins entre tablas |
| mart | dbt | Tablas listas para el tablero. Es lo único que lee el dashboard |

**Ventas netas** = suma de `quantity * unit_price * (1 - discount)` sobre pedidos que no estén cancelados ni devueltos. El descuento es una proporción entre 0 y 1.

## Pasos

1. **Instalá el proyecto** siguiendo el README hasta que `python run.py setup` diga "All checks passed". Si se traba, mirá "Si se rompe" al final de esta página.
2. **Escribí el requerimiento en tus palabras.** Copiá `tickets/_plantilla_requerimiento.md` como `tickets/requerimiento.md` y completalo. No copies el pedido de arriba: explicalo como se lo explicarías a alguien que no lo leyó.
3. **Partilo en tickets.** Una tarea por ticket (`tickets/_plantilla_ticket.md`), con criterios de aceptación que se puedan verificar. Pista: si un ticket no se puede terminar en una tarde, es muy grande.
4. **Dibujá el flujo** en `docs/diagrama.md`, desde la API hasta el dashboard. Tiene que aparecer dónde vive cada capa y qué herramienta la crea.
5. **Mirá los datos sin escribir código todavía.** Abrí los CSV de `data/seed/` (son una copia de lo que devuelve la API). Anotá lo que te llame la atención: lo vas a necesitar el día 3.

## Cómo saber que quedó

- Alguien que no leyó el pedido entiende qué vas a construir leyendo solo tu `requerimiento.md`.
- Cada ticket tiene al menos un criterio que se puede chequear con un sí o un no.
- En tu diagrama se ve qué parte hace Python y qué parte hace dbt.

## Si se rompe

| Síntoma | Qué mirar |
|---|---|
| `python` no se reconoce | Instalá Python 3.11 o 3.12 desde python.org y, en Windows, tildá "Add python.exe to PATH" |
| `pip install` falla con un error de compilación | Tu Python es muy nuevo o muy viejo: usá 3.11 o 3.12 |
| `dbt debug` dice que no encuentra `profiles.yml` | Corré `python run.py setup` desde la raíz del proyecto, no desde otra carpeta |
| No reconoce `make` | En Windows no viene instalado. Usá `python run.py <comando>`: hace lo mismo |

## Checkpoint

1. ¿Por qué raw y stg son capas distintas si tienen las mismas filas?
2. ¿Por qué el dashboard lee solo de mart y no de int?
3. Un pedido devuelto, ¿suma en las ventas netas? ¿Y en la cantidad de pedidos de un cliente? Justificá.

<details>
<summary>Respuestas de referencia</summary>

1. raw es la copia fiel de lo que llegó: si mañana algo sale mal, ahí está la prueba de qué mandó el origen. stg es el primer lugar donde el dato tiene nombres y tipos confiables. Separarlas te deja ver la frontera entre lo que trajo Python y lo que transformó dbt.
2. Porque mart es el contrato con quien consume: si cambiás cómo limpiás en int, el tablero no se entera mientras el mart mantenga sus columnas. Si el dashboard leyera int, cada cambio interno rompería el tablero.
3. En ventas netas no, por definición. En la cantidad de pedidos depende de lo que quieras medir, y por eso hay que decidirlo y escribirlo: no hay una respuesta "obvia". Lo importante es que la decisión esté en `docs/decisiones.md` y sea la misma en todos los marts.

</details>
