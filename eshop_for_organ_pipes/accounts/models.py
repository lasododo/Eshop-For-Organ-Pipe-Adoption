from django.db import models
from django.template.loader import get_template
from django.template import Context
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, full_name=None, password=None, is_staff=False, is_admin=False):
        print("hello")
        if not email:
            raise ValueError("User must have an email (blank is not an email)")

        if not password:
            raise ValueError("User does not have a correct password")

        user = self.model(
            email=self.normalize_email(email),
            full_name=full_name
        )
        user.set_password(password)  # changing is done the same way
        user.staff = is_staff
        user.admin = is_admin
        user.save()
        return user

    def create_staff_user(self, email, full_name=None, password=None):
        return self.create_user(email, full_name=full_name, password=password, is_staff=True)

    def create_superuser(self, email, full_name=None, password=None):
        return self.create_user(email, full_name=full_name, password=password, is_staff=True, is_admin=True)


class User(AbstractBaseUser):
    email = models.EmailField(unique=True, max_length=255, blank=False)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    active = models.BooleanField(default=True)  # can sign in
    staff = models.BooleanField(default=False)  # can do some magic
    admin = models.BooleanField(default=False)  # can do all magic
    timestamp = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    # email and password are required by default (password is in Abstract)
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    def send_email(self, context, fail_silence=False):
        html_template = get_template('accounts/email/generic-email-2.html')
        context['username'] = self.email
        # context['pipes'] = cart.pipes.all()

        subject, from_email, to = '[E-Shop] - Purchase Report', 'kekington144@gmail.com', self.email
        text_content = 'This is a test message.'
        html_content = html_template.render(context)
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=fail_silence)

    def get_full_name(self):
        if self.full_name is not None:
            return self.full_name + " ---- full name "
        return self.email

    def get_short_name(self):
        if self.full_name is not None:
            return self.full_name
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_active(self):
        return self.active


