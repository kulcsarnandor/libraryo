from books.models import Category, Author

def categories_processor(request):
    return {'categories': Category.objects.all()}

def authors_processor(request):
    return {'authors_all': Author.objects.all()}

#SETTINGSBEN EZEKET BEALLITANI -- NAVBAR FILTEREK.