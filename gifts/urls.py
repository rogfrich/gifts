from django.urls import path
from django.contrib.auth import views as auth_views

from .views import home
from .views import my_wishes
from .views import other_wishes
from .views import my_claims




urlpatterns = [
    path('', home, name='home'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('wishes/', other_wishes, name='other_wishes'),
    path('my-wishes/', my_wishes, name='my_wishes'),
    path('my-claims/', my_claims, name='my_claims'),
]