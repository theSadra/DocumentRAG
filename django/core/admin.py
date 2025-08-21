
from django.contrib import admin
from .models import Assistant, File, Thread, VectorStore


@admin.register(Assistant)
class AssistantAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'openai_assistant_id', 'created_at')
    search_fields = ('id', 'name', 'openai_assistant_id')


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('id', 'openai_file_id', 'assistant')
    search_fields = ('id', 'openai_file_id')
    list_filter = ('assistant',)


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'assistant', 'created_at', 'is_active', 'openai_thread_id')
    search_fields = ('id', 'openai_thread_id')
    list_filter = ('assistant', 'is_active')

@admin.register(VectorStore)
class VectorStoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'openai_vectorstore_id', 'assistant', 'user_id')
    search_fields = ('id', 'name', 'openai_vectorstore_id')
    list_filter = ('assistant',)
