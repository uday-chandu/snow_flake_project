{% macro multiply(x, y,precision) %}
    round({{x}} * {{y}}, {{precision}})
  {# {{ return(round(x * y, precision)) }} #}
{% endmacro %}