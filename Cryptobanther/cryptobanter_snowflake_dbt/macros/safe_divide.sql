{% macro safe_divide(numerator, denominator, default=0) %}
    CASE
        WHEN {{ denominator }} IS NULL OR {{ denominator }} = 0 THEN {{ default }}
        ELSE {{ numerator }} / {{ denominator }}
    END
{% endmacro %}
