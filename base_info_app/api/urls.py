from django.urls import path
from . import views

urlpatterns = [
    path('', views.BaseInfoView.as_view(), name='base-info'),
]
