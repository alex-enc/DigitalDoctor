from django.shortcuts import render, redirect
from django.contrib import messages
import requests
import json
from digidoc.models.message_models import OnBoarding, MultipleChoice, SingleChoice, APIResponse, TextInput, HealthBackground, ConversationId, Language
from digidoc.forms.chat_forms import OnBoardingForm, MultipleChoiceForm, SingleChoiceForm, TextInputForm
from django.http import HttpResponse, QueryDict
from django.contrib.sessions.models import Session
from django.http import HttpResponseNotFound
from datetime import datetime
# from django.utils.translation import gettext as _
from easygoogletranslate import EasyGoogleTranslate


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

    def set_yes_no_response_in_formatted_input(self, type, selected_symptoms_ids, conversation_id):
        self.formatted_input = {
            "answer":{
                "type": type,
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
    
    def set_factor_response(self, selected_id, conversation_id):
        self.formatted_input = {
            "answer":{
                "type":"factor",
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
        print(params)
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

def save_mcq_label(target_language_code, api_response):
    MultipleChoice.objects.all().delete()
    all_symptoms=[]
    all_symptoms.append(api_response.get('question', {}).get('choices' , []))
    conversation_id = api_response.get('conversation', {}).get('id' , None)
    print("convo id")
    print(conversation_id)
    print("SYMPTOM CHOICES")
    print(all_symptoms)
    print(len(all_symptoms))

    for sublist in all_symptoms:
        for symptom_data in sublist:
            # Extracts symptom id and label
            symptom_id = symptom_data['id']
            if target_language_code == 'en':
                symptom_label = symptom_data['label']
            else:
                symptom_label = translate(target_language_code, symptom_data['label'])
            symptom_conversation_id = conversation_id
    
            # Create MultipleChoice object and save selected choice(s) to the database
            symptom = MultipleChoice(choice_id=symptom_id, name=symptom_label, conversation_id=symptom_conversation_id)
            symptom.full_clean()
            symptom.save()

def save_mcq_long_name(target_language_code, api_response):
    MultipleChoice.objects.all().delete()
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
            if target_language_code == 'en':
                condition_long_name = health_condition_data['long_name']
            else:
                condition_long_name = translate(target_language_code, health_condition_data['long_name'])
            condition_conversation_id = conversation_id
    
            # Create MultipleChoice object and save selected choice(s) to the database
            condition = MultipleChoice(choice_id=condition_id, name=condition_long_name, conversation_id=condition_conversation_id)
            condition.full_clean()
            condition.save()
    
def save_mcq_text(target_language_code, api_response):
    MultipleChoice.objects.all().delete()
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
            if target_language_code == 'en':
                choice_label = choice['text']
            else:
                choice_label = translate(target_language_code, choice['text'])
            print("CHOICE TEXT")
            print(choice_label)
            # selected = True
            choice_conversation_id = conversation_id
    
            # Create  object and save to database
            chosen_option = MultipleChoice(choice_id=choice_id, name=choice_label, conversation_id=choice_conversation_id)
            chosen_option.full_clean()
            chosen_option.save()

def save_choices_label(target_language_code, api_response):
        SingleChoice.objects.all().delete()
        list_of_choices = []
        list_of_choices.append(api_response.get('question', {}).get('choices' , []))

        conversation_id = api_response.get('conversation', {}).get('id' , None)

        print("CHOICES")
        print(list_of_choices)
        for sublist in list_of_choices:
            for choice in sublist:
                # Extracts symptom id and label
                choice_id = choice['id']
                if target_language_code == 'en':
                    choice_label = choice['label']
                else:
                    choice_label = translate(target_language_code, choice['label'])
                # selected = True
                choice_conversation_id = conversation_id
        
                # Create Symptom object and save to database
                chosen_option = SingleChoice(choice_id=choice_id, label=choice_label, conversation_id=choice_conversation_id)
                chosen_option.full_clean()
                chosen_option.save()

def save_choices_text(target_language_code, api_response):
        SingleChoice.objects.all().delete()
        list_of_choices = []
        list_of_choices.append(api_response.get('question', {}).get('choices' , []))

        conversation_id = api_response.get('conversation', {}).get('id' , None)

        print("CHOICES")
        print(list_of_choices)
        for sublist in list_of_choices:
            for choice in sublist:
                # Extracts symptom id and label
                choice_id = choice['id']
                if target_language_code == 'en':
                    choice_label = choice['text']
                else:
                    choice_label = translate(target_language_code, choice['text'])
                # selected = True
                choice_conversation_id = conversation_id
        
                # Create Symptom object and save to database
                chosen_option = SingleChoice(choice_id=choice_id, label=choice_label, conversation_id=choice_conversation_id)
                chosen_option.full_clean()
                chosen_option.save()

def save_APIResponse(phase, question_type, choice_type):
    APIResponse.objects.all().delete()
    response = APIResponse(phase=phase, question_type=question_type, choice_type=choice_type)
    response.full_clean()
    response.save()

def save_conversationID(convo_id):
    ConversationId.objects.all().delete()
    conversation = ConversationId(conversation_id=convo_id)
    conversation.full_clean()
    conversation.save()

def delete_database():
    # deletes contents of the database
    # Message.objects.all().delete()
    OnBoarding.objects.all().delete()
    MultipleChoice.objects.all().delete() 
    SingleChoice.objects.all().delete()
    APIResponse.objects.all().delete()
    TextInput.objects.all().delete()
    HealthBackground.objects.all().delete()
    Language.objects.all().delete()
    ConversationId.objects.all().delete()


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

def get_language_code(language):
    if language == 'English':
        return 'en'
    elif language == 'Spanish':
        return 'es'
    elif language == 'French':
        return 'fr'
    elif language == 'Filipino':
        return 'fil'

def translate(target_language_code, content):
    translator = EasyGoogleTranslate(
        source_language='en',
        target_language=target_language_code,
        timeout=10
    )
    result = translator.translate(content)
    return result

def translate_to_english(source_language_code, content):
    translator = EasyGoogleTranslate(
    source_language='source_language_code',
    target_language='en',
    timeout=1000
    )
    result = translator.translate(content)
    return result

def get_language_used():
    language = (Language.objects.first()).language_code
    return language

def new_chat(request):
    response_data = Chat()
    delete_database()
    if request.method == 'POST':
        selected_language = request.POST.get('language')
        print(selected_language)
        target_language_code=get_language_code(selected_language)
        language = Language(language=selected_language, language_code = target_language_code)
        language.full_clean()
        language.save()


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
    choice_type = "on_boarding"
    save_APIResponse(phase, question_type, choice_type)

    # the template based on the phase
    template_name = get_template_for_phase(phase)
    print("TEMPLATE")
    print(template_name)

    messages = append_message(api_response)
    text_content = [msg['text'] for sublist in messages for msg in sublist if msg.get('type') == 'text']
    
    print("text content")
    print(text_content)
    translated_messages = []

    for message in text_content:
        print(message)
        print(translate(target_language_code, message))
        translated_messages.append(translate(target_language_code, message))
    conversation_id = api_response.get('conversation', {}).get('id' , None)
    print("conversation id")
    print(conversation_id)
    save_conversationID(conversation_id)

    # if request.method == 'GET':
    if phase == 'user_name': 
        print("GET -- NEW CHAT")
        print("first 2:")
        first_two_messages = translated_messages[:2]
        print(first_two_messages)
        form = OnBoardingForm()
        female_option = SingleChoice(choice_id='female', label='Female', conversation_id=conversation_id)
        female_option.full_clean()
        female_option.save()
        male_option = SingleChoice(choice_id='male', label='Male', conversation_id=conversation_id)
        male_option.full_clean()
        male_option.save()
        gender_form = SingleChoiceForm()
        return render(request, template_name, {'first_two_messages': first_two_messages, 'form': form, 'gender_form': gender_form, 'scenario': scenario})

def main_chat(request):
    # response_data = Chat()
    # api_response= response_data.get_response_data()
    # Get the phase of the conversation
    print("main chat")
    previous_phase = (APIResponse.objects.get()).phase
    print("previous PHASE")
    print(str(previous_phase))
    previous_question_type = (APIResponse.objects.get()).question_type
    print("previous question type")
    print(str(previous_question_type))
    previous_choice_type = (APIResponse.objects.get()).choice_type
    print("previous choice type")

    if request.method == 'POST':
        if previous_phase == 'user_name': 
            print("previous_phase -- user_name") 
            return send_on_boarding(request) 
        elif previous_phase == 'symptom_check': 
            print("previous_phase -- symptom_check") 
            return send_symptom_check(request) 
            # return send_answer(request)
        elif previous_phase == 'autocomplete_start':
            print("previous_phase -- autocomplete_start") 
            return send_autocomplete_start(request)
        elif previous_phase == 'autocomplete_add':
            print("previous_phase -- autocomplete_add") 
            return autocomplete(request)
        elif previous_phase == 'clarify': 
            print("previous_phase -- clarify") 
            return send_symptom_check(request) 
            # return send_answer(request)
        elif previous_phase == 'duration': 
            print("previous_phase -- duration") 
            return send_autocomplete_start(request)
            # return send_answer(request)
        elif previous_phase == 'health_background':
            print("previous_phase -- health_background") 
            return send_health_background(request)
            # return send_answer(request)
        elif previous_phase == 'questions': 
            print("previous_phase -- questions") 
            # return send_answer(request)
            if previous_question_type == 'symptoms':
                return send_symptoms_question(request)
            elif previous_question_type == 'symptom':
                return send_symptom_question(request)
            elif previous_question_type == 'factor':
                return send_symptom_question(request)
            else:
                print("Previous question type does not exist")
        elif previous_phase == 'pre_diagnosis':
            print("previous_phase -- pre_diagnosis") 
            return send_pre_diagnosis(request)
        elif previous_phase == 'dynamic-buttons':
            print("previous_phase -- dynamic_buttons") 
            # send_autocomplete_start(request)
            # return send_dynamic_buttons(request)
            return send_answer(request)
        elif previous_phase == 'report':
            print("previous_phase -- report") 
            return send_report(request)
        else:
            # If none of the conditions are met, return a default response
            return HttpResponseNotFound('Page not found')
        #    return page_not_found(request)

# def page_not_found(request):
#     render(request, 'page_not_found.html')

def send_on_boarding(request):
    response_data = Chat()
    if request.method == 'POST': 
      
        target_language_code = get_language_used()
        print(target_language_code)
        print("POST -- on_boarding")        

        form = OnBoardingForm(request.POST)
        gender_form = SingleChoiceForm(request.POST)
        if form.is_valid():
            name = request.POST.get('name')
            birth_year = request.POST.get('birth_year')
            if target_language_code == 'en':
                initial_symptoms = request.POST.get('initial_symptoms')
            else:
                initial_symptoms = translate_to_english(target_language_code, request.POST.get('initial_symptoms'))
          
            if gender_form.is_valid():
                gender = gender_form.cleaned_data['choices']

            initial_symptoms_splitted = initial_symptoms.split(", ")
            print("initial symptoms")
            print(initial_symptoms)

            on_boarding_answers = OnBoarding(name=name, birth_year=birth_year, initial_symptoms=initial_symptoms_splitted, gender=gender)
            on_boarding_answers.full_clean()
            on_boarding_answers.save()

        SingleChoice.objects.all().delete()
        APIResponse.objects.all().delete()

        response_data.set_on_boarding_answers_in_formatted_input(on_boarding_answers.name, on_boarding_answers.birth_year, on_boarding_answers.initial_symptoms, on_boarding_answers.gender)
        print(response_data.formatted_input)
        response = requests.post(response_data.url, json=response_data.formatted_input, headers=response_data.headers)
        print(response.json())
        api_response = response.json()

        phase = get_phase_from_api_response(api_response)
        question_type = get_question_type_from_api_response(api_response)
        step_back_possible = api_response.get('conversation', {}).get('step_back_possible' , [])
        # Check if mandatory and multiple fields are true
        mandatory = api_response.get('question', {}).get('mandatory' , [])
        multiple = api_response.get('question', {}).get('multiple' , [])
        choices = api_response.get('question', {}).get('choices' , [])
        if multiple:
            print("is multiple")
            choice_type = 'multiple'
            descriptor = find_mcq_type(choices)
            if descriptor == 'label':
                save_mcq_label(target_language_code, api_response)
            elif descriptor == 'text':
                save_mcq_text(target_language_code, api_response)
            elif descriptor == 'long_name':
                save_mcq_long_name(target_language_code, api_response)
            else:
                print('not found')
            form = MultipleChoiceForm()
        elif multiple == []:
            print("is multiple []")
            choice_type = 'multiple'
            descriptor = find_mcq_type(choices)
            if descriptor == 'label':
                save_mcq_label(target_language_code, api_response)
            elif descriptor == 'text':
                save_mcq_text(target_language_code, api_response)
            elif descriptor == 'long_name':
                save_mcq_long_name(target_language_code, api_response)
            else:
                print('not found')
            form = MultipleChoiceForm()
        else:
            print("is single")
            choice_type = 'single'
            descriptor = find_choices_type(choices)
            if descriptor == 'label':
                save_choices_label(target_language_code, api_response)
            elif descriptor == 'text':
                save_choices_text(target_language_code, api_response)
            else:
                print('not found')
            form = SingleChoiceForm()

        print(choice_type)
        save_APIResponse(phase, question_type, choice_type)
        print("phase")
        print(phase)
        template_name = get_template_for_phase(phase)

        # saves api response as messages
        messages = []
        messages.append(api_response.get('question', {}).get('messages' , []))

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


        translated_messages = []
    
        for message in text_content:
            print(message)
            print(translate(target_language_code, message))
            translated_messages.append(translate(target_language_code, message))
    
        print(translated_messages)
        conversation_id = api_response.get('conversation', {}).get('id' , None)
        print("conversation id")
        print(conversation_id)
        save_conversationID(conversation_id)

        return render(request, template_name, {'messages': translated_messages, 'form': form, 'step_back_possible':step_back_possible})

def send_symptom_check(request):
    response_data = Chat()
    SingleChoice.objects.all().delete()
    if request.method == 'POST': 
        target_language_code = get_language_used()
        print(target_language_code)
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


        response_data.set_symptom_confirmation_in_formatted_input(selected_symptoms_ids, conversation_id)
        response = requests.post(response_data.url, json=response_data.formatted_input, headers=response_data.headers)
        print(response_data.formatted_input)
        print(response.json())
        api_response = response.json()

        phase = get_phase_from_api_response(api_response)
        question_type = get_question_type_from_api_response(api_response)
        multiple = api_response.get('question', {}).get('multiple' , [])
        if multiple:
            choice_type = 'multiple'
        elif multiple == []:
            choice_type = 'multiple'
        else:
            choice_type = 'single'
        
        save_APIResponse(phase, question_type, choice_type)

        template_name = get_template_for_phase(phase)

        step_back_possible = api_response.get('conversation', {}).get('step_back_possible' , [])
        print(step_back_possible)
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

        translated_messages = []
    
        for message in text_content:
            print(message)
            print(translate(target_language_code, message))
            translated_messages.append(translate(target_language_code, message))
    
        print(translated_messages)
        save_mcq_label(target_language_code, api_response)

        save_choices_label(target_language_code, api_response)

        form = SingleChoiceForm()
        # return render(request, 'chat.html', {'messages': all_messages, 'form': form})
    else:
        form = MultipleChoiceForm()
    return render(request, 'chat.html', {'messages': translated_messages, 'form': form, 'step_back_possible':step_back_possible})

def send_autocomplete_start(request):
    response_data = Chat()
    if request.method == 'POST': 
        print("POST -- submit_choice")        
        APIResponse.objects.all().delete()
        target_language_code = get_language_used()
        print(target_language_code)
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

            response_data.set_symptom_confirmation_in_formatted_input(selected_choice_id, conversation_id)

            response = requests.post(response_data.url, json=response_data.formatted_input, headers=response_data.headers)
            print(response_data.formatted_input)
            print(response.json())
            api_response = response.json()

            phase = get_phase_from_api_response(api_response)
            question_type = get_question_type_from_api_response(api_response)
            multiple = api_response.get('question', {}).get('multiple' , [])
            if multiple:
                choice_type = 'multiple'
            else:
                choice_type = 'single'
            save_APIResponse(phase, question_type, choice_type)

            template_name = get_template_for_phase(phase)
          
        else:
            print("NO")
        step_back_possible = api_response.get('conversation', {}).get('step_back_possible' , [])
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
        elif message_type == 'duration':
            text_content = [msg['text'] for sublist in messages for msg in sublist if msg.get('type') == 'text' or msg.get('type') == 'small_text']
            print("text content")
            print(text_content)
        else :
            text_content = "No content"
            print("text content")
            print(text_content)

        translated_messages = []
    
        for message in text_content:
            print(message)
            print(translate(target_language_code, message))
            translated_messages.append(translate(target_language_code, message))
    
        phase_value = api_response['conversation']['phase']
        print("phase")
        print(phase_value)
        if (phase_value=='info_result'):
            form = SingleChoiceForm()
            # Accessing the articles
            articles = api_response['report']['articles']
            request.session['articles'] = json.dumps(articles)
            return render(request, 'end_of_chat.html', {'messages': translated_messages, 'form': form, 'step_back_possible':step_back_possible})
        elif (phase_value=='clarify'):
            MultipleChoice.objects.all().delete()
            save_mcq_label(target_language_code, api_response)
            form = MultipleChoiceForm()
            return render(request, 'chat.html', {'messages': translated_messages,'form': form, 'step_back_possible':step_back_possible})
        elif (phase_value=='symptom_check'):
            MultipleChoice.objects.all().delete()
            save_mcq_label(target_language_code, api_response)
            form = MultipleChoiceForm()
            return render(request, 'chat.html', {'messages': translated_messages,'form': form, 'step_back_possible':step_back_possible})
        elif (phase_value=='health_background'):
            MultipleChoice.objects.all().delete()
            save_mcq_long_name(target_language_code,api_response)
            form = MultipleChoiceForm()
            return render(request, 'chat.html', {'messages': translated_messages,'form': form, 'step_back_possible':step_back_possible})
        elif (phase_value=='duration'):
            SingleChoice.objects.all().delete()
            save_choices_label(target_language_code,api_response)
            form = SingleChoiceForm()
            return render(request, 'chat.html', {'messages': translated_messages,'form': form, 'step_back_possible':step_back_possible})  
        elif (phase_value=='autocomplete_add'):
            SingleChoice.objects.all().delete()
            save_choices_text(target_language_code, api_response)
            form1 = TextInputForm()
            form2 = SingleChoiceForm()
            symptoms_count = TextInput.objects.count()
            print("COUNT")
            print(symptoms_count)
            choices = SingleChoice.objects.all()
            return render(request, 'chat2.html', {'messages': translated_messages,'form1': form1, 'form2': form2, 'symptoms_count': symptoms_count, 'choices':choices})
       
        else:
            pass
    else:
        form = MultipleChoiceForm()
    return render(request, 'chat.html', {'form': form, 'step_back_possible':step_back_possible})


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
        target_language_code = get_language_used()
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
        target_language_code = get_language_used()
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

            MultipleChoice.objects.all().delete()

            response_data.set_autocomplete_post(selected_symptom_ids, conversation_id)
            print(response_data.formatted_input)
            response = requests.post(response_data.url, json=response_data.formatted_input, headers=response_data.headers)
            print(response_data.formatted_input)
            print(response.json())
            api_response = response.json()

            phase = get_phase_from_api_response(api_response)
            question_type = get_question_type_from_api_response(api_response)
            save_APIResponse(phase, question_type)

            template_name = get_template_for_phase(phase)

        else:
            print("NO")
        step_back_possible = api_response.get('conversation', {}).get('step_back_possible' , [])
        print(step_back_possible)
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

        translated_messages = []
    
        for message in text_content:
            print(message)
            print(translate(target_language_code, message))
            translated_messages.append(translate(target_language_code, message))

            form = MultipleChoiceForm()
        return render(request, 'chat.html', {'messages': translated_messages, 'form': form, 'step_back_possible':step_back_possible})
    else:
        form = MultipleChoiceForm()
    return render(request, 'chat.html', {'form': form})

def send_health_background(request):
    response_data = Chat()
    # MultipleChoice.objects.all().delete()
    if request.method == 'POST': 
        target_language_code = get_language_used()
        print(target_language_code)
        print("POST -- send_health_background")        
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

            MultipleChoice.objects.all().delete()

            response_data.set_condition_confirmation_in_formatted_input(selected_condition_ids, conversation_id)

            response = requests.post(response_data.url, json=response_data.formatted_input, headers=response_data.headers)
            print(response.json())
            api_response = response.json()

            phase = get_phase_from_api_response(api_response)
            print(phase)
            question_type = get_question_type_from_api_response(api_response)
            multiple = api_response.get('question', {}).get('multiple' , [])
            choices = api_response.get('question', {}).get('choices' , [])
            max_selection = api_response.get('question', {}).get('constraints' , {}).get('max_selections' , [])

            if max_selection == 1:
                print("max selection =1 ")
                print("is single")
                choice_type = 'single'
                descriptor = find_choices_type(choices)
                if descriptor == 'label':
                    save_choices_label(target_language_code, api_response)
                elif descriptor == 'text':
                    save_choices_text(target_language_code, api_response)
                else:
                    print('not found')
                form = SingleChoiceForm()
                print(choice_type)
                save_APIResponse(phase, question_type, choice_type)
            else:
                if multiple:
                    print("is multiple")
                    choice_type = 'multiple'
                    descriptor = find_mcq_type(choices)
                    if descriptor == 'label':
                        save_mcq_label(target_language_code, api_response)
                    elif descriptor == 'text':
                        save_mcq_text(target_language_code, api_response)
                    elif descriptor == 'long_name':
                        save_mcq_long_name(target_language_code, api_response)
                    else:
                        print('not found')
                    form = MultipleChoiceForm()
                    print(choice_type)
                    save_APIResponse(phase, question_type, choice_type)
                elif multiple == []:
                    print("is multiple []")
                    choice_type = 'multiple'
                    descriptor = find_mcq_type(choices)
                    if descriptor == 'label':
                        save_mcq_label(target_language_code, api_response)
                    elif descriptor == 'text':
                        save_mcq_text(target_language_code, api_response)
                    elif descriptor == 'long_name':
                        save_mcq_long_name(target_language_code, api_response)
                    else:
                        print('not found')
                    form = MultipleChoiceForm()
                    print(choice_type)
                    save_APIResponse(phase, question_type, choice_type)
                else:
                    print("is single")
                    choice_type = 'single'
                    descriptor = find_choices_type(choices)
                    if descriptor == 'label':
                        save_choices_label(target_language_code, api_response)
                    elif descriptor == 'text':
                        save_choices_text(target_language_code, api_response)
                    else:
                        print('not found')
                    form = SingleChoiceForm()
                    print(choice_type)
                    save_APIResponse(phase, question_type, choice_type)


            template_name = get_template_for_phase(phase)

        else:
            print("NO")

        step_back_possible = api_response.get('conversation', {}).get('step_back_possible' , [])
        print(step_back_possible)
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
        elif message_type == 'factor':
            text_content = [msg['text'] for sublist in messages for msg in sublist if msg.get('type') == 'text']
            print("text content")
            print(text_content)
        elif message_type == 'duration':
            text_content = [msg['text'] for sublist in messages for msg in sublist if msg.get('type') == 'text' or msg.get('type') == 'small_text']
            print("text content")
            print(text_content)
        else :
            text_content = "No content"
            print("text content")
            print(text_content)

        translated_messages = []
    
        for message in text_content:
            print(message)
            print(translate(target_language_code, message))
            translated_messages.append(translate(target_language_code, message))
    
        print(translated_messages)

        # save_mcq_text(target_language_code, api_response)
        # form = MultipleChoiceForm()
        return render(request, 'chat.html', {'messages': translated_messages, 'form': form, 'step_back_possible':step_back_possible})
    else:
        form = MultipleChoiceForm()
    return render(request, 'chat.html', {'form': form})
      
def send_symptoms_question(request):
    response_data = Chat()
    html = 'chat.html'
    if request.method == 'POST': 
        target_language_code = get_language_used()
        print(target_language_code)
        print("POST -- send_send_symptoms_question")        
        previous_phase = (APIResponse.objects.get()).phase
        print("previous PHASE")
        print(str(previous_phase))

        previous_question_type = (APIResponse.objects.get()).question_type
        print("previous question type")
        print(str(previous_question_type))

        previous_choice_type = (APIResponse.objects.get()).choice_type
        print("previous choice type")
        print(previous_choice_type)  
        conversation_id = (ConversationId.objects.first()).conversation_id
        if previous_choice_type == 'multiple':
            form = MultipleChoiceForm(request.POST)
            selected_symptoms_ids = []
            selected_symptoms_name = []
            if form.is_valid():
                print("multiple choice form is valid")
                selected_symptoms = form.cleaned_data['multiple_choices']
                # Handle the selected symptoms data
                for symptom in selected_symptoms:
            
                    print(f"Selected Symptom: {symptom}")
        
                    selected_symptoms_name.append(symptom.name)
                    # Retrieves the symptom's choice_ID from the MultipleChoice object and append it to the list
                    selected_symptoms_ids.append(symptom.choice_id)
                print(str(selected_symptoms_ids))
                print("selected_symptoms_name")
                print(str(selected_symptoms_name))

                MultipleChoice.objects.all().delete()
                SingleChoice.objects.all().delete()
    
                
                response_data.set_condition_confirmation_in_formatted_input(selected_symptoms_ids, conversation_id)
        else:
            form = SingleChoiceForm(request.POST)
            selected_choice_id = []
            selected_choice_label = []
            if form.is_valid():
                print("single choice form is valid")
                choice = form.cleaned_data['choices']
                # Handle the selected symptoms data

        
                # Do something with the selected symptom ID
                print(f"Selected choice: {choice}")

                selected_choice_label.append(choice.label)
                # Retrieves the choice ID from the choice object and append it to the list
                selected_choice_id.append(choice.choice_id)
                print(str(selected_choice_id))
                print("selected_choice_label")
                print(str(selected_choice_label))   
                response_data.set_condition_confirmation_in_formatted_input(selected_choice_id, conversation_id)
           
        response = requests.post(response_data.url, json=response_data.formatted_input, headers=response_data.headers)
        print(response.json())
        api_response = response.json()
        
        phase = get_phase_from_api_response(api_response)
        question_type = get_question_type_from_api_response(api_response)
        multiple = api_response.get('question', {}).get('multiple' , [])
        choices = api_response.get('question', {}).get('choices' , [])
        max_selection = api_response.get('question', {}).get('constraints' , {}).get('max_selections' , [])

        if max_selection == 1:
            print("max selection =1 ")
            print("is single")
            choice_type = 'single'
            descriptor = find_choices_type(choices)
            if descriptor == 'label':
                save_choices_label(target_language_code, api_response)
            elif descriptor == 'text':
                save_choices_text(target_language_code, api_response)
            else:
                print('not found')
            form = SingleChoiceForm()
            print(choice_type)
            save_APIResponse(phase, question_type, choice_type)
        else:
            if multiple:
                print("is multiple")
                choice_type = 'multiple'
                descriptor = find_mcq_type(choices)
                if descriptor == 'label':
                    save_mcq_label(target_language_code, api_response)
                elif descriptor == 'text':
                    save_mcq_text(target_language_code, api_response)
                elif descriptor == 'long_name':
                    save_mcq_long_name(target_language_code, api_response)
                else:
                    print('not found')
                form = MultipleChoiceForm()
                print(choice_type)
                save_APIResponse(phase, question_type, choice_type)
            elif multiple == []:
                print("is multiple []")
                choice_type = 'multiple'
                descriptor = find_mcq_type(choices)
                if descriptor == 'label':
                    save_mcq_label(target_language_code, api_response)
                elif descriptor == 'text':
                    save_mcq_text(target_language_code, api_response)
                elif descriptor == 'long_name':
                    save_mcq_long_name(target_language_code, api_response)
                else:
                    print('not found')
                form = MultipleChoiceForm()
                print(choice_type)
                save_APIResponse(phase, question_type, choice_type)
            else:
                print("is single")
                choice_type = 'single'
                descriptor = find_choices_type(choices)
                if descriptor == 'label':
                    save_choices_label(target_language_code, api_response)
                elif descriptor == 'text':
                    save_choices_text(target_language_code, api_response)
                else:
                    print('not found')
                form = SingleChoiceForm()
                print(choice_type)
                save_APIResponse(phase, question_type, choice_type)




        template_name = get_template_for_phase(phase)

        step_back_possible = api_response.get('conversation', {}).get('step_back_possible' , [])
        print(step_back_possible)

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
        elif message_type == 'factor':
            text_content = [msg['text'] for sublist in messages for msg in sublist if msg.get('type') == 'text']
            print("text content factor")
            print(text_content)
        else :
            text_content = "No content"

        translated_messages = []
    
        for message in text_content:
            print(message)
            print(translate(target_language_code, message))
            translated_messages.append(translate(target_language_code, message))
    
        print(translated_messages)
        # save_mcq_text(target_language_code, api_response)


        list_of_choices = []
        list_of_choices.append(api_response.get('question', {}).get('choices' , []))

        conversation_id = api_response.get('conversation', {}).get('id' , None)

        print("CHOICES")
        print(list_of_choices)
        # Check if 'max_selections' exists in the 'constraints' dictionary
        # if 'constraints' in api_response['question'] and 'max_selections' in api_response['question']['constraints']:
        #     max_selections = api_response['question']['constraints']['max_selections']
        #     print("Max Selections:", max_selections)
        # else:
        #     print("'max_selections' not found in constraints")
        # if 'constraints' in api_response['question'] and 'max_selections' in api_response['question']['constraints']:
        #     # max_selections_exist = true
        #     max_selections = api_response['question']['constraints']['max_selections']
        #     print("max_selections exist")

        #     if (max_selections == 1):
        #         form = SingleChoiceForm()
        #         print("Choose 1!!!")
        #         html = 'chat.html'
        #         save_choices_text(target_language_code, api_response)
        #     else:
        #         form = MultipleChoiceForm()
        #         print("Multiple choice!!!!")
        #         html = 'chat.html'
        #         save_mcq_text(target_language_code, api_response)
        # else:
        #     print("max_selections DOESNT exist")
        #     form = SingleChoiceForm()
        #     html = 'chat.html'
        #     for sublist in list_of_choices:
        #         for choice in sublist:
        #             # Extracts choice id and label
        #             choice_id = choice['id']
        #             if 'text' in choice:
        #                 # The choice uses 'text'
        #                 choice_label = translate(target_language_code, choice['text'])
 
        #             elif 'label' in choice:
        #                 # The choice uses 'label'
        #                 choice_label = translate(target_language_code, choice['label'])
        #             # selected = True
        #             choice_conversation_id = conversation_id
            
        #             # Create Symptom object and save to database
        #             chosen_option = SingleChoice(choice_id=choice_id, label=choice_label, conversation_id=choice_conversation_id)
        #             chosen_option.full_clean()
        #             chosen_option.save()
    
        return render(request, html, {'messages': translated_messages, 'form': form, 'step_back_possible':step_back_possible})
    else:
        form = MultipleChoiceForm()
    return render(request, html, {'form': form})

def send_symptom_question(request): 
    response_data = Chat()
    html = 'chat.html'
    if request.method == 'POST': 
        target_language_code = get_language_used()
        print(target_language_code)
        print("POST -- send_symptom_question")  
        previous_question_type = (APIResponse.objects.get()).question_type
        print("previous question type")
        print(previous_question_type)      
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

            MultipleChoice.objects.all().delete()
            SingleChoice.objects.all().delete()

        response_data.set_yes_no_response_in_formatted_input(previous_question_type, selected_choice_id, conversation_id)

        response = requests.post(response_data.url, json=response_data.formatted_input, headers=response_data.headers)
        print(response_data.formatted_input)
        print(response.json())
        api_response = response.json()

        phase = get_phase_from_api_response(api_response)
        question_type = get_question_type_from_api_response(api_response)
        multiple = api_response.get('question', {}).get('multiple' , [])
        choices = api_response.get('question', {}).get('choices' , [])
        max_selection = api_response.get('question', {}).get('constraints' , {}).get('max_selections' , [])

        if max_selection == 1:
            print("max selection =1 ")
            print("is single")
            choice_type = 'single'
            descriptor = find_choices_type(choices)
            if descriptor == 'label':
                save_choices_label(target_language_code, api_response)
            elif descriptor == 'text':
                save_choices_text(target_language_code, api_response)
            else:
                print('not found')
            form = SingleChoiceForm()
            print(choice_type)
            save_APIResponse(phase, question_type, choice_type)
        else:
            if multiple:
                print("is multiple")
                choice_type = 'multiple'
                descriptor = find_mcq_type(choices)
                if descriptor == 'label':
                    save_mcq_label(target_language_code, api_response)
                elif descriptor == 'text':
                    save_mcq_text(target_language_code, api_response)
                elif descriptor == 'long_name':
                    save_mcq_long_name(target_language_code, api_response)
                else:
                    print('not found')
                form = MultipleChoiceForm()
                print(choice_type)
                save_APIResponse(phase, question_type, choice_type)
            elif multiple == []:
                print("is multiple []")
                choice_type = 'multiple'
                descriptor = find_mcq_type(choices)
                if descriptor == 'label':
                    save_mcq_label(target_language_code, api_response)
                elif descriptor == 'text':
                    save_mcq_text(target_language_code, api_response)
                elif descriptor == 'long_name':
                    save_mcq_long_name(target_language_code, api_response)
                else:
                    print('not found')
                form = MultipleChoiceForm()
                print(choice_type)
                save_APIResponse(phase, question_type, choice_type)
            else:
                print("is single")
                choice_type = 'single'
                descriptor = find_choices_type(choices)
                if descriptor == 'label':
                    save_choices_label(target_language_code, api_response)
                elif descriptor == 'text':
                    save_choices_text(target_language_code, api_response)
                else:
                    print('not found')
                form = SingleChoiceForm()
                print(choice_type)
                save_APIResponse(phase, question_type, choice_type)



        template_name = get_template_for_phase(phase)
       
        step_back_possible = api_response.get('conversation', {}).get('step_back_possible' , [])
        print(step_back_possible)

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
        elif message_type == 'factor':
            text_content = [msg['text'] for sublist in messages for msg in sublist if msg.get('type') == 'text']
            print("text content factor")
            print(text_content)
        
        else :
            text_content = "No content"

        translated_messages = []
    
        for message in text_content:
            print(message)
            print(translate(target_language_code, message))
            translated_messages.append(translate(target_language_code, message))
    
        print(translated_messages)

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
                save_choices_text(target_language_code, api_response)
            else:
                form = MultipleChoiceForm()
                print("Multiple choice!!!!")
                html = 'chat.html'
                save_mcq_text(target_language_code, api_response)
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
        
        return render(request, html, {'messages': translated_messages, 'form': form, 'step_back_possible':step_back_possible})
    else:
        form = MultipleChoiceForm()
    return render(request, 'chat.html', {'form': form})



def send_pre_diagnosis(request):
    response_data = Chat()
    html = 'report_summary.html'
    if request.method == 'POST': 
        target_language_code = get_language_used()
        print(target_language_code)
        print("POST -- send_pre_diagnosis")        
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

            MultipleChoice.objects.all().delete()
            SingleChoice.objects.all().delete()
            
        response_data.set_final_response_in_formatted_input(selected_choice_id, conversation_id)

        response = requests.post(response_data.url, json=response_data.formatted_input, headers=response_data.headers)
        print(response.json())
        api_response = response.json()

        phase = get_phase_from_api_response(api_response)
        question_type = get_question_type_from_api_response(api_response)
        multiple = api_response.get('question', {}).get('multiple' , [])
        if multiple:
            choice_type = 'multiple'
        else:
            choice_type = 'single'
        save_APIResponse(phase, question_type, choice_type)


        template_name = get_template_for_phase(phase)

        step_back_possible = api_response.get('conversation', {}).get('step_back_possible' , [])
        print(step_back_possible)
        # saves api response as messages
        messages = []
        messages.append(api_response.get('question', {}).get('messages' , []))

        print("MESSAGES")
        print(messages)

        if target_language_code == 'en':
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
            duration = api_response['report']['summary']['duration']
            extracted_symptoms =api_response['report']['summary']['extracted_symptoms']
            additional_symptoms = api_response['report']['summary']['additional_symptoms']
            negative_symptoms = api_response['report']['summary']['negative_symptoms']
            unsure_symptoms = api_response['report']['summary']['unsure_symptoms']
            user_profile = api_response['report']['summary']['user_profile']
            # timestamp = datetime.now()
        else:
            # translated
            consultation_triage_json_string = json.dumps(api_response['report']['summary']['consultation_triage'])
            consultation_triage = json.loads(translate(target_language_code, consultation_triage_json_string))
                       
            possible_conditions_json_string = json.dumps(api_response['report']['summary']['articles_v3'])
            possible_conditions = json.loads(translate(target_language_code, possible_conditions_json_string))
                         
            metadata_json_string = json.dumps(api_response['report']['summary']['articles_v3'][0]['metadata'])
            metadata = json.loads(translate(target_language_code, metadata_json_string))
                               
            triage_worries_json_string = json.dumps(api_response['report']['summary']['articles_v3'][0]['content']['triage']['triage_worries'])
            triage_worries = json.loads(translate(target_language_code, triage_worries_json_string))   
            triage_worries_html = triage_worries.replace('\n', '<br>')
        
            influencing_factors_json_string = json.dumps(api_response['report']['summary']['influencing_factors'])
            influencing_factors = json.loads(translate(target_language_code, influencing_factors_json_string)) 

            duration_json_string = json.dumps(api_response['report']['summary']['duration'])
            duration = json.loads(translate(target_language_code, duration_json_string)) 

            extracted_symptoms_json_string = json.dumps(api_response['report']['summary']['extracted_symptoms'])
            extracted_symptoms = json.loads(translate(target_language_code, extracted_symptoms_json_string)) 

            additional_symptoms_json_string = json.dumps(api_response['report']['summary']['additional_symptoms'])
            additional_symptoms = json.loads(translate(target_language_code, additional_symptoms_json_string)) 
            
            negative_symptoms_json_string = json.dumps(api_response['report']['summary']['negative_symptoms'])
            negative_symptoms = json.loads(translate(target_language_code, negative_symptoms_json_string)) 
            
            unsure_symptoms_json_string = json.dumps(api_response['report']['summary']['unsure_symptoms'])
            unsure_symptoms = json.loads(translate(target_language_code, unsure_symptoms_json_string)) 

            user_profile_json_string = json.dumps(api_response['report']['summary']['user_profile'])
            user_profile = json.loads(translate(target_language_code, user_profile_json_string)) 
                        
        timestamp =  datetime.now()

        health_background_conditions_list = []
        condition_ids = list(HealthBackground.objects.values_list('condition_id', flat=True))
        print("condition_ids")
        print(condition_ids)
        for factor in influencing_factors:
            health_background_conditions = {}
            print("factor")
            print(factor)
            if factor['cui'] in condition_ids:
                health_background_conditions["name"] = translate(target_language_code,factor['long_name'])    
                health_background_conditions["patient_has_condition"] = translate(target_language_code,"Yes")
            else:
                health_background_conditions["name"] = translate(target_language_code,factor['long_name'])
                health_background_conditions["patient_has_condition"] = translate(target_language_code,"No")
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
        # save_digidoc_message(text_content)

        translated_messages = []
        # all_messages = Message.objects.all()
    
        for message in text_content:
            print(message)
            print(translate(target_language_code, message))
            translated_messages.append(translate(target_language_code, message))
    
        print(translated_messages)

        save_choices_label(target_language_code, api_response)
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
                'timestamp': timestamp,
                'step_back_possible': step_back_possible
        }
        return render(request, html, context)

def send_report(request):
    print("POST -- send_report")
    response_data = Chat()
    html = 'report.html'
    if request.method == 'POST': 
        target_language_code = get_language_used()
        print(target_language_code)       
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

            MultipleChoice.objects.all().delete()
            SingleChoice.objects.all().delete()
            
        response_data.set_final_response_in_formatted_input(selected_choice_id, conversation_id)

        response = requests.post(response_data.url, json=response_data.formatted_input, headers=response_data.headers)
        print(response.json())
        api_response = response.json()

        phase = get_phase_from_api_response(api_response)
        question_type = get_question_type_from_api_response(api_response)
        multiple = api_response.get('question', {}).get('multiple' , [])
        if multiple:
            choice_type = 'multiple'
        else:
            choice_type = 'single'
        save_APIResponse(phase, question_type, choice_type)


        template_name = get_template_for_phase(phase)


        step_back_possible = api_response.get('conversation', {}).get('step_back_possible' , [])
        print(step_back_possible)

        # saves api response as messages
        messages = []
        messages.append(api_response.get('question', {}).get('messages' , []))

        print("MESSAGES")
        print(messages)
        text_content = [msg['value'] for sublist in messages for msg in sublist if msg.get('type') == 'generic']

        save_choices_label(target_language_code, api_response)
    return render(request, html, {'text_content':text_content, 'form':form, 'step_back_possible':step_back_possible})

def see_articles(request):
    articles = json.loads(request.session['articles'])
    print("articles")
    print(articles)
    # Render report.html with articles data
    return render(request, 'articles.html', {'articles': articles})

def thank_you(request):
    return render(request, 'thank_you.html')

def find_mcq_type(choices):
    for choice in choices:
        if 'label' in choice:
            print('this is a label')
            return 'label'
        elif 'text' in choice:
            print('this is a text')
            return 'text'
        elif 'long_name' in choice:
            print('this is a long name')
            return 'long_name'
        else:
            return 'Not found'

def find_choices_type(choices):
    for choice in choices:
        if 'label' in choice:
            return 'label'
        elif 'text' in choice:
            return 'text'
        else:
            return 'Not found'

def send_answer(request):
    response_data = Chat()
    if request.method == 'POST': 
        target_language_code = get_language_used()
        print(target_language_code)
        print("POST -- send_answer")  
        previous_phase = (APIResponse.objects.get()).phase
        print("previous PHASE")
        print(str(previous_phase))

        previous_question_type = (APIResponse.objects.get()).question_type
        print("previous question type")
        print(str(previous_question_type))

        previous_choice_type = (APIResponse.objects.get()).choice_type
        print("previous choice type")
        print(previous_choice_type)
        conversation_id = (ConversationId.objects.first()).conversation_id

        if previous_choice_type == 'multiple':
            form = MultipleChoiceForm(request.POST)
            selected_choices_ids = []
            selected_choices_name = []
            if form.is_valid():
                selected_choices = form.cleaned_data['multiple_choices']
                # Handle the selected symptoms data
                for choice in selected_choices:
            
                    print(f"Selected Symptom: {choice}")
        
                    selected_choices_name.append(choice.name)
                    # Retrieves the symptom's choice_ID from the MultipleChoice object and append it to the list
                    selected_choices_ids.append(choice.choice_id)
                print(str(selected_choices_ids))
                print("selected_symptoms_name")
                print(str(selected_choices_name))

            if previous_phase == 'symptom_check':
                response_data.set_symptom_confirmation_in_formatted_input(selected_choices_ids, conversation_id)
                response = requests.post(response_data.url, json=response_data.formatted_input, headers=response_data.headers)
                print(response_data.formatted_input) #prints users answer response
                print(response.json())
                    # pass
            elif previous_phase == 'clarify':
                response_data.set_symptom_confirmation_in_formatted_input(selected_choices_ids, conversation_id)
                response = requests.post(response_data.url, json=response_data.formatted_input, headers=response_data.headers)
                print(response_data.formatted_input) #prints users answer response
                print(response.json())
            elif previous_phase == 'health_background':
                health_background = HealthBackground(condition_id = choice.choice_id)
                health_background.full_clean()
                health_background.save()
                response_data.set_condition_confirmation_in_formatted_input(selected_choices_ids, conversation_id)
                response = requests.post(response_data.url, json=response_data.formatted_input, headers=response_data.headers)
                print(response_data.formatted_input) #prints users answer response
                print(response.json())
            elif previous_phase == 'questions':
                if previous_question_type == 'symptoms':
                    response_data.set_condition_confirmation_in_formatted_input(selected_choices_ids, conversation_id)
                    response = requests.post(response_data.url, json=response_data.formatted_input, headers=response_data.headers)
                    print(response_data.formatted_input) #prints users answer response
                    print(response.json())
                else:
                    print('no question type')
            else:
                print('none')


        elif previous_choice_type == 'single':
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
                print("selected_choice_label")
                print(str(selected_choice_label))

                if previous_phase == 'autocomplete_start':
                    response_data.set_symptom_confirmation_in_formatted_input(selected_choice_id, conversation_id)
                elif previous_phase =='dynamic-buttons':
                    response_data.set_symptom_confirmation_in_formatted_input(selected_choice_id, conversation_id)
                elif previous_phase =='questions':
                    if previous_question_type == 'symptom':
                        response_data.set_yes_no_response_in_formatted_input(selected_choice_id, conversation_id)
                    else:
                        print("should be multiple")
                elif previous_phase == 'duration':
                    print("///duration")
                    response_data.set_symptom_confirmation_in_formatted_input(selected_choice_id, conversation_id)
    
        else:
            print('different choice type')

    
        response = requests.post(response_data.url, json=response_data.formatted_input, headers=response_data.headers)
        print(response_data.formatted_input) #prints users answer response
        print(response.json())
        api_response = response.json()

        phase = get_phase_from_api_response(api_response)
        question_type = get_question_type_from_api_response(api_response)
        step_back_possible = api_response.get('conversation', {}).get('step_back_possible' , [])
        # Check if mandatory and multiple fields are true
        mandatory = api_response.get('question', {}).get('mandatory' , [])
        multiple = api_response.get('question', {}).get('multiple' , [])
        choices = api_response.get('question', {}).get('choices' , [])
        max_selection = api_response.get('question', {}).get('constraints' , {}).get('max_selections' , [])

        if max_selection == 1:
            print("max selection =1 ")
            print("is single")
            choice_type = 'single'
            descriptor = find_choices_type(choices)
            if descriptor == 'label':
                save_choices_label(target_language_code, api_response)
            elif descriptor == 'text':
                save_choices_text(target_language_code, api_response)
            else:
                print('not found')
            form = SingleChoiceForm()
            print(choice_type)
            save_APIResponse(phase, question_type, choice_type)
        else:
            if multiple:
                print("is multiple")
                choice_type = 'multiple'
                descriptor = find_mcq_type(choices)
                if descriptor == 'label':
                    save_mcq_label(target_language_code, api_response)
                elif descriptor == 'text':
                    save_mcq_text(target_language_code, api_response)
                elif descriptor == 'long_name':
                    save_mcq_long_name(target_language_code, api_response)
                else:
                    print('not found')
                form = MultipleChoiceForm()
                print(choice_type)
                save_APIResponse(phase, question_type, choice_type)
            elif multiple == []:
                print("is multiple []")
                choice_type = 'multiple'
                descriptor = find_mcq_type(choices)
                if descriptor == 'label':
                    save_mcq_label(target_language_code, api_response)
                elif descriptor == 'text':
                    save_mcq_text(target_language_code, api_response)
                elif descriptor == 'long_name':
                    save_mcq_long_name(target_language_code, api_response)
                else:
                    print('not found')
                form = MultipleChoiceForm()
                print(choice_type)
                save_APIResponse(phase, question_type, choice_type)
            else:
                print("is single")
                choice_type = 'single'
                descriptor = find_choices_type(choices)
                if descriptor == 'label':
                    save_choices_label(target_language_code, api_response)
                elif descriptor == 'text':
                    save_choices_text(target_language_code, api_response)
                else:
                    print('not found')
                form = SingleChoiceForm()
                print(choice_type)
                save_APIResponse(phase, question_type, choice_type)


        print("phase")
        print(phase)
        template_name = get_template_for_phase(phase)

        step_back_possible = api_response.get('conversation', {}).get('step_back_possible' , [])
        print(step_back_possible)
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
            print("can you pls work :'(")
            text_content = [msg['text'] for sublist in messages for msg in sublist if msg.get('type') == 'text']
            print("text content")
            print(text_content)
        elif message_type == 'autocomplete':
            text_content = [msg['text'] for sublist in messages for msg in sublist if msg.get('type') == 'text' or msg.get('type') == 'small_text']
            print("text content")
            print(text_content)
        elif message_type == 'duration':
            text_content = [msg['text'] for sublist in messages for msg in sublist if msg.get('type') == 'text' or msg.get('type') == 'small_text']
            print("text content")
            print(text_content)
        elif message_type == 'symptoms':
            text_content = [msg['text'] for sublist in messages for msg in sublist if msg.get('type') == 'text']
            print("text content")
            print(text_content)
        elif message_type == 'symptom':
            text_content = [msg['text'] for sublist in messages for msg in sublist if msg.get('type') == 'text']
            print("text content symptom")
            print(text_content)
        elif message_type == 'factor':
            text_content = [msg['text'] for sublist in messages for msg in sublist if msg.get('type') == 'text']
            print("text content")
            print(text_content)
        else :
            text_content = "No content"
            print("text content")
            print(text_content)

        translated_messages = []
    
        for message in text_content:
            print(message)
            print(translate(target_language_code, message))
            translated_messages.append(translate(target_language_code, message))
    
        print(translated_messages)

        if (phase=='info_result'):
            form = SingleChoiceForm()
            # Accessing the articles
            articles = api_response['report']['articles']
            request.session['articles'] = json.dumps(articles)
            return render(request, 'chat.html', {'messages': translated_messages,'step_back_possible':step_back_possible, 'see_articles': True})
        elif (phase=='clarify'):
            MultipleChoice.objects.all().delete()
            save_mcq_label(target_language_code, api_response)
            form = MultipleChoiceForm()
            return render(request, 'chat.html', {'messages': translated_messages,'form': form, 'step_back_possible':step_back_possible})
        elif (phase=='health_background'):
            MultipleChoice.objects.all().delete()
            save_mcq_long_name(target_language_code,api_response)
            form = MultipleChoiceForm()
            return render(request, 'chat.html', {'messages': translated_messages,'form': form, 'step_back_possible':step_back_possible})
        elif (phase=='duration'):
            SingleChoice.objects.all().delete()
            save_choices_label(target_language_code,api_response)
            form = SingleChoiceForm()
            return render(request, 'chat.html', {'messages': translated_messages,'form': form, 'step_back_possible':step_back_possible})  
        elif (phase=='autocomplete_add'):
            SingleChoice.objects.all().delete()
            save_choices_text(target_language_code, api_response)
            form1 = TextInputForm()
            form2 = SingleChoiceForm()
            symptoms_count = TextInput.objects.count()
            print("COUNT")
            print(symptoms_count)
            choices = SingleChoice.objects.all()
            return render(request, 'chat2.html', {'messages': translated_messages,'form1': form1, 'form2': form2, 'symptoms_count': symptoms_count, 'choices':choices})
       
        else:
            pass
    else:
        form = MultipleChoiceForm()
    return render(request, 'chat.html', {'messages': translated_messages, 'form': form, 'step_back_possible':step_back_possible})

# def send_dynamic_buttons(request):
#     print("DYNAMIC BUTTON VIEW")
#     render(request, 'chat.html')