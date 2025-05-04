from django.db import models
from django.contrib.auth.models import User
from books.models import Book

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_user', verbose_name='Felhasználó')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='review_book', verbose_name='Könyv')
    rating = models.PositiveIntegerField(choices=[(i, f'{i} ⭐') for i in range(1, 6)], verbose_name='Értékelés')
    comment = models.TextField(max_length= 500, verbose_name='Megjegyzés')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Posztolás ideje")
    updated_at = models.DateTimeField(auto_now=True)  

    class Meta:
        verbose_name = "Értékelés"
        verbose_name_plural = "Értékelések"
        unique_together = ('user', 'book') 
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.book.title} ({self.rating})"