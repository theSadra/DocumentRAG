# Django Project: docrag

This Django project manages Assistants, Files, and Threads for document-based workflows.

## Database Models
- **Assistant**: Has an ID, a creation timestamp, and a list of related files and threads.
- **File**: Has an ID, OpenAI file ID, and a foreign key to Assistant.
- **Thread**: Has an ID, foreign key to Assistant, creation timestamp, active status, and OpenAI thread ID.

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run migrations:
   ```bash
   python manage.py migrate
   ```
3. Create a superuser (for admin):
   ```bash
   python manage.py createsuperuser
   ```
4. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Admin
All models are registered in the Django admin for easy management.

## Project Structure
- `core/models.py`: Database models
- `core/admin.py`: Admin registration
- `docrag/settings.py`: Project settings

---
For more, see Django documentation: https://docs.djangoproject.com/
