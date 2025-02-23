# code_scribe_app/urls.py
from django.urls import path
from .views import markdown_view, home

urlpatterns = [
    path('', home, name="home"),
    path('markdown/<int:article_id>/', markdown_view, name='markdown_view'),
]
