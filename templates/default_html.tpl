<!DOCTYPE html>
<html lang="de">
	<head>
		<title>{{ title }}</title>
		<meta charset="UTF-8">
    	<meta http-equiv="X-UA-Compatible" content="IE=edge">
    	<meta name="viewport" content="width=device-width, initial-scale=1.0">

		<style type="text/css" rel="stylesheet">
			* {
				font-family: Poppins;
			}
			body {
				font-size: 11pt;
			}
			.nomargin {
				margin-top: 1px;
				margin-bottom: 1px;
			}
			table {
				border-spacing: 0;
				border-collapse: collapse;
			}
		</style>
	</head>
	<body>
	
<!--
		<div style="margin-bottom:5px; color:#05758a; margin-top:10px;">
					<div style="margin-bottom:5px; color:#05758a; margin-top:10px;">
						<p style="color:#5885aa;">____</p>
						<span style="font-size:14pt;">
							<b>20th</b> 
							December
							<b>2025</b> 
							until 
							<b>6th</b>
							January
							<b>2026</b>
						</span><br/>
						<span style="font-size:12pt"><b>We are closed for annual holidays</b></span><br>
						<span style="font-size:12pt;">
							We will be <b>back</b> at your service on Wednesday 
							<b>7th</b> 
							of January
							<b>2026</b>
						</span>

						<p style="font-size:12pt;">
							We wish you a <b>merry christmas</b> and a <b>happy new year 2026</b>
						</p>
					</div>
			</div>


		{% if promo_counter > 0 %}
			<div style="margin-top:0px; margin-bottom:0px;">
				<p style="color:#5885aa;">____</p>
				{% for promo in promotions %}
					{% if promo.display == True %}
						<a href="{{ promo.url }}">
							<img src="{{ server }}/ex/static/images/{{ promo.image }}" width="450px" />
						</a>
					{% endif %}
				{% endfor %}
			</div>
		{% endif %}
-->
		<div>
			<div style="color:#5885aa; margin-bottom:10px;">____</div>
			<div>Best regards,</div>
			<div style="font-size:14pt; color:#5885aa; font-weight:bold; margin-bottom:0px;">
				{{ user.firstname }} {{ user.lastname }}
			</div>
			<div style="color:#8b8b8b; margin-top:0px;">{{ user.position }}</div>
		</div>

		<div style="font-size:10pt; margin-top:10px;">
			<table>
				<tr>
					<td style="width:55px;">phone</td>
					<td>{{ user.officephone }}</td>
				</tr>
				{% if user.mobilephone %}
					<tr>
						<td>mobile</td>
						<td>{{ user.mobilephone }}</td>
					</tr>
				{% endif %}
				<tr>
					<td>mail</td>
					<td>{{ user.email }}</td>
				</tr>
				<tr>
					<td>web</td>
					<td><a>{{ branch.website }}</a></td>
				</tr>
			</table>

			
			<!-- Social + vCard container -->
<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin-top:8px;">
    <tr>
		<td style="vertical-align:middle; padding-right:20px;">
            <a href="https://intra.zimmer-austria.com/vc{{ vcard.view }}" style="text-decoration:none;">
                <img src="{{ server }}/ex/static/images/vcard.png" 
                     alt="vCard" 
                     style="display:block; height:40px;">
            </a>
        </td>
        {% if branch.linkedin|length > 0 %}
        <td style="vertical-align:middle; padding-right:6px;">
            <a href="{{ branch.linkedin }}" style="text-decoration:none;">
                <img src="{{ server }}/ex/static/images/linkedin.jpg" 
                     alt="LinkedIn" 
                     style="display:block; height:40px;">
            </a>
        </td>
        {% endif %}

        
    </tr>
</table>


			
			
			<div style="margin-top:8px;">
				<a class="nomargin" href="{{ branch.website }}" style="text-decoration:none; color:#5885aa; font-size:11pt;">
					<b>ZIMMER</b> AUSTRIA
				</a>
				<p class="nomargin">{{ branch.name }}</p>
				<p class="nomargin">{{ branch.street }}</p>
				<p class="nomargin">{{ branch.postalcode }} {{ branch.city }}, {{ branch.country }}</p>
				<p class="nomargin" style="font-size:8pt;">{{ branch.registrationnumber }}, {{ branch.registrar }}, {{ branch.taxid }}</p>
			</div>
		</div>
	</body>
</html>
