from .models import Assistant, File, Thread
from django.core.exceptions import ObjectDoesNotExist

def add_assistant():
    assistant = Assistant.objects.create()
    return assistant

def delete_assistant(assistant_id):
    try:
        assistant = Assistant.objects.get(id=assistant_id)
        assistant.delete()
        return True
    except Assistant.DoesNotExist:
        return False

def upload_file(openai_id, assistant_id):
    try:
        assistant = Assistant.objects.get(id=assistant_id)
        file = File.objects.create(openai_id=openai_id, assistant=assistant)
        return file
    except Assistant.DoesNotExist:
        return None

def delete_file(file_id):
    try:
        file = File.objects.get(id=file_id)
        file.delete()
        return True
    except File.DoesNotExist:
        return False

def create_thread(assistant_id, openai_thread_id, is_active=True):
    try:
        assistant = Assistant.objects.get(id=assistant_id)
        thread = Thread.objects.create(assistant=assistant, openai_thread_id=openai_thread_id, is_active=is_active)
        return thread
    except Assistant.DoesNotExist:
        return None

def send_prompt(thread_id, prompt):
    # Placeholder for actual OpenAI API call logic
    try:
        thread = Thread.objects.get(id=thread_id)
        # Here you would call OpenAI API and return the response
        # For now, just return a dummy response
        return {
            'thread_id': thread_id,
            'prompt': prompt,
            'response': 'This is a dummy response from OpenAI.'
        }
    except Thread.DoesNotExist:
        return None
