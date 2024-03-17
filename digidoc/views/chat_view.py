from django.shortcuts import render, redirect
from django.contrib import messages
import requests
import json
from digidoc.models.message_models import Message, OnBoarding, MultipleChoice, SingleChoice, APIResponse, TextInput, HealthBackground, ConversationId
from digidoc.forms.chat_forms import SendMessageForm, OnBoardingForm, MultipleChoiceForm, SingleChoiceForm, TextInputForm
from django.http import HttpResponse, QueryDict
from django.contrib.sessions.models import Session
from django.http import HttpResponseNotFound
from datetime import datetime
from django.utils.translation import gettext as _

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
                    "type": "generic", 
                        "input": { 
                            "include": selected_symptoms_ids,
                            "exclude": [] 
                        }
                },
            "conversation": { 
                "id": conversation_id
            }
        }

    def set_condition_confirmation_in_formatted_input(self, selected_symptoms_ids, conversation_id):
        self.formatted_input = {
            "answer":{
                "type": "symptoms",
                "selection": selected_symptoms_ids
            },
            "conversation":{
                "id": conversation_id
            }
        }

    def set_yes_no_response_in_formatted_input(self, selected_symptoms_ids, conversation_id):
        self.formatted_input = {
            "answer":{
                "type": "symptom",
                "selection": selected_symptoms_ids
            },
            "conversation":{
                "id": conversation_id
            }
        }
    def set_final_response_in_formatted_input(self, selected_id, conversation_id):
        self.formatted_input = {
            "answer":{
                "type":"generic",
                "input":{
                    "include":selected_id
                }
            },
            "conversation":{
                    "id": conversation_id
            }
        }

    def set_new_response(self):
        self.response = requests.post(self.url, json=self.formatted_input, headers=self.headers)

    def autocomplete_request(self,symptom):
        params = {
            'text': symptom,
        }

        response = requests.get('https://portal.your.md/v4/search/symptoms', params=params, headers=self.headers)
        return response.json()

    def set_autocomplete_post(self, selected_symptoms_ids, conversation_id):
        self.formatted_input = {
            "answer": { 
                "type": "autocomplete", 
                "selection":  selected_symptoms_ids   
            }, 
            "conversation": {
                "id": conversation_id 
            } 
        }

        
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
    
            # Create MultipleChoice object and save selected choice(s) to the database
            symptom = MultipleChoice(choice_id=symptom_id, name=symptom_label, conversation_id=symptom_conversation_id)
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
    
            # Create MultipleChoice object and save selected choice(s) to the database
            condition = MultipleChoice(choice_id=condition_id, name=condition_long_name, conversation_id=condition_conversation_id)
            condition.full_clean()
            condition.save()

def save_APIResponse(phase, question_type):
    response = APIResponse(phase=phase, question_type=question_type)
    response.full_clean()
    response.save()

def save_conversationID(convo_id):
    conversation = ConversationId(conversation_id=convo_id)
    conversation.full_clean()
    conversation.save()

def delete_database():
    # deletes contents of the database
    Message.objects.all().delete()
    OnBoarding.objects.all().delete()
    MultipleChoice.objects.all().delete() 
    SingleChoice.objects.all().delete()
    APIResponse.objects.all().delete()
    TextInput.objects.all().delete()
    HealthBackground.objects.all().delete()


def get_phase_from_api_response(api_response):
    return api_response['conversation']['phase']

def get_question_type_from_api_response(api_response):
    return api_response['question']['type']

def get_template_for_phase(phase):
    phase_templates = {
        'user_name': 'on_boarding.html',
        'symptom_check': 'chat.html',
        'autocomplete_start': 'chat.html',
        'clarify': 'chat.html',
        'duration': 'chat.html',
        'health_background': 'chat.html',
        'questions':'chat.html' ,
        'pre_diagnosis':'chat.html'

    }
    if phase in phase_templates:
        return phase_templates[phase]
    else:
        return 'chat.html'

def append_message(api_response):
    messages = []
    messages.append(api_response.get('question', {}).get('messages' , []))
    return messages

def get_text_content(messages):
    text_content = [msg['text'] for sublist in messages for msg in sublist if msg.get('type') == 'text']
    
    return text_content


def new_chat(request):
    response_data = Chat()
    delete_database()
    print(response_data.get_headers())

    response_data.set_response()
    status = response_data.get_response_status()
    print("Status: " + str(status))

    api_response= response_data.get_response_data()
    print(api_response)
    scenario = api_response.get('conversation', {}).get('scenario' , [])
    print("scenario")
    print(scenario)

    # Get the phase of the conversation
    phase = get_phase_from_api_response(api_response)
    question_type = get_question_type_from_api_response(api_response)
    save_APIResponse(phase, question_type)

    # the template based on the phase
    template_name = get_template_for_phase(phase)
    print("TEMPLATE")
    print(template_name)

    messages = append_message(api_response)
    text_content = [msg['text'] for sublist in messages for msg in sublist if msg.get('type') == 'text']
    
    # text_content = get_text_content(messages)
    print("text content")
    print(text_content)
    save_digidoc_message(text_content)
    conversation_id = api_response.get('conversation', {}).get('id' , None)
    save_conversationID(conversation_id)
    all_messages = Message.objects.all()
    for message in all_messages:
        print(message.content)
    if request.method == 'GET':
        if phase == 'user_name': 
            print("GET -- NEW CHAT")
            print("first 2:")
            first_two_messages = _(text_content[:2])
            print(first_two_messages)
            form = OnBoardingForm()
            return render(request, template_name, {'first_two_messages': first_two_messages, 'form': form, 'scenario': scenario})
 
