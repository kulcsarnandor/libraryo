from django.shortcuts import render, redirect
from .forms import RegistrationForm, LoginForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.views import PasswordResetView

#email megerositeshez szuksegesek.
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.html import strip_tags
from django.http import HttpResponse
from django.urls import reverse


def register_user(request):
  if request.method == "POST":
    form = RegistrationForm(request.POST) #beepitett form
    if form.is_valid():
        user = form.save(commit=False)
        user.is_active = False  #amig nincs megerositve a fiok, addig nem lehet bejelentkezni.
        user.save()

      #email verification token generalasa
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        verification_link = request.build_absolute_uri(reverse('verify_email', kwargs={'uidb64': uid, 'token': token}))

        #email kuldese
        subject = "Email-cím megerősítése - Library-O"
        html_coded_message = render_to_string('register/verification-email.html', {'verification_link': verification_link, 'user': user})
        text_message = strip_tags(html_coded_message)  #Text version of email message
        email = EmailMultiAlternatives(
            subject,
            text_message,  #Plain text 
            settings.DEFAULT_FROM_EMAIL,
            [user.email]
        )
        email.attach_alternative(html_coded_message, "text/html")  #HTML verzio
        email.send()

        messages.success(request, "Regisztráció sikeres! Kérjük ellenőrizze az e-mail fiókját a megerősítő linkkel.")
        return redirect("login")
    else:
      messages.error(request, "Hiba a regisztrációnál, próbálja újra!")
  else:
    form = RegistrationForm()

  return render(request, "register/register.html", {"register_form": form})

def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Email sikeresen megerősítve! Mostantól bejelentkezhet a weboldalunkra.")
        return redirect('login')
    else:
        return HttpResponse("Érvénytelen megerősítés...", status=400)

def login_user(request):
    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()

            if not user.is_active:
                messages.error(request, "Az e-mail nincs megerősítve! Kérjük, ellenőrizze az e-mail fiókját.")
                return redirect('login')
            
            login(request, user)
            messages.success(request, f'Sikeres bejelentkezés, üdvözöljük {user.username}! :)')
            return redirect('home')  
        else:
          messages.error(request, "Hibás felhasználónév vagy jelszó. Kérjük, próbálja újra!")
        

    return render(request, 'register/login.html', {'login_form': form})

def logout_user(request):
  logout(request)
  messages.success(request, "Sikeres kijelentkezés!")
  return redirect("home")


class CustomPasswordResetForm(PasswordResetForm):
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):

        user = context.get('user')
        
        subject = "Jelszó átállítás - Library-O"
        
        html_coded_message = render_to_string('register/password-reset-verification.html', context)
        text_message = strip_tags(html_coded_message) 
        
        email = EmailMultiAlternatives(
            subject,
            text_message,
            settings.DEFAULT_FROM_EMAIL,
            [to_email]
        )
        email.attach_alternative(html_coded_message, "text/html")  #HTML verzio
        email.send()

class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm


