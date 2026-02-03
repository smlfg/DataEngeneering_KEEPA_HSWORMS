import os
import requests
import json

def find_category(name, domain=3):
    api_key = "ph28mvoh2pe0cdicgseei87pmmr8ja97j4u7n4iuveqaeodg22q11qsg5uoj04la"
    url = f"https://api.keepa.com/search?key={api_key}&domain={domain}&term={name}&type=category"
    resp = requests.get(url)
    return resp.json()

print("Searching for 'Tastaturen' in Germany (Domain 3):")
print(json.dumps(find_category("Tastaturen", 3), indent=2))

print("\nSearching for 'Keyboards' in UK (Domain 2):")
print(json.dumps(find_category("Keyboards", 2), indent=2))