def main_chat(request):
    # response_data = Chat()
    # api_response= response_data.get_response_data()
    # Get the phase of the conversation
    previous_phase = (APIResponse.objects.get()).phase
    print("previous PHASE")
    print(str(previous_phase))
    previous_question_type = (APIResponse.objects.get()).question_type
    print("previous question type")
    print(str(previous_question_type))
    # the default template 
    # template_name = None
    # form = None
    # print("TEMPLATE")
    # print(template_name)
    
    if request.method == 'POST':
        if previous_phase == 'user_name': 
            print("previous_phase -- user_name") 
            return send_on_boarding(request) 
        elif previous_phase == 'symptom_check': 
            print("previous_phase -- symptom_check") 
            return send_symptom_confirmation(request) 
        elif previous_phase == 'autocomplete_start':
            print("previous_phase -- autocomplete_start") 
            return submit_choice(request)
        elif previous_phase == 'autocomplete_add':
            print("previous_phase -- autocomplete_add") 
            return autocomplete(request)
        elif previous_phase == 'clarify': 
            print("previous_phase -- clarify") 
            return send_symptom_confirmation(request) 
        elif previous_phase == 'duration': 
            print("previous_phase -- duration") 
            return submit_choice(request)
        elif previous_phase == 'health_background':
            print("previous_phase -- health_background") 
            return send_condition(request)
        elif previous_phase == 'questions': 
            print("previous_phase -- questions") 
            if previous_question_type == 'symptoms':
                return send_next(request)
            elif previous_question_type == 'symptom':
                return send_next2(request)
            else:
                print("Previous question type does not exist")
        elif previous_phase == 'pre_diagnosis':
            print("previous_phase -- pre_diagnosis") 
            return send_final(request)
        elif previous_phase == 'dynamic_buttons':
            print("previous_phase -- dynamic_buttons") 
            form = None
        elif previous_phase == 'report':
            print("previous_phase -- report") 
            return send_final_continue(request)
        else:
            # If none of the conditions are met, return a default response
            return HttpResponseNotFound('Page not found')
       
def send_on_boarding(request):
    response_data = Chat()
    if request.method == 'POST': 
        APIResponse.objects.all().delete()

        print("POST -- on_boarding")        

        form = OnBoardingForm(request.POST)
        
        if form.is_valid():
            name = request.POST.get('name')
            birth_year = request.POST.get('birth_year')
            initial_symptoms = request.POST.get('initial_symptoms')
            gender = request.POST.get('gender')
            timestamp = request.POST.get('timestamp')
            initial_symptoms_splitted = initial_symptoms.split(", ")

            on_boarding_answers = OnBoarding(name=name, birth_year=birth_year, initial_symptoms=initial_symptoms_splitted, gender=gender, timestamp=timestamp)
            on_boarding_answers.full_clean()
            on_boarding_answers.save()

            content = "Name: " + str(name) + ", " + "Birth Year: " + str(birth_year) + ", " + "Initial Symptoms: " + str(initial_symptoms) + ", " + "Gender: " + str(gender)
            save_user_message(content, timestamp)

        response_data.set_on_boarding_answers_in_formatted_input(on_boarding_answers.name, on_boarding_answers.birth_year, on_boarding_answers.initial_symptoms, on_boarding_answers.gender)

        response = requests.post(response_data.url, json=response_data.formatted_input, headers=response_data.headers)
        print(response.json())
        api_response = response.json()

        phase = get_phase_from_api_response(api_response)
        question_type = get_question_type_from_api_response(api_response)
        save_APIResponse(phase, question_type)

        template_name = get_template_for_phase(phase)

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
        # text_content= get_text_content(messages)
        print("text content")
        print(text_content)
        save_digidoc_message(text_content)

        all_messages = Message.objects.all()
        for message in all_messages:
            print(message.content)

        save_symptoms(api_response)

        if multiple:
            form = MultipleChoiceForm()
        else:
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
                    chosen_option = SingleChoice(choice_id=choice_id, label=choice_label, conversation_id=choice_conversation_id)
                    chosen_option.full_clean()
                    chosen_option.save()
            form = SingleChoiceForm()
        # return api_response
        return render(request, template_name, {'messages': all_messages, 'form': form})



def send_symptom_confirmation(request):
    response_data = Chat()
    SingleChoice.objects.all().delete()
    if request.method == 'POST': 
        print("POST -- send_symptom_confirmation")        
        APIResponse.objects.all().delete()
        form = MultipleChoiceForm(request.POST)
        selected_symptoms_ids = []
        selected_symptoms_name = []
        if form.is_valid():
            selected_symptoms = form.cleaned_data['multiple_choices']
            # Handle the selected symptoms data
            for symptom in selected_symptoms:
          
                print(f"Selected Symptom: {symptom}")
    
                selected_symptoms_name.append(symptom.name)
                # Retrieves the symptom's choice_ID from the MultipleChoice object and append it to the list
                selected_symptoms_ids.append(symptom.choice_id)
            print(str(selected_symptoms_ids))
            conversation_id = MultipleChoice.objects.get(choice_id=selected_symptoms_ids[0]).conversation_id
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

        phase = get_phase_from_api_response(api_response)
        question_type = get_question_type_from_api_response(api_response)
        save_APIResponse(phase, question_type)

        template_name = get_template_for_phase(phase)

        # saves api response as messages
        messages = []
        messages.append(api_response.get('question', {}).get('messages' , []))
        print("MESSAGES")
        print(messages)
        # check the type of message
        message_type = api_response.get('question', {}).get('type' , [])
        print("MESSAGE TYPE")
        print(message_type)
        if message_type == 'generic':
            text_content = [msg['value'] for sublist in messages for msg in sublist if msg.get('type') == 'generic']
            print("text content")
            print(text_content)
        elif message_type == 'health_background':
            text_content = [msg['text'] for sublist in messages for msg in sublist if msg.get('type') == 'health_background']
            print("text content")
            print(text_content)
        else :
            text_content = "No content"

        save_digidoc_message(text_content)

        all_messages = Message.objects.all()
        # for message in all_messages:
        #     print(message.content)

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
                chosen_option = SingleChoice(choice_id=choice_id, label=choice_label, conversation_id=choice_conversation_id)
                chosen_option.full_clean()
                chosen_option.save()
        form = SingleChoiceForm()
        # return render(request, 'chat.html', {'messages': all_messages, 'form': form})
    else:
        form = MultipleChoiceForm()
    return render(request, 'chat.html', {'messages': all_messages, 'form': form})

