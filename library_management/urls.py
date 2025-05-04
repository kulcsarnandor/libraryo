from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from pages import views as page_views
from borrow import views as borrow_views
from books import views as book_views
from review import views as review_views
from recommendation import views as recommendation_views
from register import views as register_views
from register.forms import CustomSetPasswordForm 

from django.conf import settings
from django.conf.urls.static import static

from scheduler.views import run_cronjob_overdue


urlpatterns = [
    #Admin panel URL
    path('admin/', admin.site.urls),
    
    #home page URL
    path('', page_views.home_page_view, name='home'),

    #loginregisterlogout URL
    path('register/', register_views.register_user, name = "register"),
    path('login/', register_views.login_user, name = "login"),
    path('logout/', register_views.logout_user, name = "logout"),

    #email verification
    path('verify-email/<uidb64>/<token>/', register_views.verify_email, name="verify_email"),
    
    #password reset
    path('reset-password/', register_views.CustomPasswordResetView.as_view(template_name="register/password-reset.html"), name = "reset_password"),
    path('reset-password-sent/', auth_views.PasswordResetDoneView.as_view(template_name="register/password-reset-sent.html"), name = "password_reset_done"),
    path('reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(template_name="register/password-reset-form.html", form_class=CustomSetPasswordForm),
        name = "password_reset_confirm"),
    path('reset-password-complete/', auth_views.PasswordResetCompleteView.as_view(template_name="register/password-reset-done.html"), name = "password_reset_complete"),

    #book detail URL
    path('book/<int:book_id>/', book_views.book_detail_view, name = "book_detail"),

    #borrow URLs
    path('borrow/', borrow_views.view_borrowing_list, name = 'view_borrowing_list'),
    path('borrow/add/<int:book_id>/', borrow_views.add_to_borrowing_list, name='add_to_borrowing_list'),
    path('borrow/process/', borrow_views.process_borrowing_list, name='process_borrowing_list'),
    path('borrow/remove/<int:list_item_id>/', borrow_views.remove_from_borrowing_list, name='remove_from_borrowing_list'),

    #profile URLs
    path('profile/', page_views.profile_page_view, name='profile'),

    #CurrentBorrowing URLs
    path('current_borrowings/', page_views.current_borrowings_page_view, name='current_borrowings'),
    path('current_borrowings_detail/<int:borrowing_id>/', page_views.current_borrowings_detail_page_view, name='current_borrowings_detail'),
    path("borrowing/delete/<int:borrowing_id>/", page_views.delete_current_borrowing, name="delete_current_borrowing"),

    #VerifiedBorrowing URL
    path('verified_borrowings_detail/<int:verified_borrowing_id>/', page_views.verified_borrowings_detail_page_view, name='verified_borrowings_detail'),

    #HistoryBorrowing URLs
    path('history_borrowings/', page_views.history_borrowings_page_view, name='history_borrowings'),
    path('history_borrowings_detail/<int:history_id>/', page_views.history_borrowings_detail_page_view, name='history_borrowings_detail'),

    #Reviews URL
    path('reviews_profile/', page_views.reviews_page_view, name='reviews_profile'),

    #Wishlist URLs
    path('wishlist/', recommendation_views.view_wishlist, name='view_wishlist'), 
    path('wishlist/add/', recommendation_views.add_to_wishlist, name='add_to_wishlist'), 
    path('remove/<int:item_id>/', recommendation_views.remove_from_wishlist, name='remove_from_wishlist'), 


    #filter URLs

    #Category
    path('category_filter/<int:category_id>/', page_views.category_filter_view, name='category_filter'),
    #Author
    path('author_filter/<int:author_id>/', page_views.author_filter_view, name='author_filter'),
    #ForYou
    path('for_you_filter/', page_views.for_you_filter_view, name='for_you_filter'),
    #AllBooks
    path('all_books_filter/', page_views.all_books_filter_view, name='all_books_filter'),

    #search feature URL
    path('search/', page_views.search_site, name='search_site'),

    #reviews URLs
    path('submit/<int:book_id>/', review_views.submit_review, name='submit_review'),
    path('review/delete/<int:review_id>/', review_views.delete_review, name='delete_review'),

    #CRON-JOB url
    path('cron-job-overdue/', run_cronjob_overdue, name='cron-job-overdue'),

]

#media fajlok kezelesehez szukseges kód, ha buildelunk.

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

