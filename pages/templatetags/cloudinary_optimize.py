from django import template

register = template.Library()

#kepek URL-jebe cloudinary transzformaciokat helyezunk optimalizacio erdekeben.
@register.filter
def cloudinary_minimize_image(url, transformation="w_200,h_300,c_fill,f_auto,q_auto"):
    if not url:
        return ""
    
    #csak a cloudinary kep URL-eket allitsuk at.
    if "res.cloudinary.com" not in url:
        return url
    
    return url.replace('/upload/', f'/upload/{transformation}/')