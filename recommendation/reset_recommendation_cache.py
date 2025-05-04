from django.core.cache import cache

# -- ha felhasznalo kezeli az oldalon lévő recommendation funkciokat, pl wishlist, igenyel, akkor az eddigi cache-t az ajanlasairol toroljuk..
def reset_recommendation_cache(user_id):
    cache_key = f"recs:user:{user_id}"
    print(f"resetting cache for {user_id} ...")
    cache.delete(cache_key)
    print(f"CACHE RESET FOR USER: {user_id}")