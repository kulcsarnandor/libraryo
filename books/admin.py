from django.contrib import admin
from .models import Book, Author, Category, BookCopy
from django.core.exceptions import ValidationError
from django import forms
from django.utils.html import format_html


class BookAdminForm(forms.ModelForm):
     
    class Meta:
        model = Book
        fields = '__all__'
        
#egy konyvhoz max 5 mufaj tartozhat.
    def clean_category(self):
        categories = self.cleaned_data['category']
        if categories.count() > 5:
            raise ValidationError("Maximum 5 műfaj választható!")
        return categories

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_per_page = 20
    form = BookAdminForm
    list_display = ('title', 'total_copies_display', 'author', 'isbn', 'id')
    search_fields = ['title', 'author__v_nev','author__k_nev', 'isbn']
    list_filter = ('author',)
    autocomplete_fields = ['author', 'category']

    readonly_fields = ('cover_image_preview',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('author').prefetch_related('category', 'book_copies')

    # 🎯 Pretty preview of uploaded cover
    def cover_image_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" style="max-height: 300px; max-width: 200px; border: 1px solid #ccc;" />', obj.cover_image.url)
        return "Nincs borítókép."
    cover_image_preview.short_description = "Borítókép előnézet"

    def total_copies_display(self, obj):
        return len(obj.book_copies.all())

    total_copies_display.short_description = "Példányok száma"

@admin.register(BookCopy)
class BookCopyAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ('book', 'borrower', 'status', 'id')
    search_fields = ['book__title', 'borrower__username']
    list_filter = ('status',)
    autocomplete_fields = ['book']
    exclude = ('is_available',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_per_page = 20
    search_fields = ['category_name']

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_per_page = 20
    search_fields = ['v_nev', 'k_nev']

# Register your models here.
