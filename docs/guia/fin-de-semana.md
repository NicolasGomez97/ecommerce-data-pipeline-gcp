# Fin de semana · Contarlo

**Objetivo:** que otra persona pueda correr tu proyecto sin preguntarte nada, y que vos puedas contarlo en una entrevista en cinco minutos.
**Entregás:** tu `README.md` y `docs/story.md`.

## README

Reescribí el README con tus palabras. La prueba es simple: pasáselo a alguien y mirá si llega al dashboard sin preguntarte nada. Tiene que tener:

- Qué problema resuelve el proyecto (las tres preguntas).
- El diagrama del flujo (enlazá `docs/diagrama.md`).
- Cómo instalarlo y correrlo, paso a paso.
- Qué decisiones tomaste (enlazá `docs/decisiones.md`).
- Una captura del dashboard.

## story.md

Completá `docs/story.md`. Es tu guion para la entrevista, con cinco apartados:

1. **Contexto:** qué te pidieron y para qué.
2. **Decisiones que tomé:** las dos o tres más importantes, con la alternativa que descartaste.
3. **Qué se rompió:** algo concreto que salió mal.
4. **Cómo lo resolví:** cómo te diste cuenta y qué hiciste.
5. **Qué haría distinto:** con lo que sabés hoy.

El apartado que más pesa en una entrevista es "qué se rompió". Nadie le cree a un proyecto donde todo salió bien de entrada.

## Checkpoint

1. Contá el proyecto en dos minutos, sin mirar nada, a alguien que no sabe qué es dbt.
2. ¿Qué número del dashboard defenderías con tu vida, y por qué confiás en él?
3. ¿Qué parte del proyecto no está lista para producción, y qué le falta?

<details>
<summary>Respuestas de referencia</summary>

1. Una buena versión: "Una tienda quería saber X. Los datos venían de una API y tenían problemas. Los traje con Python, los limpié en capas con dbt y armé un tablero. Lo más difícil fue Y, y lo resolví así."
2. Las ventas netas, porque hay un test que reconcilia los tres marts contra int y corre en cada build. Confiar en un número es poder mostrar el test que lo prueba.
3. Algunas respuestas honestas: no hay alertas cuando falla el `daily`, la carga es completa todos los días (no incremental), y nadie revisa el código antes del merge. Saber nombrarlo vale más que fingir que está perfecto.

</details>
