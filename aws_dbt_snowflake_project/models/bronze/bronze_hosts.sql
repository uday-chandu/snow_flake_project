{{ config(materialized='incremental') }}

select * from {{ source('staging', 'hosts') }}
{% if is_incremental() %}
where created_at > (select coalesce(max(created_at), '1900-01-01') from {{ this }})
{% endif %}

{# {% set incremental_flag=1 %}
{% set incremental_column='created_at' %}

select * from {{ source('staging', 'hosts') }}
{% if incremental_flag == 1 %}
where {{ incremental_column }} > (select coalesce(max({{ incremental_column }}), '1900-01-01') from {{ ref('bronze_hosts') }})
{% endif %} #}



{# select * from {{ source('staging', 'listings') }} #}