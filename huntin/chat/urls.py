from django.urls import path
from .import views


urlpatterns = [
    path('messages/<int:pk>/<int:company_id>/',views.ChatMessageApiView.as_view(),name='messages'),
    path('chatviewall/<int:pk>/',views.Chatviewall.as_view(),name='chatview')
]