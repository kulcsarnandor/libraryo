from django.shortcuts import render, get_object_or_404
from .models import Book  
from review.models import Review
from django.db.models import Avg
from pages.views import group_books

from django.db.models import Prefetch
import random


def book_detail_view(request, book_id):
    book = get_object_or_404(Book, id=book_id) 
    reviews = Review.objects.filter(book=book).order_by('-updated_at')

    user_review_submitted = None
    if request.user.is_authenticated:
        user_review_submitted = Review.objects.filter(user=request.user, book=book).first()

    average_rating = reviews.aggregate(avg_rating=Avg('rating') )['avg_rating'] or 0
    
    similar_books = Book.objects.filter(category__in=book.category.all() 
                                        ).exclude(id=book.id).distinct().select_related('author').prefetch_related('category')
    
    similar_books = list(similar_books)
    random.shuffle(similar_books)

    similar_books_unique_dict = {}
    for similar_book in similar_books:
        similar_books_unique_dict[similar_book.id] = similar_book

    unique_similar_books = list(similar_books_unique_dict.values())

    books_in_similar_books = unique_similar_books[:16]
    similar_books_group = group_books(books_in_similar_books, 4)
    
    context = {
        'book': book,
        'reviews': reviews,
        'average_rating': average_rating,
        'user_review_submitted': user_review_submitted,
        'similar_books_group': similar_books_group,
    }

    return render(request, 'books/book_detail.html', context)  
