from django.db import models
from django.contrib.auth.models import User
from books.models import Book
from borrow.models import BorrowHistory, VerifiedBorrowing
from django.core.validators import RegexValidator
import datetime

#Egy elemet reprezentál a felhasználó kívánságlistáján.
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_item', verbose_name='Felhasználó')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='wishlisted', verbose_name='Könyv')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Hozzáadás dátuma')

    class Meta:
        unique_together = ('user', 'book') 
        ordering = ['-created_at']
        verbose_name = "Kívánságlista"
        verbose_name_plural = "Kívánságlisták"

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"
