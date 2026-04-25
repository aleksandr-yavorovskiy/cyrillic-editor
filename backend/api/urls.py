from django.urls import path
from api import views

urlpatterns = [
    path("ping/", views.ping),
    path("compile/", views.compile_handler),
    path("import/", views.import_handler),
    path("export-docx/", views.export_handler),
]
