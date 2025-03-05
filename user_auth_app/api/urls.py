from django.urls import path
from .views import RegistrationView, CustomLoginView
from . import views


urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', CustomLoginView.as_view(), name='login'),
    # path('guest-login/', GuestLoginView.as_view(), name='guest-login'),

    path('profile/<int:pk>/', views.ProfileDetailView.as_view(), name='profile-detail'),
    path('profiles/business/', views.BusinessProfileListView.as_view(), name='business-profile-list'),
    path('profiles/customer/', views.CustomerProfileListView.as_view(), name='customer-profile-list'),
]

