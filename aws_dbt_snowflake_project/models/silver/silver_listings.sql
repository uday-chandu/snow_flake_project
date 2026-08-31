{{ 
    config(materialized='incremental', unique_key='listing_id') 
}}


select
    listing_id,
    host_id,
    property_type,
    room_type,
    city,
    bathrooms,
    bedrooms,
    country,
    accommodates,
    price_per_night,
    {{tag('price_per_night')}} as price_per_night_tag,
    created_at
from {{ref('bronze_listings')}}