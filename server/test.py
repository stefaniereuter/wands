import requests

data = {
    'uri': '30420.h5',
    'signals': ['/amc/AMC_PLASMA CURRENT/data'],
}
response = requests.post('http://localhost:8080/data', json=data)

print(response.status_code)
print(response.json())
