from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField

User = get_user_model()


class UserAdminCreationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email', 'full_name']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 is not None and password1 != password2:
            self.add_error("password_2", "Your passwords must match")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ['email', 'password', 'active', 'admin', 'full_name']

    def clean_password(self):
        return self.initial["password"]


class RegisterForm(forms.ModelForm):
    email = forms.EmailField(max_length=120, widget=forms.TextInput(attrs={
        'type': "email",
        'class': "form-control mb-3",
        'placeholder': "Enter email"
    }), label='')

    full_name = forms.CharField(max_length=120, widget=forms.TextInput(attrs={
        'type': "text",
        'class': "form-control mb-3",
        'placeholder': "Enter Full Name"
    }), label='')

    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'type': "password",
        'class': "form-control mb-3",
        'placeholder': "Password"
    }), label='')

    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'type': "password",
        'class': "form-control mb-3",
        'placeholder': "Confirm Password"
    }), label='')

    class Meta:
        model = User
        fields = ['email', 'full_name']

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")

        user_qs = User.objects.all().filter(email=email)
        if user_qs.exists():
            self.add_error("email", "Email already in use")

        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 is not None and password1 != password2:
            self.add_error("password2", "Your passwords must match")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        # user.active = False  # send conf. email
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=120, widget=forms.TextInput(attrs={
        'type': "text",
        'class': "form-control mb-3",
        'placeholder': "Enter email"
    }), label='')
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'type': "password",
        'class': "form-control mb-3",
        'placeholder': "Password"
    }), label='')

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        user_qs = User.objects.all().filter(email=email)
        if not user_qs.exists() or authenticate(username=email, password=password) is None:
            self.add_error("email", "User does not exist / password is wrong")
        return cleaned_data
