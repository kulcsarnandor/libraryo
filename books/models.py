from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

from cloudinary.models import CloudinaryField
import cloudinary.uploader

from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

class Author(models.Model):
    k_nev = models.CharField(max_length=100,
                             verbose_name='Keresztnév')
    v_nev = models.CharField(max_length=100,
                             verbose_name='Vezetéknév')

    class Meta:
        ordering = ['v_nev', 'k_nev']
        verbose_name = "Szerző" 
        verbose_name_plural = "Szerzők"  

    def __str__(self):
        return f'{self.v_nev}, {self.k_nev}'

class Category(models.Model):
  category_name = models.CharField(max_length=100, 
                                   help_text='Adja meg a műfajt...',
                                   verbose_name='Műfaj')
  
  class Meta:
      verbose_name = "Műfaj" 
      verbose_name_plural = "Műfajok"  
    
  def __str__(self):
      return self.category_name
      

class Book(models.Model):
  title = models.CharField(max_length=150, verbose_name="Cím")

  author = models.ForeignKey(Author, 
                             on_delete=models.SET_NULL,
                             null=True,
                             verbose_name="Szerző")
  description = models.TextField(max_length=2000,
                                help_text='Írjon rövid összefoglalást a könyvhöz... Max. 2000 karakter',
                                verbose_name="Leírás")
  
  category = models.ManyToManyField(Category, 
                                    help_text='Válasszon műfajokat a könyvhöz...',
                                    verbose_name="Műfaj")
  
  isbn = models.CharField('ISBN',   max_length=13,
                                    validators=[RegexValidator(r'^\d+$',
                                    message="Az ISBN csak számokat tartalmazhat...")], 
                                    unique=True, 
                                    help_text='13 karakteres ISBN szám')
  page_number = models.CharField('Oldalak száma',
                                 max_length=4,
                                 validators=[RegexValidator(r'^\d+$')],
                                  )
  
  created_at = models.DateTimeField(auto_now_add=True)

  ''' # Production -- upload images.
  cover_image = models.ImageField(upload_to='book-covers',
                                   null=True, blank=True,
                                   verbose_name="Borítókép")
  '''
  cover_image = CloudinaryField('Borítókép',
                                folder='book-covers/', 
                                blank=True, null=True)
  
  
    

  
  
  def is_available(self):
      return self.book_copies.filter(status='e').exists()
  
  def available_copies(self): #mennyi elerheto copy van jelenleg raktaron
      return self.book_copies.filter(status='e').count()
  
  def total_copies(self):
      return self.book_copies.count()
  
  
        
  class Meta:
        ordering = ['title', 'author', 'page_number', 'description', 'cover_image', 'isbn']
        verbose_name = "Könyv" 
        verbose_name_plural = "Könyvek"

  def __str__(self):
        return self.title

#konyvpeldany
class BookCopy(models.Model):

    book = models.ForeignKey(
        Book,  
        on_delete=models.CASCADE, 
        related_name='book_copies',
        verbose_name="Könyv"
    )

    is_available = models.BooleanField(default = True)
    
    #allapotok listaja
    BORROW_STATUS = (
        ('e', 'Elérhető'),
        ('f', 'Foglalt'),
        ('k', 'Kikölcsönözve'),   
        ('v', 'VISSZAHOZATAL SÜRGŐSEN!'),
    )
    
    #jelenlegi allapot
    status = models.CharField(
        max_length=1,
        choices=BORROW_STATUS,
        default='e',
        help_text='Példány állapota.',
        verbose_name="Állapot"
    )
    
    #kolcsonzo szemely.
    borrower = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        related_name='borrowers',
        null=True, 
        blank=True,
        verbose_name="Kölcsönző felhasználó"
    )  
    
    
    class Meta:
        verbose_name = 'Könyv példány'
        verbose_name_plural = 'Könyv példányok'


    def __str__(self):
        return f'{self.id} ({self.book.title})'


@receiver(post_delete, sender=Book)
def delete_cover_image_on_book_delete(sender, instance, **kwargs):
    if instance.cover_image:
        cloudinary.uploader.destroy(instance.cover_image.public_id)

@receiver(pre_save, sender=Book)
def delete_old_cover_image_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_instance = Book.objects.get(pk=instance.pk)
    except Book.DoesNotExist:
        return

    if old_instance.cover_image and old_instance.cover_image != instance.cover_image:
        # cover image was cleared or changed
        cloudinary.uploader.destroy(old_instance.cover_image.public_id)

