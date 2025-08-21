from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from . import services

class AddAssistantView(APIView):
    def post(self, request):
        data = request.data
        assistant = services.add_assistant(
            name=data.get('name'),
            user_id=data.get('user_id'),
            organization_id=data.get('organization_id'),
            instructions=data.get('instructions'),
            model=data.get('model', 'gpt-4o')
        )
        return Response({'id': assistant.id, 'openai_assistant_id': assistant.openai_assistant_id}, status=status.HTTP_201_CREATED)

class DeleteAssistantView(APIView):
    def delete(self, request, pk):
        result = services.delete_assistant(pk)
        if result:
            return Response({'deleted': True})
        return Response({'deleted': False}, status=status.HTTP_404_NOT_FOUND)

class UploadFileView(APIView):
    def post(self, request):
        file = request.FILES['file']
        assistant_id = request.data.get('assistant_id')
        file_obj = services.upload_file(file, assistant_id)
        if file_obj:
            return Response({'id': file_obj.id, 'openai_file_id': file_obj.openai_file_id}, status=status.HTTP_201_CREATED)
        return Response({'error': 'Assistant not found'}, status=status.HTTP_404_NOT_FOUND)

class DeleteFileView(APIView):
    def delete(self, request, pk):
        result = services.delete_file(pk)
        if result:
            return Response({'deleted': True})
        return Response({'deleted': False}, status=status.HTTP_404_NOT_FOUND)

class AddVectorStoreView(APIView):
    def post(self, request):
        data = request.data
        vs = services.add_vectorstore(
            name=data.get('name'),
            file_ids=data.get('file_ids', []),
            user_id=data.get('user_id'),
            assistant_id=data.get('assistant_id')
        )
        return Response({'id': vs.id, 'openai_vectorstore_id': vs.openai_vectorstore_id}, status=status.HTTP_201_CREATED)

class DeleteVectorStoreView(APIView):
    def delete(self, request, pk):
        result = services.delete_vectorstore(pk)
        if result:
            return Response({'deleted': True})
        return Response({'deleted': False}, status=status.HTTP_404_NOT_FOUND)

class CreateThreadView(APIView):
    def post(self, request):
        data = request.data
        thread = services.create_thread(
            assistant_id=data.get('assistant_id'),
            openai_thread_id=data.get('openai_thread_id'),
            is_active=data.get('is_active', True)
        )
        if thread:
            return Response({'id': thread.id, 'openai_thread_id': thread.openai_thread_id}, status=status.HTTP_201_CREATED)
        return Response({'error': 'Assistant not found'}, status=status.HTTP_404_NOT_FOUND)

class SendPromptView(APIView):
    def post(self, request):
        data = request.data
        result = services.send_prompt(
            thread_id=data.get('thread_id'),
            prompt=data.get('prompt'),
            assistant_id=data.get('assistant_id')
        )
        if result:
            return Response(result)
        return Response({'error': 'Thread not found'}, status=status.HTTP_404_NOT_FOUND)
