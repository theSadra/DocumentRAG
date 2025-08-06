from django.shortcuts import render
from rest_framework import viewsets
from .models import Assistant, File, Thread
from .serializers import AssistantSerializer, FileSerializer, ThreadSerializer

class AssistantViewSet(viewsets.ModelViewSet):
    queryset = Assistant.objects.all()
    serializer_class = AssistantSerializer

class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer

class ThreadViewSet(viewsets.ModelViewSet):
    queryset = Thread.objects.all()
    serializer_class = ThreadSerializer
