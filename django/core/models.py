
from django.db import models

class Assistant(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    openai_assistant_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Assistant {self.id} ({self.name or 'Unnamed'}) (OpenAI: {self.openai_assistant_id})"

class File(models.Model):
    openai_file_id = models.CharField(max_length=255)
    assistant = models.ForeignKey(Assistant, related_name='files', on_delete=models.CASCADE)

    def __str__(self):
        return f"File {self.id} (OpenAI: {self.openai_file_id}) (Assistant: {self.assistant_id})"

class Thread(models.Model):
    assistant = models.ForeignKey(Assistant, related_name='threads', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    openai_thread_id = models.CharField(max_length=255)

    def __str__(self):
        return f"Thread {self.id} (Assistant: {self.assistant_id}) (OpenAI: {self.openai_thread_id}) (Active: {self.is_active}) (Created: {self.created_at})"
