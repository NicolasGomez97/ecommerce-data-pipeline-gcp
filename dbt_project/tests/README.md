# Tests singulares

Un test singular es un `.sql` en esta carpeta que devuelve las filas que **rompen** una regla. Si devuelve 0 filas, pasa.

TODO:
- **Día 3:** un test que verifique que en int no quedan pedidos duplicados ni items con `quantity` en cero.
- **Día 4:** un test de reconciliación: las ventas netas de cada mart tienen que coincidir con las calculadas desde int.

Documentación: https://docs.getdbt.com/docs/build/data-tests#singular-data-tests
