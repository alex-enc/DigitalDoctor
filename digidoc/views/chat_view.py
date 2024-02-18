from django.shortcuts import render, redirect
from django.contrib import messages
import requests
import json
from digidoc.models.message_models import Message, OnBoarding, Symptom
from digidoc.forms.chat_forms import SendMessageForm, OnBoardingForm, SymptomForm
from django.http import HttpResponse

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
        
        if self.response is not None:
            return self.response.json()
        else:
            return {}

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
'''uses on_boarding html and OnBoardingForm'''
def new_chat(request):
    print("NEW CHAT")
    Message.objects.all().delete()
    OnBoarding.objects.all().delete()
    Symptom.objects.all().delete()

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
    '''gets the actual message content of the JSON response'''
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
    
def send_on_boarding(request):
    response_data = Chat()
    if request.method == 'POST': 
        print("POST -- on_boarding")        

        form = OnBoardingForm(request.POST)
        
        if form.is_valid():
            name = request.POST.get('name')
            birth_year = request.POST.get('birth_year')
            initial_symptoms = request.POST.get('initial_symptoms')
            gender = request.POST.get('gender')
            timestamp = request.POST.get('timestamp')
            print("name:" + str(name))
            print("birth year: " + str(birth_year))
            print("initial_symptoms:" + str(initial_symptoms))
            print("gender" + str(gender))
            initial_symptoms_splitted = initial_symptoms.split(", ")

            on_boarding_answers = OnBoarding(name=name, birth_year=birth_year, initial_symptoms=initial_symptoms_splitted, gender=gender, timestamp=timestamp)
            on_boarding_answers.full_clean()
            on_boarding_answers.save()

            content = "Name: " + str(name) + ", " + "Birth Year: " + str(birth_year) + ", " + "Initial Symptoms: " + str(initial_symptoms) + ", " + "Gender: " + str(gender)
            user_message = Message(sender="You", content=content, timestamp=timestamp)
            user_message.full_clean()
            user_message.save()



        response_data.set_on_boarding_answers_in_formatted_input(on_boarding_answers.name, on_boarding_answers.birth_year, on_boarding_answers.initial_symptoms, on_boarding_answers.gender)
        
        

        response = requests.post(response_data.url, json=response_data.formatted_input, headers=response_data.headers)
        print(response.json())
        api_response = response.json()

        # saves api response as messages
        messages = []
        messages.append(api_response.get('question', {}).get('messages' , []))
        # Check if mandatory and multiple fields are true
        mandatory = api_response.get('question', {}).get('mandatory' , [])
        multiple = api_response.get('question', {}).get('multiple' , [])

        if mandatory and multiple:
            print("mandatory: " + str(mandatory))
            print("multiple: " + str(multiple))
        else:
            print("FALSE")

        print("MESSAGES")
        print(messages)
        text_content = [msg['value'] for sublist in messages for msg in sublist if msg.get('type') == 'generic']
        print("text content")
        print(text_content)
        for message in text_content:
                digiDoc_message = Message(sender="DigiDoc", content=message, timestamp=None)
                digiDoc_message.full_clean()
                digiDoc_message.save()

        all_messages = Message.objects.all()
        for message in all_messages:
            print(message.content)

        all_symptoms = []
        all_symptoms.append(api_response.get('question', {}).get('choices' , []))
        print("SYMPTOM CHOICES")
        print(all_symptoms)
        for sublist in all_symptoms:
            for symptom_data in sublist:
                # Extracts symptom id and label
                symptom_id = symptom_data['id']
                symptom_label = symptom_data['label']
        
                # Create Symptom object and save to database
                symptom = Symptom(symptom_id=symptom_id, name=symptom_label)
                symptom.full_clean()
                symptom.save()
        # symptoms = [symp['label'] for sublist in all_symptoms for symp in sublist if symp.get('type') == 'generic']
        # print("symptoms")
        # print(symptoms)
        # for symptom in symptoms:
        #         user_symptom = Symptom(name=symptom)
        #         user_symptom.full_clean()
        #         user_symptom.save()
        form = SymptomForm()
        return render(request, 'chat.html', {'messages': all_messages, 'form': form})
        # return redirect('chat')
        # return api_response
        # return response
        # response_data.set_new_response()
        # return response_data
        # return response.content
  
           
    

# def get_chat(request):
#     response_data = Chat()
#     api_data = response_data.get_response_data()
#     scenario = api_data.get('conversation', {}).get('scenario' , [])
#     print("scenario")
#     print(scenario)
#     all_messages = Message.objects.all()
#     form = SendMessageForm()
#     if request.method == 'POST':
#         if scenario=="on_boarding":
#             print("get_chat -- on_boarding")
#             response = send_on_boarding(request)
            
#     elif request.method == 'GET':
#         # form = SendMessageForm()
#         print("GET--get_chat")
#         # all_messages = Message.objects.all()
#         response_data.set_response()
#         status = response_data.get_response_status()
#         print("Status: " + str(status))
#     # if request.method == 'GET':
#     #     form = SendMessageForm()
#     #     print("GET--get_chat")
#     #     # all_messages = Message.objects.all()
#     #     response_data.set_response()
#     #     status = response_data.get_response_status()
#     #     print("Status: " + str(status))

#         api_data = response_data.get_response_data()



#     messages = []
#     messages.append(api_data.get('question', {}).get('messages' , []))

#     text_content = [msg['text'] for sublist in messages for msg in sublist if msg.get('type') == 'text']
#     print("text content")
#     print(text_content)
#     for message in text_content:
#             digiDoc_message = Message(sender="DigiDoc", content=message, timestamp=None)
#             digiDoc_message.full_clean()
#             digiDoc_message.save()

#     for message in all_messages:
#         print(message.content)
#     return render(request, 'chat.html', {'messages': all_messages, 'form': form, 'scenario': scenario})

   


def send_symptom_confirmation(request):
    response_data = Chat()
    if request.method == 'POST': 
        print("POST -- send_symptom_confirmation")        

        form = SymptomFormForm(request.POST)
        
        if form.is_valid():
            # message = form.cleaned_data.get('content')
            # sender = "You"
            # content = request.POST.get('content')
            # timestamp = request.POST.get('timestamp')
            # # print("message: " + str(message))
            # print("sender: " + str(sender))
            # print("content: " + str(content))
            # print("timestamp: " + str(timestamp))
            symptom = request.POST.get('name')

        selected_symptom = Symptom(sender=sender, content=content, timestamp=timestamp)
        user_message.full_clean()
        user_message.save()

        # response_data.set_name_in_formatted_input(user_message.content)

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

