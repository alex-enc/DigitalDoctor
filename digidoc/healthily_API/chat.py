import requests

url = "https://portal.your.md/v4/chat"

payload = {
    "conversation": {
        "symptoms_summary": { "selected": [
                {
                    "cui": "c1",
                    "name": "Cough"
                }
            ] },
        "progress": {
            "stage": "1",
            "percentage": 20
        },
        "id": "convo1",
        "scenario": "initial",
        "phase": "1",
        "available_commands": ["STOP_CONVERSATION"]
    },
    "answer": {
        "type": "year_of_birth",
        "value": 2002
    }
}
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": "Bearer eyJraWQiOiI0Y2RmY2Q0OS1kM2QyLTRlZGMtYThlZi02MDY5ZjRmZWYwNmMiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJ5bWRNb3JzZV9NdFRzdndtWnp6QkhzMGppc0xpaTB2aXAweWNHZFlMUkpkbUlINThRc09qNEZjIiwiYXVkIjoiS2luZ3NDb2xsZWdlTG9uZG9uIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImRldmljZV9pZCI6InBhcnRuZXJfS2luZ3NDb2xsZWdlTG9uZG9uXzA4ZDRkYzZkZTRlZmUzNGQ1NTQ5Y2JkNWFkMmZiMzA0NGQ0MTU4YjMwM2QxNTU0MDdkNjZhMzgwNGQyM2ZlMDIiLCJuYW1lIjoiXCJzdXBlcnVzZXJcIiIsImRlbGV0ZV9hdCI6MTcwNTUwMzQwNSwicGlkIjoiZDhKNFRtcWFIeVhoNUg1dW8yWVRKSEIxNUdydktQTFciLCJlbWFpbCI6IlwiYWRtaW5AZXhhbXBsZS5vcmdcIiIsImlzcyI6InltZC1pbnRlcm5hbC1zZXJ2aWNlLXByb2QiLCJqdGkiOiI0YTQ3NTI0NC1lMTZkLTQ0ZjAtYThlZC01YzJmNmVkYzUxMGUiLCJpYXQiOjE3MDUzMzA2MDUsImV4cCI6MTcwNTMzMjQwNX0.s8towU_8BgOHKQh-9yu4-f71b-BBERbzWE9XgyczTxkJf78a8PS5dYfZhHT0EHiBGC_JNHc3XnMnR6d99WNRbeaArARIolUUMQMfV7S0S0vaXdaEZQnfX7cxVUI6nzV-F7jwQ1Sm26cIcaYD7XHhrN_CFK1UrNIuANgeyn4RaGWHAfX-qZG9nqmu6zKCsSP_YZ5Obbv4_XmuMIMYo3s1x8-7xcR5_v4w-P7dPMIJeFgvCHFEgOTwYchWQGzU_FFHafNj3vmTwzq84FrtRpFZA4j-JeeIycRyKiHw-C0ZJFFdmXfUQznkFvh1ljFyfJjtxNO8cQ-WJfROonTdUGVdNw",
    "x-api-key": "2jqSPFo7ki5faZtPG66ys5BgNpMnNX5vaKFj1MlL"
}

response = requests.post(url, json=payload, headers=headers)

print(response.text)