from django.shortcuts import render, redirect
from django.contrib import messages
import requests
import json
from digidoc.models.message_models import Message, OnBoarding
from digidoc.forms.chat_forms import SendMessageForm, OnBoardingForm
from django.http import HttpResponse, QueryDict
from django.contrib.sessions.models import Session

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
    
    def set_symptom_confirmation_in_formatted_input(self, selected_symptoms_ids, conversation_id):
        self.formatted_input = {
            "answer": 
                { 
                    "type":
                        "generic", 
                        "input": { 
                            "include": selected_symptoms_ids,
                            "exclude": [] 
                        }
                },
            "conversation": { 
                "id": conversation_id
            }
 }

    def set_new_response(self):
        self.response = requests.post(self.url, json=self.formatted_input, headers=self.headers)

'''sets up new chat'''
'''uses on_boarding html and OnBoardingForm'''
def save_digidoc_message(text_content):
    for message in text_content:
        digiDoc_message = Message(sender="DigiDoc", content=message, timestamp=None)
        digiDoc_message.full_clean()
        digiDoc_message.save()

def save_user_message(content, timestamp):
    user_message = Message(sender="You", content=content, timestamp=timestamp)
    user_message.full_clean()
    user_message.save()

def save_symptoms(api_response):
    all_symptoms=[]
    all_symptoms.append(api_response.get('question', {}).get('choices' , []))
    conversation_id = api_response.get('conversation', {}).get('id' , None)
    print("convo id")
    print(conversation_id)
    print("SYMPTOM CHOICES")
    print(all_symptoms)
    for sublist in all_symptoms:
        for symptom_data in sublist:
            # Extracts symptom id and label
            symptom_id = symptom_data['id']
            symptom_label = symptom_data['label']
            symptom_conversation_id = conversation_id
    
            # Create Symptom object and save to database
            symptom = Symptom(symptom_id=symptom_id, name=symptom_label, conversation_id=symptom_conversation_id)
            symptom.full_clean()
            symptom.save()

def save_conditions(api_response):
    all_conditions=[]
    all_conditions.append(api_response.get('question', {}).get('choices' , []))
    conversation_id = api_response.get('conversation', {}).get('id' , None)
    print("convo id")
    print(conversation_id)
    print("HEALTH BACKGROUND CHOICES")
    print(all_conditions)
    for sublist in all_conditions:
        for health_condition_data in sublist:
            # Extracts symptom id and label
            condition_id = health_condition_data['id']
            condition_long_name = health_condition_data['long_name']
            condition_conversation_id = conversation_id
    
            # Create Symptom object and save to database
            condition = Condition(condition_id=condition_id, name=condition_long_name, conversation_id=condition_conversation_id)
            condition.full_clean()
            condition.save()

def new_chat(request):
    print("NEW CHAT")
    Message.objects.all().delete()
    OnBoarding.objects.all().delete()
    Symptom.objects.all().delete()
    Choice.objects.all().delete()
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
    save_digidoc_message(text_content)
    # for message in text_content:
    #         digiDoc_message = Message(sender="DigiDoc", content=message, timestamp=None)
    #         digiDoc_message.full_clean()
    #         digiDoc_message.save()

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
            save_user_message(content, timestamp)
            # user_message = Message(sender="You", content=content, timestamp=timestamp)
            # user_message.full_clean()
            # user_message.save()



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
        save_digidoc_message(text_content)

        all_messages = Message.objects.all()
        for message in all_messages:
            print(message.content)

        save_symptoms(api_response)
 
 
        form = SymptomForm()
        return render(request, 'chat.html', {'messages': all_messages, 'form': form})
  

