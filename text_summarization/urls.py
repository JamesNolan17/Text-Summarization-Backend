from django.urls import path
from django.urls import include, re_path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from .views import TextInstanceGetView, TextGetOneView, TextDeleteOneView, TextUpdateView, TextUploadView, InputView
urlpatterns = [
    path('get', TextInstanceGetView.as_view(), name = 'Get all text'),
    path('get/<int:text_id>', TextGetOneView.as_view(), name = 'Get one text'),
    path('delete/<int:text_id>',TextDeleteOneView.as_view(),name = 'Delete one text'),
    path('update/<int:text_id>',TextUpdateView.as_view(),name = 'Update one text'),
    path('upload',TextUploadView.as_view(),name = 'Upload one text'),
    path('input', InputView.as_view(),name = 'Input raw text')
    
]
