from django.test import TestCase, Client
from django.urls import reverse

import accounts.models
from pipes_shop.models import Manual, Note, Pipe, Registry
from pipes_shop.views import SingleManualTable, ManualInitialView
from accounts.models import User

from .models import Cart


class TestCart(TestCase):
    def setUp(self) -> None:
        self.tone = Note.objects.create(
            name='tone-c',
            shortcut='c'
        )
        self.registry = Registry.objects.create(
            name='Principal 16´',
            shortcut='princ-16'
        )
        self.manual = Manual.objects.create(
            name='Manual-1'
        )
        self.manual.registries.add(self.registry)
        self.manual.notes.add(self.tone)

        self.pipes = []

        for x in range(10):
            pipe1 = Pipe.objects.create(
                name=f"pipe={x}",
                registry=self.registry,
                note=self.tone,
                manual=self.manual,
                price=2000
            )
            self.pipes.append(pipe1)

        self.user = User.objects.create(
            email='test@test.com',
            full_name='Test Loozer',
        )

    from unittest.mock import patch

    def mocked_mail(self, context):
        pass

    @patch("accounts.models.User.send_email", mocked_mail)
    def test_cart_component(self):
        cart = Cart.objects.create(
            user=self.user
        )

        for x in range(1, 4):
            pipe = Pipe.objects.filter(name=f'pipe={x}').first()
            cart.pipes.add(pipe)

        self.assertEquals(cart.pipes.all().count(), 3)

        for pipe in cart.pipes.all():
            self.assertEquals(pipe.is_reserved, False)

        cart.reserve()
        cart.mark_reserved(None)

        for pipe in cart.pipes.all():
            self.assertEquals(pipe.is_reserved, True)

