

{% set cols =['Nights_Booked','Booking_id','booking_amount'] %}

select 
{% for col in cols %}
    {{col}}
    {% if not loop.last %},{% endif %}
{% endfor %}
from {{ ref('bronze_bookings') }}