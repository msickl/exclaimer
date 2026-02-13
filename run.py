from flask import Flask, request, jsonify, render_template, Response
import requests
from datetime import date, datetime
import json
from datetime import datetime, timedelta, timezone
from lib import config
from lib import postgres
from lib.authorization import Authorization
import os
import base64

app = Flask(__name__)    
auth = Authorization()

@app.route('/')
def home():
    return "Welcome to Exclaimer Server!"

@app.route('/api/token/create', methods=['POST'])
def api_create_token():
    return auth.create()

@app.route('/api/token/revoke', methods=['POST'])
def api_revoke_token():
    return auth.revoke()

@app.route('/api/users', methods=['GET', 'POST'])
def users():
    db = postgres.init()

    # Require token for POST
    if request.method == 'POST':
        check = auth.require()
        if check:
            return check

    # ----------------------------
    # GET: Return users with filters
    # ----------------------------
    if request.method == 'GET':
        filters = request.args
        query = "SELECT * FROM users WHERE employeeid != 0"
        values = []

        # Add dynamic filters (ILIKE for case-insensitive partial matching)
        for key, value in filters.items():
            query += f" AND {key} ILIKE %s"
            values.append(f"%{value}%")

        rows = db.select(query, tuple(values))
        db.close()

        if len(rows) > 0:
            return jsonify({"status": "ok", "data": rows})
        else:
            return jsonify({"status": "empty", "data": []})

    # ----------------------------
    # POST: Insert or update users
    # ----------------------------
    elif request.method == 'POST':
        fullsync = request.args.get('fullsync', 'false').lower() == 'true'
        data = request.get_json()

        for entry in data:
            # Extract CompanyId and EmployeeId from received employeeid (e.g., "1-1234")
            if entry.get('employeeid') is not None:
                companyid, employeeid = entry.get('employeeid').split("-")

                entry['companyid'] = companyid if companyid else 0
                entry['employeeid'] = employeeid if employeeid else 0

                # Check if user already exists
                query = "SELECT * FROM users WHERE objectsid = %s"
                rows = db.select(query, (entry.get('objectsid'),))

                if len(rows) == 1:
                    existing = rows[0]

                    # Full sync: overwrite all columns except 'id'
                    if fullsync:
                        updates = [f"{column} = %s" for column in existing if column != 'id']
                        values = [entry.get(column) for column in existing if column != 'id']
                        print(f"FULLSYNC UPDATE: {entry['samaccountname']}")

                    else:
                        # Compare USNChanged before updating
                        if int(existing.get('usnchanged')) == int(entry.get('usnchanged')):
                            continue  # skip unchanged users

                        updates = []
                        values = []
                        for column in existing:
                            if column != 'id' and str(existing[column]) != str(entry.get(column)):
                                updates.append(f"{column} = %s")
                                values.append(entry.get(column))
                        print(f"UPDATE: {entry['samaccountname']}")

                    if updates:
                        query = f"UPDATE users SET {', '.join(updates)} WHERE objectsid = %s"
                        values.append(entry.get('objectsid'))
                        db.update(query, values)

                else:
                    # Insert new user
                    columns = list(entry.keys())
                    placeholders = ", ".join(["%s"] * len(columns))
                    query = f"INSERT INTO users ({', '.join(columns)}) VALUES ({placeholders})"
                    values = [entry[column] for column in columns]
                    print(f"INSERT: {entry['samaccountname']}")
                    db.insert(query, values)

        db.close()
        return jsonify({"status": "ok"})

@app.route('/install', methods=['GET'])
def install():
    # irm http://ex.zimmer.local/install | iex
    with open('/opt/exclaimer/lib/ActiveDirectoryAgent.ps1', 'r') as file:
        content = file.read()
    return content

@app.route('/template', methods=['GET'])
def template():
    # http://ex.zimmer.local/template?u=1DDFBAB43E710E0FE2B378BB45771A5B&t=default

    objectsid_base64 = request.args.get('u')
    objectsid_bytes = base64.b64decode(objectsid_base64)
    objectsid = objectsid_bytes.decode('utf-8')
    templatename = request.args.get('t')
    if templatename is None:
        templatename = 'default_html.tpl'
    else:
        templatename = f"{templatename}.tpl"
    
    if not os.path.exists(f"/opt/exclaimer/templates/{templatename}"):
        return f"400 - template {templatename} doesn't exists"

    templateconfig = config.get("template")
    templatehost = templateconfig.get("hostname")
    templateprotocol = templateconfig.get("protocol")
    templateroot = f"{templateprotocol}://{templatehost}"

    if objectsid:
        db = postgres.init()
        query = "SELECT * FROM users WHERE objectsid = %s"
        rows = db.select(query, (objectsid,))

        if len(rows) == 1:
            user = rows[0]

            current_time = datetime.now(timezone.utc)

            query = f"SELECT * FROM branches WHERE companyid = {user.get('companyid')}"
            branch = db.select(query, (1,))

            if len(branch) == 1:
                branch = branch[0]
            else:
                return f"The Emplyoee {user.get('employeeid')} has no companyid"

            query = f"SELECT * FROM notifications WHERE template = '{templatename}'"
            notifications = db.select(query, (1,))

            query = f"SELECT * FROM promotions WHERE template = '{templatename}'"
            promotions = db.select(query, (1,))

            active_notifications = []

            for notification in notifications:
                
                from_time = notification.get('from_date')
                to_time = notification.get('to_date')

                if from_time.tzinfo is None:
                    from_time = from_time.replace(tzinfo=timezone.utc)
                if to_time.tzinfo is None:
                    to_time = to_time.replace(tzinfo=timezone.utc)

                day_of_week = to_time.weekday()
                
                if day_of_week >= 4:  # If it's Friday or later
                    notification['backon'] = to_time + timedelta(days=(7 - day_of_week))
                else:
                    notification['backon'] = to_time + timedelta(days=1)

                if from_time <= current_time <= to_time:
                    active_notifications.append(notification)

            promo_counter = sum(1 for promo in promotions if promo.get('display') == True)

            headers = {
                "Content-Type": "application/json"
            }

            payload = json.dumps({
                "user": user
            }, cls=CustomJSONEncoder)

            req = requests.post('http://127.0.0.1:5001/api/link', data=payload, headers=headers)            
            vcard = json.loads(req.content)

            template = render_template(templatename,
                                title=templatename,
                                server=templateroot,
                                notifications=active_notifications,
                                promo_counter=promo_counter,
                                promotions=promotions,
                                user=user,
                                branch=branch,
                                vcard=vcard)
            
            if 'txt' in templatename:
                response = Response(template, content_type='text/plain; charset=utf-8')
            else:
                response = Response(template, content_type='text/html; charset=utf-8')

            return response
        
        else:
            return "400 - no user found"
    else:
        return "400 - no user found"
    
@app.route('/admin', methods=['GET'])
def admin():
    return "Administrator Interface"

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)

if __name__ == '__main__':
    appconfig = config.get("app")
    app.run(host=appconfig.get("listen"), port=appconfig.get("port"), debug=appconfig.get("debug"))