def send_symptom_confirmation(request):
    
    response_data = Chat()
    Choice.objects.all().delete()
    if request.method == 'POST': 
        print("POST -- send_symptom_confirmation")        

        form = SymptomForm(request.POST)
        selected_symptoms_ids = []
        selected_symptoms_name = []
        if form.is_valid():
            selected_symptoms = form.cleaned_data['symptoms']
            # Handle the selected symptoms data
            for symptom in selected_symptoms:
          
                print(f"Selected Symptom: {symptom}")
    
                selected_symptoms_name.append(symptom.name)
                # Retrieves the symptom ID from the symptom object and append it to the list
                selected_symptoms_ids.append(symptom.symptom_id)
            print(str(selected_symptoms_ids))
            conversation_id = Symptom.objects.get(symptom_id=selected_symptoms_ids[0]).conversation_id
            print("convo id")
            print(conversation_id)
            print("selected_symptoms_name")
            print(str(selected_symptoms_name))
            content = "I confirm that I have the following symptom(s): " + str(selected_symptoms_name)
            timestamp = request.POST.get('timestamp')
            save_user_message(content, timestamp)


        response_data.set_symptom_confirmation_in_formatted_input(selected_symptoms_ids, conversation_id)

        response = requests.post(response_data.url, json=response_data.formatted_input, headers=response_data.headers)
        print(response.json())
        api_response = response.json()
        # saves api response as messages
        messages = []
        messages.append(api_response.get('question', {}).get('messages' , []))
        # Check if mandatory and multiple fields are true
        # mandatory = api_response.get('question', {}).get('mandatory' , [])
        # multiple = api_response.get('question', {}).get('multiple' , [])

        # if mandatory and multiple:
        #     print("mandatory: " + str(mandatory))
        #     print("multiple: " + str(multiple))
        # else:
        #     print("FALSE")

        print("MESSAGES")
        print(messages)
        text_content = [msg['value'] for sublist in messages for msg in sublist if msg.get('type') == 'generic']
        print("text content")
        print(text_content)
        save_digidoc_message(text_content)

        all_messages = Message.objects.all()
        for message in all_messages:
            print(message.content)

        list_of_choices = []
        list_of_choices.append(api_response.get('question', {}).get('choices' , []))

        conversation_id = api_response.get('conversation', {}).get('id' , None)

        print("CHOICES")
        print(list_of_choices)
        for sublist in list_of_choices:
            for choice in sublist:
                # Extracts symptom id and label
                choice_id = choice['id']
                choice_label = choice['label']
                # selected = True
                choice_conversation_id = conversation_id
        
                # Create Symptom object and save to database
                chosen_option = Choice(choice_id=choice_id, label=choice_label, conversation_id=choice_conversation_id)
                chosen_option.full_clean()
                chosen_option.save()
        form = ChoiceForm()
        return render(request, 'chat2.html', {'messages': all_messages, 'form': form})
    else:
        form = SymptomForm()
    return render(request, 'chat.html', {'form': form})

def submit_choice(request):
    response_data = Chat()
    if request.method == 'POST': 
        print("POST -- submit_choice")        

        form = ChoiceForm(request.POST)
        selected_choice_id = []
        selected_choice_label = []
        if form.is_valid():
            choice = form.cleaned_data['choices']
            # Handle the selected symptoms data
       
            # Do something with the selected symptom ID
            print(f"Selected choice: {choice}")

            selected_choice_label.append(choice.label)
            # Retrieves the choice ID from the choice object and append it to the list
            selected_choice_id.append(choice.choice_id)
            print(str(selected_choice_id))
            conversation_id = Choice.objects.get(choice_id=selected_choice_id[0]).conversation_id
            print("convo id")
            print(conversation_id)
            print("selected_choice_label")
            print(str(selected_choice_label))
            content = "Selected: " + str(selected_choice_label)
            timestamp = request.POST.get('timestamp')
            save_user_message(content, timestamp)

            response_data.set_symptom_confirmation_in_formatted_input(selected_choice_id, conversation_id)

            response = requests.post(response_data.url, json=response_data.formatted_input, headers=response_data.headers)
            print(response.json())
            api_response = response.json()
        else:
            print("NO")
        # saves api response as messages
        messages = []
        messages.append(api_response.get('question', {}).get('messages' , []))

        print("MESSAGES")
        print(messages)
        text_content = [msg['value'] for sublist in messages for msg in sublist if msg.get('type') == 'generic']
        print("text content")
        print(text_content)
        save_digidoc_message(text_content)

        all_messages = Message.objects.all()

        phase_value = api_response['conversation']['phase']
        print("phase")
        print(phase_value)
        if (phase_value=='info_result'):
                form = ChoiceForm()
                # Accessing the articles
                articles = api_response['report']['articles']
                request.session['articles'] = json.dumps(articles)
                return render(request, 'end_of_chat.html', {'messages': all_messages, 'form': form})
        elif (phase_value=='clarify'):
            Symptom.objects.all().delete()
            save_symptoms(api_response)
            form = SymptomForm()
            return render(request, 'chat.html', {'messages': all_messages,'form': form})
        elif (phase_value=='health_background'):
            Condition.objects.all().delete()
            save_conditions(api_response)
            form = ConditionForm()
            return render(request, 'health_background_chat.html', {'messages': all_messages,'form': form})
        else:
            pass
    else:
        form = SymptomForm()
    return render(request, 'chat.html', {'form': form})

