import requests
from API_authentication import APIAuthenticate

class Chat():
    def __init__(self):
        self.url = "https://portal.your.md/v4/chat"

        self.payload = {
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

        self.headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": "Bearer " +  self.get_authorization(),
            "x-api-key": "2jqSPFo7ki5faZtPG66ys5BgNpMnNX5vaKFj1MlL"
        }
        self.response = None

    def get_authorization(self):
        auth_key = APIAuthenticate()
        auth_key.set_response()
        return auth_key.get_response_data()['access_token']

    def get_headers(self):
        return self.headers

    def set_response(self):
        self.response = requests.post(self.url, json=self.payload, headers=self.headers)

    def get_response_status(self):
        return self.response.status_code
    
    def get_response_data(self):
        return self.response.json()
    
    
response_data = Chat()
print(response_data.get_headers())
response_data.set_response()
status = response_data.get_response_status()
print("Status: " + str(status))
if status == 200:
    print( response_data.get_response_data())
else:
    print(status)
# print("Authorization: " + response_data.get_authorization())
