from django.test import TestCase, Client
from django.urls import reverse
from .models import Manual, Note, Pipe, Registry
from .views import SingleManualTable, ManualInitialView

# Create your tests here.


class TestPipeShopModels(TestCase):

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

    def test_prerequisitories(self):
        self.assertEquals(self.tone.name, 'tone-c')
        self.assertEquals(self.tone.shortcut, 'c')
        self.assertEquals(self.registry.name, 'Principal 16´')
        self.assertEquals(self.registry.shortcut, 'princ-16')
        self.assertEquals(self.manual.name, 'Manual-1')
        self.assertEquals(self.manual.registries.all().count(), 1)
        self.assertEquals(self.manual.notes.all().count(), 1)
        self.assertEquals(self.manual.registries.all().first(), self.registry)
        self.assertEquals(self.manual.notes.all().first(), self.tone)

    def test_pipe_creation(self):
        name = 'Pipe-1'
        pipe1 = Pipe.objects.create(
            name=name,
            registry=self.registry,
            note=self.tone,
            manual=self.manual,
            price=2000
        )
        pipe2 = Pipe.objects.create(
            name=name,
            registry=self.registry,
            note=self.tone,
            manual=self.manual,
            price=2000
        )
        self.assertEquals(pipe1.name, pipe2.name)
        self.assertNotEquals(pipe1.slug, pipe2.slug)
        self.assertEquals(pipe1.registry, pipe2.registry)
        self.assertEquals(pipe1.note, pipe2.note)
        self.assertEquals(pipe1.manual, pipe2.manual)
        self.assertEquals(pipe1.price, pipe2.price)


class TestURLErrors(TestCase):

    def test_empty_list(self):
        client = Client()
        response = client.get(reverse('pipes_shop:list'))
        self.assertEquals(response.status_code, 200)

    def test_empty_manual(self):
        client = Client()
        response = client.get(reverse('pipes_shop:smt'))
        self.assertEquals(response.status_code, 404)


class TestURLS(TestCase):
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

        self.list_url = reverse('pipes_shop:smt')

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

    def test_non_empty_manual(self):
        client = Client()
        response = client.get(self.list_url)
        self.assertEquals(response.status_code, 200)

    def test_multiple_manuals(self):
        manual2 = Manual.objects.create(
            name='Manual-2'
        )
        manual2.registries.add(self.registry)
        manual2.notes.add(self.tone)

        for x in range(10):
            pipe1 = Pipe.objects.create(
                name=f"pipe={x}",
                registry=self.registry,
                note=self.tone,
                manual=manual2,
                price=2000
            )
            self.pipes.append(pipe1)

        client = Client()

        detail_url = reverse('pipes_shop:smt')
        response = client.get(detail_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, SingleManualTable.template_name)

        detail_url = reverse('pipes_shop:table', args=[self.manual.name])
        response = client.get(detail_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, ManualInitialView.template_name)

        detail_url = reverse('pipes_shop:table', args=[manual2.name])
        response = client.get(detail_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, ManualInitialView.template_name)

