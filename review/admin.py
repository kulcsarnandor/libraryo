from django.contrib import admin
from .models import Review
from books.models import Book

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
  list_per_page = 20
  list_display = ['user', 'book', 'created_at']
  search_fields = ['user__username', 'book__title']
  list_filter = ('user', 'book', 'created_at', 'updated_at')

  


# Register your models here.