def submit_choice(request):
    response_data = Chat()
    if request.method == 'POST': 
        print("POST -- submit_choice")        
        APIResponse.objects.all().delete()
        form = SingleChoiceForm(request.POST)
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
            conversation_id = SingleChoice.objects.get(choice_id=selected_choice_id[0]).conversation_id
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

            phase = get_phase_from_api_response(api_response)
            question_type = get_question_type_from_api_response(api_response)
            save_APIResponse(phase, question_type)

            template_name = get_template_for_phase(phase)
          
        else:
            print("NO")
        # saves api response as messages
        messages = []
        messages.append(api_response.get('question', {}).get('messages' , []))

        print("MESSAGES")
        print(messages)

        # check the type of message
        message_type = api_response.get('question', {}).get('type' , [])
        print("MESSAGE TYPE")
        print(message_type)
        if message_type == 'generic':
            text_content = [msg['value'] for sublist in messages for msg in sublist if msg.get('type') == 'generic']
            print("text content")
            print(text_content)
        elif message_type == 'health_background':
            text_content = [msg['text'] for sublist in messages for msg in sublist if msg.get('type') == 'text' or msg.get('type') == 'small_text']
            print("text content")
            print(text_content)
        elif message_type == 'autocomplete':
            text_content = [msg['text'] for sublist in messages for msg in sublist if msg.get('type') == 'text' or msg.get('type') == 'small_text']
            print("text content")
            print(text_content)
        else :
            text_content = "No content"
            print("text content")
            print(text_content)

        save_digidoc_message(text_content)

        all_messages = Message.objects.all()

        phase_value = api_response['conversation']['phase']
        print("phase")
        print(phase_value)
        if (phase_value=='info_result'):
            form = SingleChoiceForm()
            # Accessing the articles
            articles = api_response['report']['articles']
            request.session['articles'] = json.dumps(articles)
            return render(request, 'end_of_chat.html', {'messages': all_messages, 'form': form})
        elif (phase_value=='clarify'):
            MultipleChoice.objects.all().delete()
            save_symptoms(api_response)
            form = MultipleChoiceForm()
            return render(request, 'chat.html', {'messages': all_messages,'form': form})
        elif (phase_value=='health_background'):
            MultipleChoice.objects.all().delete()
            save_conditions(api_response)
            form = MultipleChoiceForm()
            return render(request, 'chat.html', {'messages': all_messages,'form': form})
        elif (phase_value=='autocomplete_add'):
            SingleChoice.objects.all().delete()
            list_of_choices = []
            list_of_choices.append(api_response.get('question', {}).get('choices' , []))

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
                    chosen_option = SingleChoice(choice_id=choice_id, label=choice_label, conversation_id=choice_conversation_id)
                    chosen_option.full_clean()
                    chosen_option.save()
            form1 = TextInputForm()
            form2 = SingleChoiceForm()
            symptoms_count = TextInput.objects.count()
            print("COUNT")
            print(symptoms_count)
            choices = SingleChoice.objects.all()
            return render(request, 'chat2.html', {'messages': all_messages,'form1': form1, 'form2': form2, 'symptoms_count': symptoms_count, 'choices':choices})
       
        else:
            pass
    else:
        form = MultipleChoiceForm()
    return render(request, 'chat.html', {'form': form})


def add_symptom(request):
    print("POST -- add_symptom")
    symptoms_count = TextInput.objects.count()
    print("COUNT")
    print(symptoms_count)
    symptoms = TextInput.objects.all()
    is_database_empty = TextInput.objects.count() > 0
    form2 = SingleChoiceForm()
    choices = SingleChoice.objects.all()
    if symptoms_count >= 3:
        choice_id = 'empty_id_autocomplete'
        form2 = SingleChoiceForm(initial=choice_id)
        return render(request, 'chat2.html', {'form2': form2, 'symptoms':symptoms,'symptoms_count': symptoms_count, 'choices':choices})
    if request.method == 'POST':
        form = TextInputForm(request.POST)
        if form.is_valid():
            form.save()
            # return redirect('add_symptom')
            form1 = TextInputForm()
            symptoms_count = TextInput.objects.count()
            print("COUNT")
            print(symptoms_count)
            if symptoms_count == 0:
                choice_id = 'cant_find_symptoms'
                form2 = SingleChoiceForm(initial={'choice_id': choice_id})
            else:
                choice_id = 'empty_id_autocomplete'
                form2 = SingleChoiceForm(initial={'choice_id': choice_id})
            return render(request, 'chat2.html', {'form1': form1, 'form2':form2, 'symptoms':symptoms, 'symptoms_count': symptoms_count, 'choices': choices})
    else:
        form1 = TextInputForm()
        form2 = form2 = SingleChoiceForm()
    return render(request, 'chat2.html', {'form1': form1, 'form2':form2, 'symptoms':symptom, 'symptoms_count': symptoms_count, 'choices':choices})

