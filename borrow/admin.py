from django.contrib import admin
from .models import Borrowing, VerifiedBorrowing, BorrowHistory
from books.models import BookCopy
class BorrowingAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ('user', 'borrow_date', 'expire_date', 'get_books')
    search_fields = ['user__username']
    list_filter = ('user', )
    exclude = ('is_returned',)

    #Ne legyen QuerySet szerinti torles, a borrowinglist-et tulhalmozza.
    actions = None

    def get_books(self, obj):
        return ", ".join([book_copy.book.title for book_copy in obj.book_copies.all()])

    get_books.short_description = "Kikölcsönzött Könyvek"

    #https://docs.djangoproject.com/en/3.0/topics/class-based-views/generic-display/#generic-views-of-objects
    # borrowing-ok ne latszodjanak a verifiedborrowingban...
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(is_verified=False)  

admin.site.register(Borrowing, BorrowingAdmin)

@admin.register(VerifiedBorrowing)
class VerifiedBorrowingAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ('user', 'borrow_date', 'due_date', 'get_books', 'get_status')
    search_fields = ['user__username']
    list_filter = ('borrow_date', 'due_date',)
    exclude = ('return_date',)

    actions = None
    
    def get_books(self, obj):
        return ", ".join([book_copy.book.title for book_copy in obj.borrowing.book_copies.all()]) if obj.borrowing else ""
    get_books.short_description = "Kikölcsönzött Könyvek"

    def get_status(self, obj):
        return obj.borrowing.book_copies.first().get_status_display()
    get_status.short_description = "Kölcsönzés állapota"

@admin.register(BorrowHistory)
class BorrowHistory(admin.ModelAdmin):
    list_per_page = 20
    list_display = ('user', 'return_date', 'book_count')
    search_fields = ['user__username']
    list_filter = ('user', 'return_date')
    
