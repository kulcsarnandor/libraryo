from django.shortcuts import render, redirect, get_object_or_404
from books.models import Book, Category, Author
from borrow.models import BorrowHistory, Borrowing, VerifiedBorrowing
from review.models import Review
from django.utils import timezone
from itertools import zip_longest
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count, Q, Func

from recommendation.views import get_recommendation_for_user

from django.views.decorators.cache import cache_page

import random

#felosztja a konyveket csoportokba.
def group_books(book_items, size):
    args = size*[iter(book_items)]
    return list(zip_longest(*args))

def home_page_view(request):
    books = list(Book.objects.select_related('author').prefetch_related('category').all())
    #categories = Category.objects.all()

    #Osszes konyv
    all_books = random.sample(books, min(16, len(books)))
    all_books_group = group_books(all_books, 4)

    #legujabb konyvek az adatbazisban.
    recent_books = list(Book.objects.select_related('author').prefetch_related('category').order_by('-created_at')[:16]) 
    recent_books_group = group_books(recent_books, 4)

    recommended_book_group = [] #Szemelyre szabott ajanlasok
    excluded_category_carousel = [] #top category-ban nem szereplo category-k.
    recommended_category_carousels = []

    recommendation_categories = {}
    if request.user.is_authenticated:
        recommendation_categories, _ = get_recommendation_for_user(request.user)

        
        recommended_books = []

        for book_list in recommendation_categories.values():
            recommended_books.extend(book_list)

        # ha ujdonsult felhasznalo / nem interaktalt konyvekkel, akkor random beoszt az osszes konyv kozul.
        if not recommended_books: 
            fallback_books = list(random.sample(books, min(16, len(books))))
            recommended_book_group = group_books(fallback_books, 4)
       
        else:
            unique_recommended_books = list(set(recommended_books))
            random.shuffle(unique_recommended_books)
            recommended_books = unique_recommended_books[:16]
            recommended_book_group = group_books(recommended_books, 4)

    

        #EXCLUDED
        recommended_category_ids = set(cat.id for cat in recommendation_categories.keys())

        excluded_categories = list(Category.objects.exclude(id__in=recommended_category_ids))
        random.shuffle(excluded_categories)
        excluded_category = excluded_categories[0] if excluded_categories else None

        if excluded_category:
            books_list = list(Book.objects.filter(category=excluded_category))
            books_in_non_recommended_category = random.sample(books_list, min(16, len(books_list)))
            
            book_group = group_books(books_in_non_recommended_category, 4)
            excluded_category_carousel.append( {
                'category': excluded_category,
                'book_group': book_group
        })
        

    #mufaj szerinti ajanlas.
    #csak akkor jelenik meg, ha valid a felhasznalo, es van interaction az oldallal.

        #                   duplikacio nelkul valasztunk kategoriakat -- random.sample
        selected_categories = random.sample(list(recommendation_categories.keys()) , min(2, len(recommendation_categories)))

        for category in selected_categories:
            books = list(recommendation_categories[category])
            random.shuffle(books)
            book_group = group_books(books[:16], 4)
            recommended_category_carousels.append({
                'category': category,
                'book_group': book_group
            })
    
    context = {
        'recommended_book_group': recommended_book_group,
        'all_books_group': all_books_group,
        'recent_books_group': recent_books_group,
        "recommended_category_carousels": recommended_category_carousels,
        "excluded_category_carousel": excluded_category_carousel,
    }
    
    return render(request, "homepage.html", context)

#szemelyre szabott oldal
@login_required
def for_you_filter_view(request):
    recommendation_categories, category_weights = get_recommendation_for_user(request.user)

    top_categories = []
    for category, books in recommendation_categories.items():
        if books:
            grouped_books = group_books(books, 4)
            top_categories.append({
                'id': category.id,
                'name': category.category_name,
                'books_group': grouped_books
            })

    return render(request, 'for_you_filter.html', {'top_categories': top_categories})


@login_required
def profile_page_view(request):
    return render(request, 'profile.html', {})

# - current borrowing = folyamatban levo
@login_required
def current_borrowings_page_view(request):
    

    current_borrowings = Borrowing.objects.filter(user=request.user, is_verified=False).order_by('-borrow_date')
    verified_borrowings = VerifiedBorrowing.objects.filter(user=request.user).order_by('-due_date')

    today = timezone.now().date()
    for vb in verified_borrowings:
        vb.is_late = (vb.due_date is not None 
                      and vb.due_date < today
                      and not vb.is_returned
        )
    
    return render(request, 'current_borrowings.html',
                   {'current_borrowings': current_borrowings, 'verified_borrowings': verified_borrowings, 'today': today})

#reszletesebben a borrowingrol.
@login_required
@cache_page(900)
def current_borrowings_detail_page_view(request, borrowing_id):

    current_borrowings = get_object_or_404(Borrowing, id=borrowing_id, user=request.user)
    
    return render(request, 'current_borrowings_detail.html',
                   {'current_borrowings': current_borrowings})