def autocomplete(request):
    response_data = Chat()
    if request.method == 'GET': 
        print("GET -- autocomplete")        
        APIResponse.objects.all().delete()
        response = []
        added_symptoms = TextInput.objects.values_list('symptom_name', flat=True)
        conversation_id = ConversationId.objects.first()
        # Convert QuerySet to a Python list
        added_symptoms_list = list(added_symptoms)
        for symptom in added_symptoms_list:
            api_response = response_data.autocomplete_request(symptom)
            print(api_response)
            response.append(api_response)
        MultipleChoice.objects.all().delete()
        print("response")
        print(response)
        for item in response:
            autocomplete_list = item.get('autocomplete', []) 
            for suggestion in autocomplete_list:
                user_facing_name = suggestion.get('user_facing_name')
                choice_id = suggestion.get('id')
                print("User Facing Name:", user_facing_name)
                print("ID:", choice_id)
                # Create  object and save to database
                chosen_option = MultipleChoice(choice_id=choice_id, name=user_facing_name, conversation_id=conversation_id)
                chosen_option.full_clean()
                chosen_option.save()
            form = MultipleChoiceForm() 
        return render(request, 'chat3.html', {'form':form})
    return render(request, 'chat3.html', {'form':form})

def autocomplete_post(request):
    response_data = Chat()
    if request.method == 'POST': 
        print("GET -- autocomplete_post")        
        APIResponse.objects.all().delete()
        form = MultipleChoiceForm(request.POST)
        selected_symptom_ids = []
        selected_symptom_name = []
        if form.is_valid():
            selected_symptoms = form.cleaned_data['multiple_choices']
            # Handle the selected condition data
            for symptom in selected_symptoms:
          
                print(f"Selected symptom: {symptom}")
    
                selected_symptom_name.append(symptom.name)
                # Retrieves the symptom ID from the symptom object and append it to the list
                selected_symptom_ids.append(symptom.choice_id)
                
            print(str(selected_symptom_ids))

            conversation_id = MultipleChoice.objects.get(choice_id=selected_symptom_ids[0]).conversation_id
            print("convo id")
            print(conversation_id)
            print("selected_symptom_name")
            print(str(selected_symptom_name))
            content = "I confirm that I have the following condition(s): " + str(selected_symptom_name)
            timestamp = request.POST.get('timestamp')
            save_user_message(content, timestamp)
            MultipleChoice.objects.all().delete()

            response_data.set_autocomplete_post(selected_symptom_ids, conversation_id)
            print(response_data.formatted_input)
            response = requests.post(response_data.url, json=response_data.formatted_input, headers=response_data.headers)
            print(response.json())
            api_response = response.json()

            # phase = get_phase_from_api_response(api_response)
            # question_type = get_question_type_from_api_response(api_response)
            # save_APIResponse(phase, question_type)

            template_name = get_template_for_phase(phase)

        else:
            print("NO")
        # saves api response as messages
        messages = []
        messages.append(api_response.get('question', {}).get('messages' , []))


        print("MESSAGES")
        print(messages)

        # check the type of message
        message_type = api_response.get('question', {}).get('type' , [])
        print("MESSAGE TYPE")
        print(message_type)
        if message_type == 'generic':
            text_content = [msg['value'] for sublist in messages for msg in sublist if msg.get('type') == 'generic']
            print("text content")
            print(text_content)
        elif message_type == 'health_background':
            text_content = [msg['text'] for sublist in messages for msg in sublist if msg.get('type') == 'text' or msg.get('type') == 'small_text']
            print("text content")
            print(text_content)
        elif message_type == 'symptoms':
            text_content = [msg['text'] for sublist in messages for msg in sublist if msg.get('type') == 'text']
            print("text content")
            print(text_content)
        else :
            text_content = "No content"
            print("text content")
            print(text_content)
        # text_content = [msg['value'] for sublist in messages for msg in sublist if msg.get('type') == 'generic']
        # print("text content")
        # print(text_content)
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
                # Extracts choice id and label
                choice_id = choice['id']
                print("CHOICE ID")
                print(choice_id)
                choice_label = choice['text']
                print("CHOICE LABEL")
                print(choice_label)
                # selected = True
                choice_conversation_id = conversation_id
        
                # Create  object and save to database
                chosen_option = MultipleChoice(choice_id=choice_id, name=choice_label, conversation_id=choice_conversation_id)
                chosen_option.full_clean()
                chosen_option.save()
            form = MultipleChoiceForm()
        return render(request, 'chat.html', {'messages': all_messages, 'form': form})
    else:
        form = MultipleChoiceForm()
    return render(request, 'chat.html', {'form': form})

def add_more_symptoms(request):
    response_data = Chat()
    if request.method == 'POST': 
        print("POST -- add_more_symptoms")        
        APIResponse.objects.all().delete()
        form = SingleChoiceForm(request.POST)
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
            conversation_id = SingleChoice.objects.get(choice_id=selected_choice_id[0]).conversation_id
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

            phase = get_phase_from_api_response(api_response)
            question_type = get_question_type_from_api_response(api_response)
            save_APIResponse(phase, question_type)
        else:
            print("NO")
        # saves api response as messages
        messages = []
        messages.append(api_response.get('question', {}).get('messages' , []))

        print("MESSAGES")
        print(messages)

        # check the type of message
        message_type = api_response.get('question', {}).get('type' , [])
        print("MESSAGE TYPE")
        print(message_type)
        if message_type == 'generic':
            text_content = [msg['value'] for sublist in messages for msg in sublist if msg.get('type') == 'generic']
            print("text content")
            print(text_content)
        elif message_type == 'health_background':
            text_content = [msg['text'] for sublist in messages for msg in sublist if msg.get('type') == 'text' or msg.get('type') == 'small_text']
            print("text content")
            print(text_content)
             
        else :
            text_content = "No content"
            print("text content")
            print(text_content)

        save_digidoc_message(text_content)

        all_messages = Message.objects.all()

        MultipleChoice.objects.all().delete()
        save_symptoms(api_response)
        form = MultipleChoiceForm()
        return render(request, 'chat.html', {'messages': all_messages,'form': form})
    else:
        form = MultipleChoiceForm()
    return render(request, 'chat.html', {'form': form})

