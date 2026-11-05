{#
  Por defecto dbt arma el schema como <schema del target>_<schema del modelo> (ej: main_stg).
  Esta versión usa el schema del modelo tal cual, así las capas se llaman raw, stg, int y mart
  como datasets de BigQuery.
#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
