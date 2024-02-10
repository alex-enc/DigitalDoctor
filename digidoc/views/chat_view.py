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
        self.formatted_input = None

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

    def set_formatted_input(self):
        self.formatted_input =  {
                "answer": {
                    "type": "entry",
                    "name": (user_message.content).text,
                    "gender": "male",
                    "year_of_birth": 1978,
                    "initial_symptom": "shaking",
                    "other": true
                }
            }
    


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
    if request.method == 'GET':
        form = SendMessageForm()
        print("GET")
        all_messages = Message.objects.all()
        return render(request, 'chat.html', {'messages': all_messages, 'form': form})
    elif request.method == 'POST': 
        print("POST")        
        form = SendMessageForm(request.POST)
        if form.is_valid():
            # message = form.cleaned_data.get('content')
            sender = "You"
            content = request.POST.get('content')
            timestamp = request.POST.get('timestamp')
            # print("message: " + str(message))
            print("sender: " + str(sender))
            print("content: " + str(content))
            print("timestamp: " + str(timestamp))
        user_message = Message(sender=sender, content=content, timestamp=timestamp)
        user_message.full_clean()
        user_message.save()
        all_user_messages = Message.objects.all()
        form = SendMessageForm()
        return render(request, 'chat.html', {'messages': all_user_messages, 'form': form})
    return redirect('chat') 




def new_chat(request):
    Message.objects.all().delete()
    response_data = Chat()
    print(response_data.get_headers())
    response_data.set_response()
    status = response_data.get_response_status()
    print("Status: " + str(status))
    api_data = response_data.get_response_data()
    messages = []
    messages.append(api_data.get('question', {}).get('messages' , []))
    text_content = [msg['text'] for sublist in messages for msg in sublist if msg.get('type') == 'text']
    print(text_content)
    for message in text_content:
            digiDoc_message = Message(sender="DigiDoc", content=message, timestamp=None)
            digiDoc_message.full_clean()
            digiDoc_message.save()
    if status == 200:
        print(api_data)
    else:
        print(status)
    if request.method == 'GET':
        form = SendMessageForm()
        print("GET")
        all_messages = Message.objects.all()
        return render(request, 'chat.html', {'messages': all_messages, 'form': form})