def send_condition(request):
    
    response_data = Chat()
    # MultipleChoice.objects.all().delete()
    if request.method == 'POST': 
        print("POST -- send_condition")        
        APIResponse.objects.all().delete()
        form = MultipleChoiceForm(request.POST)
        selected_condition_ids = []
        selected_condition_name = []
        if form.is_valid():
            selected_conditions = form.cleaned_data['multiple_choices']
            # Handle the selected condition data
            for condition in selected_conditions:
          
                print(f"Selected condition: {condition}")
    
                selected_condition_name.append(condition.name)
                # Retrieves the symptom ID from the symptom object and append it to the list
                selected_condition_ids.append(condition.choice_id)
                health_background = HealthBackground(condition_id = condition.choice_id)
                health_background.full_clean()
                health_background.save()
            print(str(selected_condition_ids))

            conversation_id = MultipleChoice.objects.get(choice_id=selected_condition_ids[0]).conversation_id
            print("convo id")
            print(conversation_id)
            print("selected_condition_name")
            print(str(selected_condition_name))
            content = "I confirm that I have the following condition(s): " + str(selected_condition_name)
            timestamp = request.POST.get('timestamp')
            save_user_message(content, timestamp)
            MultipleChoice.objects.all().delete()

            response_data.set_condition_confirmation_in_formatted_input(selected_condition_ids, conversation_id)

            response = requests.post(response_data.url, json=response_data.formatted_input, headers=response_data.headers)
            print(response.json())
            api_response = response.json()

            phase = get_phase_from_api_response(api_response)
            question_type = get_question_type_from_api_response(api_response)
            save_APIResponse(phase, question_type)

            template_name = get_template_for_phase(phase)

        else:
            print("NO")
        # saves api response as messages
        messages = []
        messages.append(api_response.get('question', {}).get('messages' , []))


        print("MESSAGES")
        print(messages)

        # check the type of message
        message_type = api_response.get('question', {}).get('type' , [])
        print("MESSAGE TYPE")
        print(message_type)
        if message_type == 'generic':
            text_content = [msg['value'] for sublist in messages for msg in sublist if msg.get('type') == 'generic']
            print("text content")
            print(text_content)
        elif message_type == 'health_background':
            text_content = [msg['text'] for sublist in messages for msg in sublist if msg.get('type') == 'text' or msg.get('type') == 'small_text']
            print("text content")
            print(text_content)
        elif message_type == 'symptoms':
            text_content = [msg['text'] for sublist in messages for msg in sublist if msg.get('type') == 'text']
            print("text content")
            print(text_content)
        else :
            text_content = "No content"
            print("text content")
            print(text_content)
        # text_content = [msg['value'] for sublist in messages for msg in sublist if msg.get('type') == 'generic']
        # print("text content")
        # print(text_content)
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
                # Extracts choice id and label
                choice_id = choice['id']
                print("CHOICE ID")
                print(choice_id)
                choice_label = choice['text']
                print("CHOICE LABEL")
                print(choice_label)
                # selected = True
                choice_conversation_id = conversation_id
        
                # Create  object and save to database
                chosen_option = MultipleChoice(choice_id=choice_id, name=choice_label, conversation_id=choice_conversation_id)
                chosen_option.full_clean()
                chosen_option.save()
            form = MultipleChoiceForm()
        return render(request, 'chat.html', {'messages': all_messages, 'form': form})
    else:
        form = MultipleChoiceForm()
    return render(request, 'chat.html', {'form': form})
      
