from django.contrib import admin

from .models import Registry, Note, Pipe, Manual


class pipeAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'slug']

    class Meta:
        model = Pipe


class NoteAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'name']

    class Meta:
        model = Note


class RegistryAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'name']

    class Meta:
        model = Registry


class ManualAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'name']

    class Meta:
        model = Manual


admin.site.register(Pipe, pipeAdmin)
admin.site.register(Note, NoteAdmin)
admin.site.register(Registry, RegistryAdmin)
admin.site.register(Manual, ManualAdmin)
