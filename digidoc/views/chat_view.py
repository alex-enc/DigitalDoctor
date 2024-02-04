from django.shortcuts import render, redirect
from django.contrib import messages
import requests
import json
from digidoc.models.message_models import Message
from digidoc.forms.chat_forms import SendMessageForm

from digidoc.healthily_API.API_authentication import APIAuthenticate
class Chat():
    def __init__(self):
        self.url = "https://portal.your.md/v4/chat"

        self.payload = {
            "conversation": {
                "symptoms_summary": { "selected": [
                        {
                            "cui": "c1",
                            "name": ""
                        }
                    ] },
                "progress": {
                    "stage": "1",
                    "percentage": 0
                },
                "id": "convo1",
                "scenario": "initial",
                "phase": "1",
                "available_commands": ["STOP_CONVERSATION"]
            },
            "answer": {
                "type": "year_of_birth",
                "value": 0000
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
api_data = response_data.get_response_data()
messages = api_data.get('question', {}).get('messages' , [])
if status == 200:
    print(api_data)
else:
    print(status)
# print("Authorization: " + response_data.get_authorization())


# def chat(request):
#     print("chat request" + str(request))
#     if request.method == 'POST':
#         try:
            
#             # Extract user input from the request
#             data = json.loads(request.body)
#             print(data)
#             user_input = data.get('inputData')
#             print("user input" + user_input)
#             # Do something with the user input (e.g., save it to the database)
            
#             # Return a JSON response
#             # return JsonResponse({'message': 'Data received successfully'})
#             render(request, 'chat.html', {'user_input': user_input})
#         except json.JSONDecodeError:
#             return JsonResponse({'error': 'Invalid JSON data'}, status=400)
#     else:
#         print("API")
#         return render(request, 'chat.html', {'messages': messages})

def chat(request):
    form = SendMessageForm()
    if request.method == 'GET':
        print("GET")
        user_messages = Message.objects.all()
        return render(request, 'chat.html', {'messages': messages, 'form': form})
    elif request.method == 'POST': 
        print("POST")        
        sender = request.POST.get('sender')
        content = request.POST.get('content')
        user_message = Message.objects.create(sender=sender, content=content)
        return render(request, 'chat.html', {'user_message': user_message, 'form': form})
    return redirect('chat') 

def send_message(request):
    print("send message")
    if request.method == 'POST':
        if request.user.is_authenticated:
            current_user = "You"
            form = SendMessageForm(request.POST)
            if form.is_valid():
                text = form.cleaned_data.get('text')
                message = Message.objects.create(author=current_user, text=text)
                return redirect('chat')
            else:
                return render(request, 'chat.html', {'messages':messages, 'form': form})
        else:
            return redirect('home')
    else:
        return HttpResponseForbidden()
# def send_message(request):
#     print("send_message")
#     if request.method == 'POST':
#         sender = request.POST.get('sender')
#         content = request.POST.get('content')
#         Message.objects.create(sender=sender, content=content)
#     return redirect('chat')

