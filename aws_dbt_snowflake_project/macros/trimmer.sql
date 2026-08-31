{% macro trimmer(column_name,node) %}
    {{column_name | trim | upper }}
  {# {{ return(trim(column_name)) }} #}
{% endmacro %}