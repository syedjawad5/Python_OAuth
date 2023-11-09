from django.contrib import admin
from django.urls import path
from .views import hello_endpoint , oauth_logout

urlpatterns = [
    path('hello/', hello_endpoint),
    path('logout/', oauth_logout)  
    
]