def send_next(request):
    response_data = Chat()
    html = 'chat.html'
    if request.method == 'POST': 
        print("POST -- send_next")        
        
        form = MultipleChoiceForm(request.POST)
        selected_symptoms_ids = []
        selected_symptoms_name = []
        if form.is_valid():
            selected_symptoms = form.cleaned_data['multiple_choices']
            # Handle the selected symptoms data
            for symptom in selected_symptoms:
          
                print(f"Selected Symptom: {symptom}")
    
                selected_symptoms_name.append(symptom.name)
                # Retrieves the symptom's choice_ID from the MultipleChoice object and append it to the list
                selected_symptoms_ids.append(symptom.choice_id)
            print(str(selected_symptoms_ids))
            conversation_id = MultipleChoice.objects.get(choice_id=selected_symptoms_ids[0]).conversation_id
            print("convo id")
            print(conversation_id)
            print("selected_symptoms_name")
            print(str(selected_symptoms_name))
            content = "I confirm that I have the following symptom(s): " + str(selected_symptoms_name)
            timestamp = request.POST.get('timestamp')
            save_user_message(content, timestamp)
            MultipleChoice.objects.all().delete()
            SingleChoice.objects.all().delete()
        # response_data.set_condition_confirmation_in_formatted_input(selected_symptoms_ids, conversation_id)
            # previous_question_type = (APIResponse.objects.get()).question_type
            # question_type = api_response.get('question', {}).get('type')
            
            response_data.set_condition_confirmation_in_formatted_input(selected_symptoms_ids, conversation_id)
           
           
        response = requests.post(response_data.url, json=response_data.formatted_input, headers=response_data.headers)
        print(response.json())
        api_response = response.json()
        APIResponse.objects.all().delete()
        phase = get_phase_from_api_response(api_response)
        question_type = get_question_type_from_api_response(api_response)
        save_APIResponse(phase, question_type)

        template_name = get_template_for_phase(phase)

        # saves api response as messages
        messages = []
        messages.append(api_response.get('question', {}).get('messages' , []))

        print("MESSAGES")
        print(messages)
        # check the type of message
        message_type = api_response.get('question', {}).get('type' , [])
        print("MESSAGE TYPE")
        print(message_type)
        if message_type == 'generic':
            text_content = [msg['value'] for sublist in messages for msg in sublist if msg.get('type') == 'generic']
            print("text content")
            print(text_content)
        elif message_type == 'health_background':
            text_content = [msg['text'] for sublist in messages for msg in sublist if msg.get('type') == 'health_background']
            print("text content")
            print(text_content)
        elif message_type == 'symptoms':
            text_content = [msg['text'] for sublist in messages for msg in sublist if msg.get('type') == 'text']
            print("text content symptoms")
            print(text_content)
        elif message_type == 'symptom':
            text_content = [msg['text'] for sublist in messages for msg in sublist if msg.get('type') == 'text']
            print("text content symptom")
            print(text_content)
        
        else :
            text_content = "No content"

        save_digidoc_message(text_content)

        all_messages = Message.objects.all()
        for message in all_messages:
            print(message.content)

        list_of_choices = []
        list_of_choices.append(api_response.get('question', {}).get('choices' , []))

        conversation_id = api_response.get('conversation', {}).get('id' , None)

        print("CHOICES")
        print(list_of_choices)
        # Check if 'max_selections' exists in the 'constraints' dictionary
        if 'constraints' in api_response['question'] and 'max_selections' in api_response['question']['constraints']:
            max_selections = api_response['question']['constraints']['max_selections']
            print("Max Selections:", max_selections)
        else:
            print("'max_selections' not found in constraints")
        if 'constraints' in api_response['question'] and 'max_selections' in api_response['question']['constraints']:
            # max_selections_exist = true
            max_selections = api_response['question']['constraints']['max_selections']
            print("max_selections exist")

            if (max_selections == 1):
                form = SingleChoiceForm()
                print("Choose 1!!!")
                html = 'chat.html'
                for sublist in list_of_choices:
                    for choice in sublist:
                        # Extracts choice id and label
                        choice_id = choice['id']
                        choice_label = choice['text']
                        # selected = True
                        choice_conversation_id = conversation_id
                
                        # Create Symptom object and save to database
                        chosen_option = SingleChoice(choice_id=choice_id, label=choice_label, conversation_id=choice_conversation_id)
                        chosen_option.full_clean()
                        chosen_option.save()
            else:
                form = MultipleChoiceForm()
                print("Multiple choice!!!!")
                html = 'chat.html'
                for sublist in list_of_choices:
                    for choice in sublist:
                        # Extracts choice id and label
                        choice_id = choice['id']
                        choice_label = choice['text']
                        # selected = True
                        choice_conversation_id = conversation_id
                
                        # Create Symptom object and save to database
                        chosen_option = MultipleChoice(choice_id=choice_id, name=choice_label, conversation_id=choice_conversation_id)
                        chosen_option.full_clean()
                        chosen_option.save()
        else:
            print("max_selections DOESNT exist")
            form = SingleChoiceForm()
            html = 'chat.html'
            for sublist in list_of_choices:
                for choice in sublist:
                    # Extracts choice id and label
                    choice_id = choice['id']
                    if 'text' in choice:
                        # The choice uses 'text'
                        choice_label = choice['text']
 
                    elif 'label' in choice:
                        # The choice uses 'label'
                        choice_label = choice['label']
                    # selected = True
                    choice_conversation_id = conversation_id
            
                    # Create Symptom object and save to database
                    chosen_option = SingleChoice(choice_id=choice_id, label=choice_label, conversation_id=choice_conversation_id)
                    chosen_option.full_clean()
                    chosen_option.save()
    
        return render(request, html, {'messages': all_messages, 'form': form})
    else:
        form = MultipleChoiceForm()
    return render(request, html, {'form': form})

