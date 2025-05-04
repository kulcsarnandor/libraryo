#SAJAT FILTEREK TEMPLATE-EKHEZ.
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, 0)


@register.filter
def repeat(value, count):
    return str(value) * int(count)

@register.filter
def star_icons(rating):
    try:
        rating = float(rating)
    except (ValueError, TypeError):
        return ['empty'] * 5

    icons = []
    for i in range(1, 6):
        if rating >= i:
            icons.append('full')
        elif rating >= i - 0.5:
            icons.append('half')
        else:
            icons.append('empty')
    return icons

# https://docs.djangoproject.com/en/5.1/howto/custom-template-tags/
# __init__.py is kell csinalni, hogy felismerje a package-t...