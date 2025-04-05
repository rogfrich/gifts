from django.urls import path


from .views import home
from .views import my_wishes
from .views import other_wishes
from .views import my_claims
from .views import create_wish
from .views import edit_wish
from .views import delete_wish




urlpatterns = [
    path('', home, name='home'),

    path('wishes/', other_wishes, name='other_wishes'),
    path('my-wishes/', my_wishes, name='my_wishes'),
    path('my-claims/', my_claims, name='my_claims'),
    path('create-wish/', create_wish, name='create_wish'),
    path('edit-wish/<int:wish_id>/', edit_wish, name='edit_wish'), 
    path('delete-wish/<int:wish_id>/', delete_wish, name='delete_wish'),
]

