from django.contrib import admin
from .models import Wish  # Updated import to Wish

admin.site.register(Wish)  # Ensure Wish is registered in the admin
