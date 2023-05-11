import requests

data = {
    'uri': '30420.h5',
    'signals': ['/amc/AMC_PLASMA CURRENT', '/amc/AMC_SOL CURRENT'],
}
response = requests.post('http://localhost:8080/data', json=data)

print(response.status_code)
print(response.json())