def send_next2(request):
    
    response_data = Chat()
    html = 'chat.html'
    if request.method == 'POST': 
        print("POST -- send_next2")        
        APIResponse.objects.all().delete()
        form = SingleChoiceForm(request.POST)
        selected_choice_id = []
        selected_choice_label = []
        if form.is_valid():
            choice = form.cleaned_data['choices']
            print(f"Selected choice: {choice}")

            selected_choice_label.append(choice.label)
            # Retrieves the choice ID from the choice object and append it to the list
            selected_choice_id.append(choice.choice_id)
            print(str(selected_choice_id))
            conversation_id = SingleChoice.objects.get(choice_id=selected_choice_id[0]).conversation_id
            print("convo id")
            print(conversation_id)
            print("selected_choice_name")
            print(str(selected_choice_label))
            content = "I confirm that I have the following symptom(s): " + str(selected_choice_label)
            timestamp = request.POST.get('timestamp')
            save_user_message(content, timestamp)
            MultipleChoice.objects.all().delete()
            SingleChoice.objects.all().delete()
            
        response_data.set_yes_no_response_in_formatted_input(selected_choice_id, conversation_id)

        response = requests.post(response_data.url, json=response_data.formatted_input, headers=response_data.headers)
        print(response.json())
        api_response = response.json()

        phase = get_phase_from_api_response(api_response)
        question_type = get_question_type_from_api_response(api_response)
        save_APIResponse(phase, question_type)

        template_name = get_template_for_phase(phase)
       
        # saves api response as messages
        messages = []
        messages.append(api_response.get('question', {}).get('messages' , []))

        print("MESSAGES")
        print(messages)
        # check the type of message
        message_type = api_response.get('question', {}).get('type' , [])
        print("MESSAGE TYPE")
        print(message_type)
        if message_type == 'generic':
            text_content = [msg['value'] for sublist in messages for msg in sublist if msg.get('type') == 'generic']
            print("text content")
            print(text_content)
        elif message_type == 'health_background':
            text_content = [msg['text'] for sublist in messages for msg in sublist if msg.get('type') == 'health_background']
            print("text content")
            print(text_content)
        elif message_type == 'symptoms':
            text_content = [msg['text'] for sublist in messages for msg in sublist if msg.get('type') == 'text']
            print("text content symptoms")
            print(text_content)
        elif message_type == 'symptom':
            text_content = [msg['text'] for sublist in messages for msg in sublist if msg.get('type') == 'text']
            print("text content symptom")
            print(text_content)
        
        else :
            text_content = "No content"

        save_digidoc_message(text_content)

        all_messages = Message.objects.all()
        for message in all_messages:
            print(message.content)

        list_of_choices = []
        list_of_choices.append(api_response.get('question', {}).get('choices' , []))

        conversation_id = api_response.get('conversation', {}).get('id' , None)

        print("CHOICES")
        print(list_of_choices)
        if 'constraints' in api_response['question'] and 'max_selections' in api_response['question']['constraints']:
            # max_selections_exist = true
            max_selections = api_response['question']['constraints']['max_selections']
 

            if (max_selections == 1):
                form = SingleChoiceForm()
                print("Choose 1!!!")
                html = 'chat.html'
                for sublist in list_of_choices:
                    for choice in sublist:
                        # Extracts choice id and label
                        choice_id = choice['id']
                        choice_label = choice['text']
                        # selected = True
                        choice_conversation_id = conversation_id
                
                        # Create Symptom object and save to database
                        chosen_option = SingleChoice(choice_id=choice_id, label=choice_label, conversation_id=choice_conversation_id)
                        chosen_option.full_clean()
                        chosen_option.save()
            else:
                form = MultipleChoiceForm()
                print("Multiple choice!!!!")
                html = 'chat.html'
                for sublist in list_of_choices:
                    for choice in sublist:
                        # Extracts choice id and label
                        choice_id = choice['id']
                        choice_label = choice['text']
                        # selected = True
                        choice_conversation_id = conversation_id
                
                        # Create Symptom object and save to database
                        chosen_option = MultipleChoice(choice_id=choice_id, name=choice_label, conversation_id=choice_conversation_id)
                        chosen_option.full_clean()
                        chosen_option.save()
        else:
            form = SingleChoiceForm()
            html = 'chat.html'
            for sublist in list_of_choices:
                for choice in sublist:
                    # Extracts choice id and label
                    choice_id = choice['id']
                    if 'text' in choice:
                        # The choice uses 'text'
                        choice_label = choice['text']
 
                    elif 'label' in choice:
                        # The choice uses 'label'
                        choice_label = choice['label']
                    # selected = True
                    choice_conversation_id = conversation_id
            
                    # Create Symptom object and save to database
                    chosen_option = SingleChoice(choice_id=choice_id, label=choice_label, conversation_id=choice_conversation_id)
                    chosen_option.full_clean()
                    chosen_option.save()
        
        return render(request, html, {'messages': all_messages, 'form': form})
    else:
        form = MultipleChoiceForm()
    return render(request, 'chat.html', {'form': form})



