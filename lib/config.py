import json

configpath = "/opt/exclaimer/var/config.json"

with open(configpath) as f:
    data = json.load(f)

def get(x):
    return data[x]
