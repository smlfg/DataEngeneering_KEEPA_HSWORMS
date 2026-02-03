import requests
import json

api_key = "ph28mvoh2pe0cdicgseei87pmmr8ja97j4u7n4iuveqaeodg22q11qsg5uoj04la"
category = "430253031" # Gaming Keyboards DE
domain = 3 # DE

url = f"https://api.keepa.com/bestsellers?key={api_key}&domain={domain}&category={category}"
resp = requests.get(url)
print(f"Bestsellers Status: {resp.status_code}")
print(json.dumps(resp.json(), indent=2))
