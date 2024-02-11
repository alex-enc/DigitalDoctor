from django.shortcuts import render, redirect
from django.contrib import messages
import requests
import json
from digidoc.models.message_models import Message, OnBoarding
from digidoc.forms.chat_forms import SendMessageForm, OnBoardingForm


from digidoc.healthily_API.API_authentication import APIAuthenticate
class Chat():
    def __init__(self):
        self.url = "https://portal.your.md/v4/chat"

        self.payload = {
            "conversation": {
                "symptoms_summary": { "selected": [
                        {
                            "cui": "",
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
                "value": None
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

    def set_on_boarding_answers_in_formatted_input(self, name, birth_year, initial_symptoms, gender):
        self.formatted_input = {
           
            "answer": {
                "type": "entry",
                "name": name,
                "gender": gender,
                "year_of_birth": birth_year,
                "initial_symptom": initial_symptoms,
                "other": True
            }
        }
    def set_new_response(self):
        self.response = requests.post(self.url, json=self.formatted_input, headers=self.headers)

'''sets up new chat'''
def new_chat(request):
    Message.objects.all().delete()
    OnBoarding.objects.all().delete()
    response_data = Chat()
    print(response_data.get_headers())
    response_data.set_response()
    status = response_data.get_response_status()
    print("Status: " + str(status))
    api_data = response_data.get_response_data()

    scenario = api_data.get('conversation', {}).get('scenario' , [])
    print("scenario")
    print(scenario)

    messages = []
    messages.append(api_data.get('question', {}).get('messages' , []))

    text_content = [msg['text'] for sublist in messages for msg in sublist if msg.get('type') == 'text']
    print("text content")
    print(text_content)
    for message in text_content:
            digiDoc_message = Message(sender="DigiDoc", content=message, timestamp=None)
            digiDoc_message.full_clean()
            digiDoc_message.save()
    print("first 2:")
    first_two_messages = text_content[:2]
    print(first_two_messages)
    if status == 200:
        print(api_data)
    else:
        print(status)
   
    if request.method == 'GET':
        
        # form = SendMessageForm()
        form = OnBoardingForm()
        print("GET")
        all_messages = Message.objects.all()
        return render(request, 'on_boarding.html', {'first_two_messages': first_two_messages, 'form': form, 'scenario': scenario})
    
           
    

def get_chat(request):
    response_data = Chat()

    if request.method == 'GET':
        form = SendMessageForm()
        print("GET")
        all_messages = Message.objects.all()
        api_data = response_data.get_response_data()
        scenario = api_data.get('conversation', {}).get('scenario' , [])
        print("scenario")
        print(scenario)

        for message in all_messages:
            print(message.content)
        return render(request, 'chat.html', {'messages': all_messages, 'form': form, 'scenario': scenario})

   
    return redirect('chat') 

def send_chat(request):
    response_data = Chat()
    if request.method == 'POST': 
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

        response_data.set_name_in_formatted_input(user_message.content)
        all_user_messages = Message.objects.all()
        form = SendMessageForm()
        response = requests.post(response_data.url, json=response_data.formatted_input, headers=response_data.headers)
        print(response.json())
        if "error" in response:
            _, expect_values = response.split('Expect:')
            expect_values = expect_values.strip() 
            api_message = Message(sender="DigiDoc", content=expect_values, timestamp=None)
            api_message.full_clean()
            api_message.save()
        # return render(request, 'chat.html', {'messages': all_user_messages, 'form': form})
        return redirect('chat')

def send_on_boarding(request):
    response_data = Chat()
    if request.method == 'POST': 
        print("POST")        

        form = OnBoardingForm(request.POST)
        
        if form.is_valid():
            # message = form.cleaned_data.get('content')
            # sender = "You"
            # content = request.POST.get('content')
            # timestamp = request.POST.get('timestamp')
            # # print("message: " + str(message))
            # print("sender: " + str(sender))
            # print("content: " + str(content))
            # print("timestamp: " + str(timestamp))
            name = request.POST.get('name')
            birth_year = request.POST.get('birth_year')
            initial_symptoms = request.POST.get('initial_symptoms')
            gender = request.POST.get('gender')
            print("name:" + str(name))
            print("birth year: " + str(birth_year))
            print("initial_symptoms:" + str(initial_symptoms))
            print("gender" + str(gender))

            on_boarding_answers = OnBoarding(name=name, birth_year=birth_year, initial_symptoms=initial_symptoms, gender=gender)
            on_boarding_answers.full_clean()
            on_boarding_answers.save()


        response_data.set_on_boarding_answers_in_formatted_input(on_boarding_answers.name, on_boarding_answers.birth_year, on_boarding_answers.initial_symptoms, on_boarding_answers.gender)
        
        form = OnBoardingForm()
        response = requests.post(response_data.url, json=response_data.formatted_input, headers=response_data.headers)
        print(response.json())
        if "error" in response:
            _, expect_values = response.split('Expect:')
            expect_values = expect_values.strip() 
            api_message = Message(sender="DigiDoc", content=expect_values, timestamp=None)
            api_message.full_clean()
            api_message.save()
        # return render(request, 'chat.html', {'messages': all_user_messages, 'form': form})
        return redirect('chat')