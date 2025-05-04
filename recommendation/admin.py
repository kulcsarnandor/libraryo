from django.contrib import admin
from .models import Wishlist
from django.contrib.auth.models import User

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
  list_per_page = 20
  list_display = ('user', 'book')
  search_fields = ['user__username']
  list_filter = ('user', )