def send_condition(request):
    
    response_data = Chat()
    Choice.objects.all().delete()
    if request.method == 'POST': 
        print("POST -- send_condition")        

        form = ConditionForm(request.POST)
        selected_condition_ids = []
        selected_condition_name = []
        if form.is_valid():
            selected_conditions = form.cleaned_data['conditions']
            # Handle the selected condition data
            for condition in selected_conditions:
          
                print(f"Selected condition: {condition}")
    
                selected_condition_name.append(condition.name)
                # Retrieves the symptom ID from the symptom object and append it to the list
                selected_condition_ids.append(condition.condition_id)
            print(str(selected_condition_ids))
            conversation_id = Condition.objects.get(condition_id=selected_condition_ids[0]).conversation_id
            print("convo id")
            print(conversation_id)
            print("selected_condition_name")
            print(str(selected_condition_name))
            content = "I confirm that I have the following condition(s): " + str(selected_condition_name)
            timestamp = request.POST.get('timestamp')
            save_user_message(content, timestamp)


        response_data.set_symptom_confirmation_in_formatted_input(selected_condition_ids, conversation_id)

        response = requests.post(response_data.url, json=response_data.formatted_input, headers=response_data.headers)
        print(response.json())
        api_response = response.json()
        # saves api response as messages
        messages = []
        messages.append(api_response.get('question', {}).get('messages' , []))


        print("MESSAGES")
        print(messages)
        text_content = [msg['value'] for sublist in messages for msg in sublist if msg.get('type') == 'generic']
        print("text content")
        print(text_content)
        save_digidoc_message(text_content)

        all_messages = Message.objects.all()
        for message in all_messages:
            print(message.content)

        list_of_choices = []
        list_of_choices.append(api_response.get('question', {}).get('choices' , []))

        conversation_id = api_response.get('conversation', {}).get('id' , None)

        print("CHOICES")
        print(list_of_choices)
        for sublist in list_of_choices:
            for choice in sublist:
                # Extracts symptom id and label
                choice_id = choice['id']
                choice_label = choice['text']
                # selected = True
                choice_conversation_id = conversation_id
        
                # Create Symptom object and save to database
                chosen_option = Choice(choice_id=choice_id, label=choice_label, conversation_id=choice_conversation_id)
                chosen_option.full_clean()
                chosen_option.save()
            form = ConditionForm()
        return render(request, 'chat.html', {'messages': all_messages, 'form': form})
    else:
        form = ConditionFormForm()
    return render(request, 'chat.html', {'form': form})

def see_articles(request):
    articles = json.loads(request.session['articles'])
    print("articles")
    print(articles)
    # Render report.html with articles data
    return render(request, 'articles.html', {'articles': articles})

