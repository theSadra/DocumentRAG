from rest_framework import serializers
from .models import Assistant, File, Thread, VectorStore

class AssistantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assistant
        fields = '__all__'

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'

class ThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thread
        fields = '__all__'


class VectorStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = VectorStore
        fields = '__all__'