def send_final(request):
    response_data = Chat()
    html = 'report_summary.html'
    if request.method == 'POST': 
        print("POST -- send_final")        
        APIResponse.objects.all().delete()
        form = SingleChoiceForm(request.POST)
        selected_choice_id = []
        selected_choice_label = []
        if form.is_valid():
            choice = form.cleaned_data['choices']
            print(f"Selected choice: {choice}")

            selected_choice_label.append(choice.label)
            # Retrieves the choice ID from the choice object and append it to the list
            selected_choice_id.append(choice.choice_id)
            print(str(selected_choice_id))
            conversation_id = SingleChoice.objects.get(choice_id=selected_choice_id[0]).conversation_id
            print("convo id")
            print(conversation_id)
            print("selected_choice_name")
            print(str(selected_choice_label))
            content = "I confirm that I have the following symptom(s): " + str(selected_choice_label)
            timestamp = request.POST.get('timestamp')
            save_user_message(content, timestamp)
            MultipleChoice.objects.all().delete()
            SingleChoice.objects.all().delete()
            
        response_data.set_final_response_in_formatted_input(selected_choice_id, conversation_id)

        response = requests.post(response_data.url, json=response_data.formatted_input, headers=response_data.headers)
        print(response.json())
        api_response = response.json()

        phase = get_phase_from_api_response(api_response)
        question_type = get_question_type_from_api_response(api_response)
        save_APIResponse(phase, question_type)

        template_name = get_template_for_phase(phase)

        # saves api response as messages
        messages = []
        messages.append(api_response.get('question', {}).get('messages' , []))

        print("MESSAGES")
        print(messages)

        consultation_triage = api_response['report']['summary']['consultation_triage']
        print("CONSULTATION TRIAGE")
        print(consultation_triage)

        possible_conditions = api_response['report']['summary']['articles_v3']
        print("POSSIBLE CONDITIONS")
        print(possible_conditions)

        metadata = api_response['report']['summary']['articles_v3'][0]['metadata']
        triage_worries = api_response['report']['summary']['articles_v3'][0]['content']['triage']['triage_worries']
        # Replace newline characters with <br> tags
        triage_worries_html = triage_worries.replace('\n', '<br>')
        influencing_factors = api_response['report']['summary']['influencing_factors']
        user_profile = api_response['report']['summary']['user_profile']
        duration = api_response['report']['summary']['duration']
        extracted_symptoms =api_response['report']['summary']['extracted_symptoms']
        additional_symptoms = api_response['report']['summary']['additional_symptoms']
        negative_symptoms = api_response['report']['summary']['negative_symptoms']
        unsure_symptoms = api_response['report']['summary']['unsure_symptoms']
        user_profile = api_response['report']['summary']['user_profile']
        
        timestamp = datetime.now()

        health_background_conditions_list = []
        condition_ids = list(HealthBackground.objects.values_list('condition_id', flat=True))
        print("condition_ids")
        print(condition_ids)
        for factor in influencing_factors:
            health_background_conditions = {}
            print("factor")
            print(factor)
            if factor['cui'] in condition_ids:
                health_background_conditions["name"] = factor['long_name']          
                health_background_conditions["patient_has_condition"] = "Yes"
            else:
                health_background_conditions["name"] = factor['long_name']
                health_background_conditions["patient_has_condition"] = "No"
            health_background_conditions_list.append(health_background_conditions)
        print(health_background_conditions_list)

        # check the type of message
        message_type = api_response.get('question', {}).get('type' , [])
        print("MESSAGE TYPE")
        print(message_type)
        if message_type == 'generic':
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

        for sublist in list_of_choices:
            for choice in sublist:
                # Extracts choice id and label
                choice_id = choice['id']
                choice_label = choice['label']
                # selected = True
                choice_conversation_id = conversation_id
        
                # Create Symptom object and save to database
                chosen_option = SingleChoice(choice_id=choice_id, label=choice_label, conversation_id=choice_conversation_id)
                chosen_option.full_clean()
                chosen_option.save()
        context = {
                'text_content': text_content, 
                'form':form, 
                'consultation_triage': consultation_triage, 
                'possible_conditions': possible_conditions, 
                'metadata':metadata, 
                'triage_worries': triage_worries_html, 
                'influencing_factors': influencing_factors, 
                'user_profile': user_profile,
                'duration': duration,
                'extracted_symptoms': extracted_symptoms,
                'additional_symptoms': additional_symptoms,
                'negative_symptoms': negative_symptoms,
                'unsure_symptoms': unsure_symptoms,
                'user_profile': user_profile,
                'health_background_conditions': health_background_conditions_list,
                'timestamp': timestamp
        }

        return render(request, html, context)
def send_final_continue(request):
    print("POST -- send_final_continue")
    response_data = Chat()
    html = 'report.html'
    if request.method == 'POST': 
        print("POST -- send_final")        
        APIResponse.objects.all().delete()
        form = SingleChoiceForm(request.POST)
        selected_choice_id = []
        selected_choice_label = []
        if form.is_valid():
            choice = form.cleaned_data['choices']
            print(f"Selected choice: {choice}")

            selected_choice_label.append(choice.label)
            # Retrieves the choice ID from the choice object and append it to the list
            selected_choice_id.append(choice.choice_id)
            print(str(selected_choice_id))
            conversation_id = SingleChoice.objects.get(choice_id=selected_choice_id[0]).conversation_id
            print("convo id")
            print(conversation_id)
            print("selected_choice_name")
            print(str(selected_choice_label))
            content = "I confirm that I have the following symptom(s): " + str(selected_choice_label)
            timestamp = request.POST.get('timestamp')
            save_user_message(content, timestamp)
            MultipleChoice.objects.all().delete()
            SingleChoice.objects.all().delete()
            
        response_data.set_final_response_in_formatted_input(selected_choice_id, conversation_id)

        response = requests.post(response_data.url, json=response_data.formatted_input, headers=response_data.headers)
        print(response.json())
        api_response = response.json()

        phase = get_phase_from_api_response(api_response)
        question_type = get_question_type_from_api_response(api_response)
        save_APIResponse(phase, question_type)

        template_name = get_template_for_phase(phase)

        # saves api response as messages
        messages = []
        messages.append(api_response.get('question', {}).get('messages' , []))

        print("MESSAGES")
        print(messages)
        text_content = [msg['value'] for sublist in messages for msg in sublist if msg.get('type') == 'generic']
        save_digidoc_message(text_content)
        list_of_choices = []
        list_of_choices.append(api_response.get('question', {}).get('choices' , []))

        conversation_id = api_response.get('conversation', {}).get('id' , None)

        for sublist in list_of_choices:
            for choice in sublist:
                # Extracts choice id and label
                choice_id = choice['id']
                choice_label = choice['label']
                # selected = True
                choice_conversation_id = conversation_id
        
                # Create Symptom object and save to database
                chosen_option = SingleChoice(choice_id=choice_id, label=choice_label, conversation_id=choice_conversation_id)
                chosen_option.full_clean()
                chosen_option.save()
    return render(request, html, {'text_content':text_content, 'form':form})

def see_articles(request):
    articles = json.loads(request.session['articles'])
    print("articles")
    print(articles)
    # Render report.html with articles data
    return render(request, 'articles.html', {'articles': articles})

def thank_you(request):
    return render(request, 'thank_you.html')