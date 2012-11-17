import hashlib
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from misago.forms import Form
from misago.security import captcha
from misago.users.models import User
from misago.users.validators import validate_password, validate_email


class UserRegisterForm(Form):
    username = forms.CharField(max_length=15,help_text=_("Between 3 and 15 characters, only letters and digits are allowed."))
    email = forms.EmailField(max_length=255,help_text=_("Working e-mail inbox is required to maintain control over your forum account."))
    email_rep = forms.EmailField(max_length=255)
    password = forms.CharField(max_length=255,help_text=_("Password you will be using to sign in to your account. Make sure it's strong."))
    password_rep = forms.CharField(max_length=255)
    captcha_qa = captcha.QACaptchaField()
    recaptcha = captcha.ReCaptchaField()
    accept_tos = forms.BooleanField(required=True,label=_("Forum Terms of Service"),error_messages={'required': _("Acceptation of board ToS is mandatory for membership.")})
    
    validate_repeats = (('email', 'email_rep'), ('password', 'password_rep'))
    repeats_errors = [{
                       'different': _("Entered addresses do not match."), 
                       },
                      {
                       'different': _("Entered passwords do not match."),
                       }]
    
    layout = [
                 (
                     None,
                     [('username', {'placeholder': _("Enter your desired username")})]
                 ),
                 (
                     None,
                     [('nested', [('email', {'placeholder': _("Enter your e-mail"), 'width': 50}), ('email_rep', {'placeholder': _("Repeat your e-mail"), 'width': 50})]), 
                      ('nested', [('password', {'has_value': False, 'placeholder': _("Enter your password"), 'width': 50}), ('password_rep', {'has_value': False, 'placeholder': _("Repeat your password"), 'width': 50})])]
                 ),
                 (
                     None,
                     ['captcha_qa', 'recaptcha']
                 ),
                 (
                     None,
                     [('accept_tos', {'inline': _("I have read and accept this forums Terms of Service.")})]
                 ),
             ]
    
    class Meta:
        widgets = {
            'password': forms.PasswordInput(),
            'password_rep': forms.PasswordInput(),
        }
        
    def clean_username(self):
        new_user = User.objects.get_blank_user()
        new_user.set_username(self.cleaned_data['username'])
        try:
            new_user.full_clean()
        except ValidationError as e:
            new_user.is_username_valid(e)
        return self.cleaned_data['username']
        
    def clean_email(self):
        new_user = User.objects.get_blank_user()
        new_user.set_email(self.cleaned_data['email'])
        try:
            new_user.full_clean()
        except ValidationError as e:
            new_user.is_email_valid(e)
        return self.cleaned_data['email']
        
    def clean_password(self):
        new_user = User.objects.get_blank_user()
        new_user.set_password(self.cleaned_data['password'])
        try:
            new_user.full_clean()
        except ValidationError as e:
            new_user.is_password_valid(e)
        validate_password(self.cleaned_data['password'])
        return self.cleaned_data['password']
    
    
class UserSendSpecialMailForm(Form):
    email = forms.EmailField(max_length=255,label=_("Your E-mail Address"),help_text=_("Your account's email address."))
    captcha_qa = captcha.QACaptchaField()
    recaptcha = captcha.ReCaptchaField()
    error_source = 'email'
    
    layout = [
                  (
                      None,
                      [('email', {'placeholder': _("Enter your e-mail address.")})]
                  ),
                  (
                      None,
                      ['captcha_qa', 'recaptcha']
                  ),
             ]
    
    def clean_email(self):
        try:
            email = self.cleaned_data['email'].lower()
            email_hash = hashlib.md5(email).hexdigest()
            self.found_user = User.objects.get(email_hash=email_hash)
        except User.DoesNotExist:
            raise ValidationError(_("There is no user with such e-mail address."))
        return email
    