import requests

url = "https://portal.your.md/v4/login"

payload = {
    "id": "user1",
    "name": "superuser",
    "email": "admin@example.org",
    "email_verified": True
}
headers = {
    "accept": "*/*",
    "content-type": "application/json",
    "Authorization": "token d8J4TmqaHyXh5H5uo2YTJHB15GrvKPLW.Cuo9pegBtQY48BpxWmMvLn8QC6k3SBb8",
    "x-api-key": "2jqSPFo7ki5faZtPG66ys5BgNpMnNX5vaKFj1MlL"
}

response = requests.post(url, json=payload, headers=headers)

print(response.text)