{# select * from {{ref('bronze_bookings')}} #}

{{
    config(
        materialized='incremental',
        unique_key='booking_id')
}}

select
    booking_id,
    listing_id,
    booking_date,
    {{multiply('NIGHTS_BOOKED','booking_amount',2)}} + cleaning_fee + service_fee as total_booking_amount,
    booking_status,
    created_at
from {{ref('bronze_bookings')}}

