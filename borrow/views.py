from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.models import User
from books.models import Book, BookCopy
from .models import BorrowingList, BorrowingListItem, Borrowing
from django.db import transaction
from django.urls import reverse

from recommendation.reset_recommendation_cache import reset_recommendation_cache

#kolcsonzesi igenlyes page megjelenitese
@login_required
def view_borrowing_list(request):

    borrowing_list, created = BorrowingList.objects.get_or_create(
        user=request.user, 
        is_processed=False
    )
    
    return render(request, 'borrow/borrow.html', {
        'borrowing_list': borrowing_list,
        'list_items': borrowing_list.list_item.all()
    })

@login_required
@require_POST
def add_to_borrowing_list(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    borrowing_list, created = BorrowingList.objects.get_or_create(
        user=request.user, 
        is_processed=False
    )

    existing_borrowing = Borrowing.objects.filter(
        user=request.user, 
        book_copies__book=book,
        is_returned=False
    )

    if existing_borrowing.exists():
        messages.error(request, "Ezt a könyvet már kikölcsönözted!!!")
        return redirect(reverse('book_detail', kwargs={'book_id': book.id}))


    if borrowing_list.list_item.filter(book=book).exists():
        messages.warning(request, "Ez a könyv már a kölcsönzési igényléseid között van!!!")
        return redirect(reverse('book_detail', kwargs={'book_id': book.id}))  
    

    available_copy = book.book_copies.filter(status='e').first() 
    if not available_copy:
        messages.warning(request, f"Nincs elérhető példány ebből a könyvből: '{book.title}'")
        return redirect(reverse('book_detail', kwargs={'book_id': book.id}))  

    #konyvet hozzaadjuk az igenlyesekhez.
    BorrowingListItem.objects.create(borrowing_list=borrowing_list, book=book)

    messages.success(request, f"'{book.title}' hozzáadva az igénylésekhez.")

    #CACHE RESET
    reset_recommendation_cache(request.user.id)

    return redirect('view_borrowing_list')


# kolcsonzesi igenyles feldolgozasa...
@login_required
@transaction.atomic
@require_POST
def process_borrowing_list(request):

    borrowing_list = get_object_or_404(BorrowingList, user=request.user, is_processed=False)

    if not borrowing_list.list_item.exists():
        messages.warning(request, "Nem kölcsönöztél semmit! Először válassz könyvet/könyveket, amelyeket kölcsönözni szeretnél!")
        return redirect('view_borrowing_list')

    list_of_books = borrowing_list.list_item.all()
    
    if list_of_books.count() > 5:
        messages.error(request, "Legfeljebb 5 könyvet kölcsönözhetsz egyszerre.")
        return redirect('view_borrowing_list')
    
    active_borrowings = Borrowing.objects.filter(user=request.user, is_returned=False)
    if active_borrowings.count() >= 2:
        messages.error(request, "Nem lehet 2-nél több aktív kölcsönzésed...")
        return redirect('current_borrowings')
    
    borrowing = Borrowing.objects.create(
        user=request.user,
        borrow_date=timezone.now(),
        borrowing_list=borrowing_list
        )


    for list_item in list_of_books:
        book = list_item.book
        available_copy = book.book_copies.filter(status='e').first()
        
        if available_copy:
            available_copy.status = 'f' 
            available_copy.borrower = request.user
            available_copy.save()
            borrowing.book_copies.add(available_copy)  


    borrowing_list.is_processed = True
    borrowing_list.save()
        
    messages.success(request, f"Sikeresen lefoglaltál {borrowing_list.list_item.count()} könyvet.")

    #CACHE RESET
    reset_recommendation_cache(request.user.id)

    return redirect('view_borrowing_list') 
    


@login_required
@require_POST
def remove_from_borrowing_list(request, list_item_id):

    list_item = get_object_or_404(
        BorrowingListItem, 
        id=list_item_id, 
        borrowing_list__user=request.user, 
        borrowing_list__is_processed=False
    )
    
    book_title = list_item.book.title
    list_item.delete()
    
    messages.success(request, f"'{book_title}' eltávolítva az igénylések listából.")

    #CACHE RESET
    reset_recommendation_cache(request.user.id)

    return redirect('view_borrowing_list')  

