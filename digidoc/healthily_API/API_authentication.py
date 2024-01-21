import requests

class APIAuthenticate():

    def __init__(self):
        self.url = "https://portal.your.md/v4/login"
        self.payload = {
            "id": "user1",
            "name": "superuser",
            "email": "admin@example.org",
            "email_verified": True
        }
        self.headers = {
            "accept": "*/*",
            "content-type": "application/json",
            "Authorization": "token d8J4TmqaHyXh5H5uo2YTJHB15GrvKPLW.Cuo9pegBtQY48BpxWmMvLn8QC6k3SBb8",
            "x-api-key": "2jqSPFo7ki5faZtPG66ys5BgNpMnNX5vaKFj1MlL"
        }
        self.response = None

    '''Set response of the API by performing POST request to API'''
    def set_response(self):
        self.response = requests.post(url=self.url, json=self.payload, headers=self.headers)

    '''Get response status code'''
    def get_response_status(self): 
        return self.response.status_code
    
    '''Get response data json'''
    def get_response_data(self): 
        return self.response.json()


# response_data = APIAuthenticate()
# response_data.set_response()
# status = response_data.get_response_status()
# print(status)
# if status == 200:
#     print(response_data.get_response_data())
#     print('access_token: ' + response_data.get_response_data()['access_token'])
# else:
#     print("Status code: "  + status)