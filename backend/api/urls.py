from django.urls import path
from .views import compile_handler, ping, import_file, export_docx

urlpatterns = [
    path('compile/', compile_handler),
    path('ping/', ping),
    path('import/', import_file),
    path('export-docx/', export_docx),
]