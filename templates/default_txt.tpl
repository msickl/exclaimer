Best regards,

{{ user.firstname }} {{ user.lastname }}
{{ user.position }}

-------------------------------------------------------

+++++++++++++++++++++++++++++++++++++++++++++++++++++++
26 July 2025 until 10 August 2025 
We are closed for annual holidays
We will be back at your service on Monday 11 of August 2025 
+++++++++++++++++++++++++++++++++++++++++++++++++++++++

phone:  {{ user.officephone }}
mobile: {{ user.mobilephone }}
mail:   {{ user.email }}
web:    {{ branch.website }}

{{ branch.name }}
{{ branch.street }}
{{ branch.postalcode }} {{ branch.city }}
{{ branch.country }}

-------------------------------------------------------
{% if branch.linkedin|length > 0 %}
VISIT US ON LINKED IN
{{ branch.linkedin }}
{% endif %}
-------------------------------------------------------
