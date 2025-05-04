from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db import IntegrityError
from .models import Wishlist 
from books.models import Book, Category

from books.models import Category


from django.core.paginator import Paginator

from borrow.models import Borrowing, VerifiedBorrowing, BorrowHistory
from collections import Counter

from django.core.cache import cache
from .reset_recommendation_cache import reset_recommendation_cache




# --- Nézet a kívánságlista megjelenítéséhez; Megjeleníti a bejelentkezett felhasználó kívánságlistáját.
@login_required 
def view_wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('book', 'book__author') 

    paginator = Paginator(wishlist_items.all(), 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'pages/wishlist.html', {'wishlist_items': wishlist_items, 'page_obj':page_obj }) 

# -- Nézet könyv hozzáadásához a kívánságlistához; Hozzáad egy könyvet a felhasználó kívánságlistájához.
@login_required
@require_POST
def add_to_wishlist(request):
    book_id = request.POST.get('book_id')
    if book_id:
        book = get_object_or_404(Book, id=book_id)
        try:
            Wishlist.objects.create(user=request.user, book=book)
            messages.success(request, f"'{book.title}' sikeresen hozzáadva a kívánságlistához.")

            #CACHE RESET
            reset_recommendation_cache(request.user.id)

        except IntegrityError: 
            messages.info(request, f"'{book.title}' már szerepel a kívánságlistádon!")
        except Exception as e:
            messages.error(request, f"Hiba történt a könyv hozzáadása közben: {e}")
            
    else:
        messages.error(request, "Nem létező könyv azonosító.")

    return redirect('book_detail', book_id=book.id) 


# --- Nézet elem eltávolításához a kívánságlistáról --- Eltávolít egy adott elemet (item_id alapján) a felhasználó kívánságlistájáról.
@login_required
@require_POST 
def remove_from_wishlist(request, item_id):
    wishlist_item = get_object_or_404(Wishlist, id=item_id, user=request.user)
    
    book_title = wishlist_item.book.title 
    
    wishlist_item.delete()
    messages.success(request, f"'{book_title}' eltávolítva a kívánságlistáról.")
    
    #CACHE RESET
    reset_recommendation_cache(request.user.id)
    
    return redirect('view_wishlist')



CACHE_TIME = 900

# RECOMMENDATION SYSTEM FUNCTION!
def get_recommendation_for_user(user, max_num_categories=5):
    #CACHE-eljuk a felhasznalo ajanlasait.
    #ha felhasznalo kezeli az oldalon lévő recommendation funkciokat, pl wishlist, igenyel, akkor az eddigi cache-t az ajanlasairol toroljuk.. --> reset_recommendation_cache
    cache_key = f"recs:user:{user.id}"
    cached = cache.get(cache_key)
    if cached is not None:
        print(f"==== CACHE TALALAT for user {user.username} (ID={user.id}) ! ====")
        return cached

    category_weights = Counter()
    interacted_books = set()

    def get_categories(book):
        return list(book.category.all())

    def update_category_weights(books, weight):
        for book in books:
            interacted_books.add(book.id)
            category_weights.update({category.id: weight for category in get_categories(book)})

    # 1. Verified Borrowings — 2 pts
    verified_borrowings = VerifiedBorrowing.objects.filter(user=user).prefetch_related('book_copies__book__category')
    for vb in verified_borrowings:
        for book_copy in vb.book_copies.all():
            update_category_weights([book_copy.book], 2)

    # 2. Borrow History —> 3 most recent = 2 pts, older = 1 pt
    history_borrowings = list(BorrowHistory.objects.filter(user=user).order_by('-return_date').prefetch_related('books__category') )
    recent_histories = history_borrowings[:3]
    old_histories = history_borrowings[3:]

    for history in recent_histories:
        update_category_weights(history.books.all(), 2)
    for history in old_histories:
        update_category_weights(history.books.all(), 1)

    # 3. Wishlist — 2 points
    wishlist = Wishlist.objects.filter(user=user)
    for item in wishlist:
        update_category_weights([item.book], 2)

    # 4. Foglalt Borrowings  — 1 pt
    foglalt_borrowings = Borrowing.objects.filter(user=user, is_verified=False).prefetch_related('book_copies__book__category')
    for fb in foglalt_borrowings:
        for book_copy in fb.book_copies.all():
            update_category_weights([book_copy.book], 1)

    # Jelenleg kikolcsonzott + nemreg kikolcsonzott (historyborrowing most recent 3) konyveket kiszedjuk az ajanlott konyvek kozul.
    excluded_books = set()
    for vb in verified_borrowings:
        excluded_books.update(book_copy.book.id for book_copy in vb.book_copies.all())
    for fb in foglalt_borrowings:
        excluded_books.update(book_copy.book.id for book_copy in fb.book_copies.all())
    for history in recent_histories:
        excluded_books.update(book.id for book in history.books.all())

    # Felhasznalo szamara legerdekesebb mufajok
    top_categories = [cat_id for cat_id, _ in category_weights.most_common(max_num_categories)]

    recommendation_categories = {}
    category_weight_dict = {}

    for category_id in top_categories:
        category = Category.objects.get(id=category_id)
        all_category_books = Book.objects.filter(category=category).select_related("author").distinct()
        category_books = all_category_books.exclude(id__in=excluded_books)

        if category_books.exists():
            recommendation_categories[category] = list(category_books)
            category_weight_dict[category.id] = category_weights[category_id]

    result = (recommendation_categories, category_weight_dict)
    cache.set(cache_key, result, CACHE_TIME)
    # ----------------------------------------------------
    print(f"====CACHE MISSING FOR USER {user.username} (ID={user.id}) --> CACHE BEALLITASA...====")
    
    return result