@login_required
@require_POST
def delete_current_borrowing(request, borrowing_id):
    borrowing = get_object_or_404(Borrowing, id=borrowing_id, user=request.user)

    if request.method == "POST":
        borrowing.delete()
        messages.success(request, "Kölcsönzési igénylés visszavonva!")
        return redirect("current_borrowings")

    return redirect("current_borrowings_detail", borrowing_id=borrowing_id)

#reszletesebben a borrowingrol.
@login_required
@cache_page(900)
def verified_borrowings_detail_page_view(request, verified_borrowing_id):

    verified_borrowings = get_object_or_404(VerifiedBorrowing, id=verified_borrowing_id, user=request.user)
    
    return render(request, 'current_borrowings_detail.html',
                   {'verified_borrowings': verified_borrowings})



#history
@login_required
def history_borrowings_page_view(request):

    borrow_history = BorrowHistory.objects.filter(user=request.user).order_by('-return_date')
    paginator = Paginator(borrow_history, 4) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'history_borrowings.html',
                    {'page_obj': page_obj})

#reszletesebben a borrowingrol.
@cache_page(900)
@login_required
def history_borrowings_detail_page_view(request, history_id):

    borrow_history = get_object_or_404(BorrowHistory, id=history_id, user=request.user)

    paginator = Paginator(borrow_history.books.all(), 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'history_borrowings_detail.html', 
                  {'borrow_history': borrow_history, 'page_obj': page_obj})

#ertekelesek
@login_required
def reviews_page_view(request):

    reviews = Review.objects.filter(user=request.user).order_by('-updated_at')

    paginator = Paginator(reviews.all(), 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'reviews_profile.html', {'page_obj': page_obj}) 


#kategoria szerinti szuro oldal.
def category_filter_view(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    books = Book.objects.filter(category=category)

    sorting_op = request.GET.get('sort')

    if sorting_op == 'title_asc':
        books = books.order_by('title')
    elif sorting_op == 'title_desc':
        books = books.order_by('-title')
    elif sorting_op == 'fresh':
        books = books.order_by('-created_at')
    elif sorting_op == 'availability':
        books = books.annotate(
            available_count=Count('book_copies', filter=Q(book_copies__status='e') )
        ).order_by('-available_count')
    

    paginator = Paginator(books , 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'books': books, 
        'page_obj': page_obj, 
        'sorting_op': sorting_op
    }

    return render(request, 'category_filter.html', context)

#szerzo szerinti szuro oldal.
def author_filter_view(request, author_id):
    author = get_object_or_404(Author, id=author_id)

    books = Book.objects.filter(author=author)

    sorting_op = request.GET.get('sort')

    if sorting_op == 'title_asc':
        books = books.order_by('title')
    elif sorting_op == 'title_desc':
        books = books.order_by('-title')
    elif sorting_op == 'fresh':
        books = books.order_by('-created_at')
    elif sorting_op == 'availability':
        books = books.annotate(
            available_count=Count('book_copies', filter=Q(book_copies__status='e') )
        ).order_by('-available_count')
    

    paginator = Paginator(books , 8) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
            'author': author,
            'books': books, 
            'page_obj': page_obj, 
            'sorting_op': sorting_op
    }

    return render(request, 'author_filter.html', context)

#osszes konyv alapjan szuro oldal
def all_books_filter_view(request):
    books = Book.objects.select_related('author').prefetch_related('category').all()

    sorting_op = request.GET.get('sort')

    if sorting_op == 'title_asc':
        books = books.order_by('title')
    elif sorting_op == 'title_desc':
        books = books.order_by('-title')
    elif sorting_op == 'fresh':
        books = books.order_by('-created_at')
    elif sorting_op == 'availability':
        books = books.annotate(
            available_count=Count('book_copies', filter=Q(book_copies__status='e') )
        ).order_by('-available_count')
    
    

    paginator = Paginator(books , 8) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
            'books': books, 
            'page_obj': page_obj, 
            'sorting_op': sorting_op
    }

    return render(request, 'all_books_filter.html', context)

#szoveg "normalizalasa", azaz a specialis karaktereket nem kell begepelni hogy search hozza megjelenjen.
import unicodedata
def normalize_search_text(s: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')

#search results - kereso mezoben valo kereses oldala
def search_site(request):
    searches = request.GET.get('searches', '').strip()
    norm_search = normalize_search_text(searches).lower() if searches else ''
    
    books = []
    authors = []

    if norm_search:
        for book in Book.objects.all():
            if norm_search in normalize_search_text(book.title).lower():
                books.append(book)

        for author in Author.objects.all():
            if (norm_search in normalize_search_text(author.k_nev).lower() or
                norm_search in normalize_search_text(author.v_nev).lower()):
                authors.append(author)

    context = {
        'searches': searches,
        'books': books,
        'authors': authors,
    }

    return render(request, 'search_result.html', context)

