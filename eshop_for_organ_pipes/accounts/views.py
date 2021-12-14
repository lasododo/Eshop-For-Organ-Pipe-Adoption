from django.contrib.auth import authenticate, login, get_user_model
from django.core.exceptions import ValidationError
from django.views.generic import CreateView, FormView
from django.shortcuts import redirect
from django.utils.http import is_safe_url

from .forms import LoginForm, RegisterForm


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = '/login/'


class LoginView(FormView):
    form_class = LoginForm
    template_name = 'accounts/login.html'
    success_url = '/'

    def form_invalid(self, form, **kwargs):
        return super().form_invalid(form)

    def form_valid(self, form):
        request = self.request
        next_jump = request.GET.get('next')
        next_post_jump = request.POST.get('next')
        redirect_path = next_jump or next_post_jump or None
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        print(email, password)
        user = authenticate(username=email, password=password)
        print(user)
        if user is not None:
            login(request, user)
            if is_safe_url(redirect_path, request.get_host()):
                return redirect(redirect_path)
            return redirect("/")
        return super(LoginView, self).form_invalid(form)
