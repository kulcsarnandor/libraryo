from django.test import TestCase
from .views import get_recommendation_for_user

# Az ajanlorendszer eredmenyeit kijelzo teszt function; konzolba kiiratjuk vele.
# szukseges parancsok: 
# from recommendation.tests  
# import test_recommendations_for_user test_recommendations_for_user('username') -- 'username' helyere egyik felhasznalo felhneve.
# 
def test_recommendations_for_user(username):
    from django.contrib.auth.models import User
    
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        print(f"Error: User '{username}' does not exist...")
        return
    
    print(f"\n=== TESTING FOR USER: {username} ===")
    
    recommended_books, category_weights = get_recommendation_for_user(user)
    
    if not recommended_books:
        print("No recommendations found...")
        return
    
    print(f"Found {len(recommended_books)} recommended categories...")
    
    for category, books in recommended_books.items():
        weight = category_weights.get(category.id, 0)
        print(f"\nCategory: {category.category_name} - Weight: {weight}")
        print(f"Num of recommended books: {len(books)}")
        
        # kiiratjuk az osszes konyvet a mufajbol
        for i, book in enumerate(books, 1):
            print(f"  {i}. {book.title}")

# Create your tests here.
