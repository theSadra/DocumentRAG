
from django.db import models


class Assistant(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    openai_assistant_id = models.CharField(max_length=255, blank=True, null=True)
    user_id = models.IntegerField(null=True, blank=True)  # Admin user id
    organization_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Assistant {self.id} ({self.name or 'Unnamed'}) (OpenAI: {self.openai_assistant_id})"



class VectorStore(models.Model):
    openai_vectorstore_id = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    files = models.ManyToManyField('File', related_name='vectorstores', blank=True)
    user_id = models.IntegerField(null=True, blank=True)  # Admin user id
    assistant = models.ForeignKey(Assistant, related_name='vectorstores', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"VectorStore {self.id} ({self.name or 'Unnamed'}) (OpenAI: {self.openai_vectorstore_id})"




class File(models.Model):
    openai_file_id = models.CharField(max_length=255)
    assistant = models.ForeignKey(Assistant, related_name='files', on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File {self.id} (OpenAI: {self.openai_file_id}) (Assistant: {self.assistant_id})"


class Thread(models.Model):
    assistant = models.ForeignKey(Assistant, related_name='threads', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    openai_thread_id = models.CharField(max_length=255)
    user_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Thread {self.id} (Assistant: {self.assistant_id}) (OpenAI: {self.openai_thread_id}) (Active: {self.is_active}) (Created: {self.created_at})"


