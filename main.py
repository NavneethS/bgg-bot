import requests
from secrets import webhook_url

r = requests.post(webhook_url, json={"text": "Hello"})
assert r.status_code == 200
