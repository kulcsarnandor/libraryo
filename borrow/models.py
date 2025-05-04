from django.db import models, transaction
from django.contrib.auth.models import User
from books.models import Book, BookCopy
from django.utils import timezone
import datetime
from django.core.exceptions import ValidationError

#Kolcsonzesi igenlyes -- tobb konyv kezelese egyetlen tranzakcioval.
class BorrowingList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrow_list')
    is_processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Kölcsönzesi lista: {self.user.username}'
    
    
#Az egyes konyveket jelenti a kolcsonzesi igenylesben...
class BorrowingListItem(models.Model):
    
    borrowing_list = models.ForeignKey(BorrowingList, on_delete=models.CASCADE, related_name='list_item')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.book.title} az ő kölcsönzési listájába került: {self.borrowing_list.user.username}"

#IGENLYES
class Borrowing(models.Model):
    def get_expire_date():
        return timezone.now() + datetime.timedelta(days=2)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrowing', verbose_name="Felhasználó")
    borrowing_list = models.ForeignKey(BorrowingList, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Igénylés ID")
    book_copies = models.ManyToManyField(BookCopy, verbose_name="Könyv példányok")
    borrow_date = models.DateTimeField(default=timezone.now, verbose_name="Igénylés ideje")
    expire_date = models.DateField(default = get_expire_date, verbose_name="Határidő elvitelre")
    is_returned = models.BooleanField(default=False)
    is_verified = models.BooleanField(default = False, verbose_name="KÖLCSÖNZÉS JÓVÁHAGYÁSA")

    def create_verified_borrowing(self):
        #adatbiztonsag/integritas fenntartasa erdekeben hasznaljuk a transaction.atomic fuggvenyt.
        #ha barmi hiba tortenik, minden valtozast visszavon.
        with transaction.atomic():  
                #veletlen duplikacio megelozese erdekeben toroljuk ha mar letezik verifiedborrowing.
                VerifiedBorrowing.objects.filter(borrowing=self).delete()
                
                verified_borrowing = VerifiedBorrowing(
                    borrowing=self,
                    borrowing_list=self.borrowing_list,
                    borrow_date=self.borrow_date,
                    due_date=self.borrow_date + datetime.timedelta(days=14),
                    user=self.user
                )

                verified_borrowing.save()

                for book_copy in self.book_copies.all():
                    book_copy.is_available = False
                    book_copy.borrower = self.user
                    book_copy.save()
                
                
                verified_borrowing.book_copies.set(self.book_copies.all())
    


    def save(self, *args, **kwargs):
         #LIMIT -- max 2 kocsonzesi igenyles/felhasznalo
        if self.pk is None:
            active_borrowings = Borrowing.objects.filter(user=self.user, is_returned=False)
            if active_borrowings.count() >= 2:
                raise ValidationError("Nem lehet 2-nél több aktív kölcsönzésed...")
        
        super().save(*args, **kwargs)

        # rogzites utan tudjuk csak a ManyToMany relaciohoz hozzakotni -- 
        # LIMIT -- max 5 konyv / kolcsonzesi igenyles.
        if self.book_copies.count() > 5:
            raise ValidationError("Egy kölcsönzés legfeljebb 5 könyvet tartalmazhat...")

        #ha el lett fogadva/ki lett adva kolcsonzesre a konyv az alkalmazott altal, akkor verifiedborrowingba tovabbitjuk
        if self.is_verified and not hasattr(self, 'verified_borrowing'):
            self.create_verified_borrowing()
        
    
    def delete(self, *args, **kwargs):
        with transaction.atomic():
            #visszaalitjuk a konyv peldanyok allapotait..
            if self.pk:
                for book_copy in self.book_copies.all():
                    book_copy.is_available = True
                    book_copy.borrower = None
                    book_copy.status = 'e' 
                    book_copy.save()
                
            if self.borrowing_list_id: 
                if BorrowingListItem.objects.filter(borrowing_list_id=self.borrowing_list_id).exists():
                    BorrowingListItem.objects.filter(borrowing_list_id=self.borrowing_list_id).delete()
                
                
                # doublechecking: ha meg mindig letezik a borrowinglist, akkor toroljuk.
                if BorrowingList.objects.filter(id=self.borrowing_list_id).exists():
                    self.borrowing_list.delete()
            
            #toroljuk a borrowingot.
            super().delete(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username} - {self.borrow_date.strftime('%Y-%m-%d %H:%M')} - {self.book_copies.count()} könyv"

    class Meta:
        ordering = ['-borrow_date']
        verbose_name = "1. Kölcsönzési igénylés" 
        verbose_name_plural = "1. Kölcsönzési igénylések"  

#VERIFIED -- A konyveket a felhasznalo megkapta, kikolcsonzes megtortent.
class VerifiedBorrowing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verified_borrowing', verbose_name="Felhasználó")
    borrowing_list = models.ForeignKey(BorrowingList, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Igénylés ID")
    borrowing = models.OneToOneField(Borrowing, on_delete=models.CASCADE, related_name='verified_borrowing', verbose_name="Kölcsönzés ID")
    book_copies = models.ManyToManyField(BookCopy, verbose_name="Könyv példányok")
    borrow_date = models.DateTimeField(default=timezone.now, verbose_name="Kikölcsönzés ideje")
    due_date = models.DateField(verbose_name="Határidő visszahozatalra")
    is_returned = models.BooleanField(default=False, verbose_name="VISSZAHOZVA")
    return_date = models.DateField(blank=True, null=True)

    def save(self, *args, **kwargs):
        #visszahozatal idejet itt szabjuk meg, 2 hettel a kikolcsonzes utanra.
        if not self.due_date:
            self.due_date = self.borrow_date + datetime.timedelta(days=14)

        if self.borrowing:
            self.borrowing.is_verified = True
            self.borrowing.save()

        super().save(*args, **kwargs)

        if self.borrowing and self.pk: 
            self.book_copies.set(self.borrowing.book_copies.all())

        #konyv peldany allapotat rogzitjuk...
        for book_copy in self.book_copies.all():
                if book_copy.status != 'k': 
                    book_copy.status = 'k' 
                    book_copy.save()

        #ha vissza lett hozva, akkor futtatjuk az ehhez relevans fuggvenyt.
        if self.is_returned and self.pk:
            transaction.on_commit(lambda: self.mark_as_returned())


    def delete(self, *args, **kwargs):
        with transaction.atomic():
            #visszaalitjuk a konyv peldanyok allapotait..
            for book_copy in self.book_copies.all():
                book_copy.is_available = True
                book_copy.borrower = None
                book_copy.status = 'e'
                book_copy.save()

            # borrowinglistitem es borrowinglist-eket toroljuk.
            if self.borrowing_list_id:
                BorrowingListItem.objects.filter(borrowing_list_id=self.borrowing_list_id).delete()
                BorrowingList.objects.filter(id=self.borrowing_list_id).delete()

            #toroljuk a borrowing objectet.
            if self.borrowing:
                self.borrowing.delete()

            #toroljuk a verifiedborrowingot is.
            super().delete(*args, **kwargs)
    
    #konyvek visszahozatala.
    def mark_as_returned(self):
        with transaction.atomic():
            self.return_date = timezone.now()

            #letrehozzuk az elozmenyeket.
            BorrowHistory.create_from_verified_borrowing(self)


            #konyv peldany allapotat visszaalitjuk...
            for book_copy in self.book_copies.all():          
                book_copy.is_available = True
                book_copy.borrower = None  
                book_copy.status = 'e'
                book_copy.save()

             #beallitjuk, hogy vissza lett hozva...
            if self.borrowing:
                self.borrowing.is_returned = True
                self.borrowing.save()
            
            #toroljuk az adatbazisbol a jelenlegi/verified kolcsonzest rogzito mostamar felesleges adatokat.
            if self.borrowing_list:
                BorrowingListItem.objects.filter(borrowing_list=self.borrowing_list).delete()
                self.borrowing_list.delete()

            if self.borrowing:
                self.borrowing.delete()

            super().delete()


    def __str__(self):
        user_name = self.borrowing.user.username if self.borrowing and self.borrowing.user else "..."
        return f"Kölcsönzés elfogadva: {user_name} - {self.borrow_date}"

    class Meta:
        verbose_name = "2. Folyamatban lévő kölcsönzés"
        verbose_name_plural = "2. Folyamatban lévő kölcsönzések"
        ordering = ['-borrow_date']

#HISTORY -- A kolcsonzesi elozmenyeket rogzitjuk felhasznalo szerint; a kikolcsonzott konyveket a felhasznalo visszahozta.
class BorrowHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='borrow_history', verbose_name="Felhasználó")
    books = models.ManyToManyField(Book, verbose_name="Könyvek")
    book_count = models.PositiveIntegerField(default=0, verbose_name="Könyvek száma")
    return_date = models.DateField(verbose_name="Visszahozatal ideje")
    due_date = models.DateField(verbose_name="Visszahozatal határideje")
    is_late = models.BooleanField(default=False, verbose_name = "Késett")

    class Meta:
        verbose_name = "3. Kölcsönzési előzmény"
        verbose_name_plural = "3. Kölcsönzési előzmények"
        ordering = ['-return_date']
    
    def __str__(self):
        user_name = self.user.username if self.user else "..."
        return f"Kölcsönzési előzmény ID:{self.id} - user: {user_name} - visszahozva: {self.return_date}"

    #Letrehozunk egyetlen BorrowHistory entry-t a VerifiedBorrowing-bol, feltetelezve hogy a felhasznalo visszahozta a konyveket.
    #classmethod --> uj BorrowHistory objectet hozunk letre a mar letezo VerifiedBorrowing object-bol; nincs szukseg mar letezo # BorrowHistory object-re.
    @classmethod
    def create_from_verified_borrowing(cls, verified_borrowing):
        
        borrowing = verified_borrowing.borrowing
        user = borrowing.user
        return_date = verified_borrowing.return_date
        is_late = verified_borrowing.due_date < return_date.date() if return_date else False

        unique_books = set()
        for book_copy in borrowing.book_copies.all():
            unique_books.add(book_copy.book)

         # a kolcsonzeshez letrehozunk egy history entry-t.
        history = cls.objects.create(
            user=user,
            book_count=len(unique_books),
            return_date=return_date,
            due_date=verified_borrowing.due_date,
            is_late=is_late
        )
        

        for book in unique_books:
            history.books.add(book)
        
        return history
    
