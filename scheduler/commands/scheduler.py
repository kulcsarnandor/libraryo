from apscheduler.schedulers.background import BackgroundScheduler
from borrow.models import VerifiedBorrowing, Borrowing, BorrowingListItem
import datetime
from django.utils import timezone


def check_if_borrowing_overdue():
    print(f"---SCHEDULER FUT: {timezone.now()} -kor ...")
    overdue_borrowings = VerifiedBorrowing.objects.filter(due_date__lt=datetime.date.today())
    overdue_request_borrowings = Borrowing.objects.filter(expire_date__lt=datetime.date.today())

    print(f"===TALALTUNK {overdue_request_borrowings.count()} LEJART KOLCSONZESI KEREST!!!")
    print(f"===TALALTUNK {overdue_borrowings.count()} LEJART KIKOLCSONZEST - VERIFIED !!!")

    #overdue verifiedborrow. -- kikolcsonzott
    for borrowing in overdue_borrowings:
        book_copies = borrowing.borrowing.book_copies.all()
        
        #konyv peldanyok 'visszahozatal surgosen' allapotra ha kikolcsonzott konyv nem lett visszahozva
        for book_copy in book_copies:
            if book_copy.status == 'k':  
                book_copy.status = 'v' 
                book_copy.save()
                print(f"BookCopy ID: {book_copy.id} - statusza atallitva --> 'v' !!!")

    #overdue requests. -- foglalt
    for borrowing in overdue_request_borrowings:
        book_copies = borrowing.book_copies.all()

        #konyv peldanyok visszaalitasa 'elerheto're ha nem jott el a konyvert, amely le volt foglalva.
        for book_copy in book_copies:
            if book_copy.status == 'f': 
                book_copy.status = 'e'  
                book_copy.borrower = None 
                book_copy.save()
                print(f"BookCopy ID: {book_copy.id} - statusza visszaallitva --> 'e' ...")

        #borrowing, ill. annak elemeinek torlese.
        if borrowing.borrowing_list:
            BorrowingListItem.objects.filter(borrowing_list=borrowing.borrowing_list).delete()
            borrowing.borrowing_list.delete()

        borrowing.delete()

'''
# render webszerverre feltettuk a cronjob-ot, lokalisan szuksegunk lenne a fuggvenyre...
def start_borrowing_overdue_scheduler():
        scheduler = BackgroundScheduler()

        scheduler.add_job(check_if_borrowing_overdue, 'interval', hours=1)
        scheduler.start()
        print("SCHEDULER STARTED...")

'''
