from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm # beepitett form
from django.contrib.auth.models import User

class RegistrationForm(UserCreationForm):
  email = forms.EmailField(
        required=True, 
        widget= forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Adja meg az e-mail címét!'}),
        label = 'E-mail'
    )
  vnev = forms.CharField(
        max_length=30, 
        required=True, 
        widget= forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Adja meg a vezetéknevét!'}),
        label = 'Vezetéknév'
    )
  knev = forms.CharField(
        max_length=30, 
        required=True, 
        widget= forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Adja meg a keresztnevét!'}),
        label = 'Keresztnév'
    )


  class Meta:
    model = User
    fields = ['username', 'vnev', 'knev', 'email', 'password1', 'password2' ]
    widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Adja meg a felhasználónevét!', 'label': 'Felhasználónév'})
        }

  # regisztracios form mezoinek atallitasa sajat szovegre, stb.
  def __init__(self, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Adja meg a jelszavát!'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Erősítse meg a jelszavát!'})
        self.fields['password1'].label = 'Jelszó' 
        self.fields['password1'].help_text = '<ul class="text-left"><li>Ajánlott az erős jelszó használata.</li><li>A jelszó legalább 8 karaktert kell hogy tartalmazzon.</li><li>A jelszó nem egyezhet túlságosan a többi megadott információval.</li></ul>' 
        self.fields['password2'].label = 'Jelszó megerősítése'  
        self.fields['password2'].help_text = ''
        self.fields['username'].label = 'Felhasználónév'
        self.fields['username'].help_text = '<ul class="text-left"><li>Kevesebb mint 150 karakter.</li>'  

  #felhnev check if already exists
  def clean_username(self):
      username = self.cleaned_data.get('username')
      if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Ez a felhasználónév már használatban van.")
      return username
  
    #ellenorizzuk, hogy az email egyedi-e az oldalon.
  def clean_email(self):
        
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Ez az email cím már használatban van.")
        return email
  
  # adatok rogzitese, elmentese.
  def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['knev']  
        user.last_name = self.cleaned_data['vnev']  
        if commit:
            user.save()
        return user

#bejelentkezes form.
class LoginForm(AuthenticationForm):
    error_messages = {
        'invalid_login': "Hibás felhasználónév vagy jelszó. Kérjük, próbálja újra!",
        'inactive': "Az e-mail nincs megerősítve! Kérjük, ellenőrizze az e-mail fiókját.",
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Felhasználónév' 
        self.fields['password'].label = 'Jelszó' 

#uj jelszo form.
class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Adja meg az új jelszót!'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Erősítse meg az új jelszót!'})
        
        self.fields['new_password1'].label = 'Új jelszó'
        self.fields['new_password1'].help_text = '<ul class="text-left"><li>Ajánlott az erős jelszó használata.</li><li>A jelszó legalább 8 karaktert kell hogy tartalmazzon.</li><li>A jelszó nem egyezhet túlságosan a többi megadott információval.</li></ul>'

        self.fields['new_password2'].label = 'Jelszó megerősítése'
        self.fields['new_password2'].help_text = ''

        