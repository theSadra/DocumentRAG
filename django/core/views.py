from django.shortcuts import render
from rest_framework import viewsets
from .models import Assistant, File, Thread, VectorStore
from .serializers import AssistantSerializer, FileSerializer, ThreadSerializer, VectorStoreSerializer

class AssistantViewSet(viewsets.ModelViewSet):
    queryset = Assistant.objects.all()
    serializer_class = AssistantSerializer

class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer


class ThreadViewSet(viewsets.ModelViewSet):
    queryset = Thread.objects.all()
    serializer_class = ThreadSerializer

class VectorStoreViewSet(viewsets.ModelViewSet):
    queryset = VectorStore.objects.all()
    serializer_class = VectorStoreSerializer
