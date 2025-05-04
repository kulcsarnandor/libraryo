from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Review
from books.models import Book

#ertekeles posztolasa.
@login_required
@require_POST
def submit_review(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        comment = request.POST.get('comment')
        rating = request.POST.get('rating')

        if not comment or not rating:
            messages.warning(request, 'Kérjük írjon véleményt (max. 500 karakter) és válasszon értékelést (1-5-ig)')
            return redirect('book_detail', book_id=book.id)

        review, created = Review.objects.update_or_create(
        user=request.user, 
        book=book,
        defaults={
            'rating': rating,
            'comment': comment
    } )
        
        if created:
          messages.success(request, 'Köszönjük az új értékelést!')
        else:
          messages.success(request, 'Értékelés sikeresen frissítve!')

        return redirect('book_detail', book_id=book.id)

    return redirect('book_detail', book_id=book.id)

# ertekeles torlese.
@login_required
@require_POST
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if review.user != request.user:
        messages.error(request, "Nincs jogosultságod törölni ezt a véleményt.")
        return redirect('book_detail', book_id=review.book.id)

    review.delete()
    messages.success(request, "Vélemény törölve!")
    return redirect('book_detail', book_id=review.book.id)
