"""
This file is for functions that are supposed to generate something ... for example fill pipe Notes.
"""

import random

from .models import Note, Registry, Pipe, Manual, unique_slug_generator


NODES_ARRAY = [
    'C', 'Cis', 'D', 'Dis', 'E', 'F', 'Fis', 'G', 'Gis', 'A', 'Ais', 'H',
    'c', 'cis', 'd', 'dis', 'e', 'f', 'fis', 'g', 'gis', 'a', 'ais', 'h',
    'c1', 'cis1', 'd1', 'dis1', 'e1', 'f1', 'fis1', 'g1', 'gis1', 'a1', 'ais1', 'h1',
    'c2', 'cis2', 'd2', 'dis2', 'e2', 'f2', 'fis2', 'g2', 'gis2', 'a2', 'ais2', 'h2',
    'c3', 'cis3', 'd3', 'dis3', 'e3', 'f3', 'fis3', 'g3', 'gis3', 'a3', 'ais3', 'h3',
    'c4',   # 'cis1', 'd1', 'dis1', 'e1', 'f1', 'fis1', 'g1', 'gis1', 'a1', 'ais1', 'h1',
]

FIRST_MANUAL_ARRAY = [
    'H1', 'H2', 'H3', 'H4', 'H4b', 'H5', 'H6', 'H7', 'H8', 'H9', 'H10',
    'H11', 'H12', 'H13', 'H14', 'H15a', 'H15b', 'H15c', 'H15d', 'H15e', 'H15f',
    'H16a', 'H16b', 'H16c', 'H16d', 'H17a', 'H17b', 'H17c', 'H17d', 'H17e', 'H18', 'H19'
]


def generate_pipes():
    noteq = list(Note.objects.all())
    cattos = list(Registry.objects.all())
    manuals = list(Manual.objects.all())
    num = 1
    for manual in manuals:
        for cat in cattos:
            if random.randint(0, 10) >= 8:
                continue
            for note in noteq:
                Pipe.objects.create(
                    name=str("pistalka-" + cat.name + "-" + note.name),
                    slug=str("pistalka-" + cat.name + "-" + note.name + "-" + str(num)),
                    registry=cat,
                    note=note,
                    manual=manual,
                    price=random.randint(100, 40000)
                )
                num += 1


def generate_notes():
    for note in NODES_ARRAY:
        Note.objects.create(name=note, shortcut=note)


def generate_manuals():
    man = ['Manual1', 'Manual2', 'Manual3', 'Manual4', 'Manual5']
    for manual in man:
        Manual.objects.create(name=manual)


def generate_registries():
    for registry in FIRST_MANUAL_ARRAY:
        Registry.objects.create(name=registry, shortcut=registry)


def generate_file_like():
    array = [(0, 1_000), (1_000, 5_000), (5_000, 25_000), (25_000, 100_000), (100_000, 1_000_000)]
    for x in range(1, 6):
        manual = Manual.objects.create(name='Manual{}'.format(x))

        for registry in FIRST_MANUAL_ARRAY:
            if random.randint(0, 10) % 2 == 0:
                continue

            cat_obj, _ = Registry.objects.get_or_create(name=registry)
            manual.registries.add(cat_obj)
            for note in NODES_ARRAY:
                note_obj, _ = Note.objects.get_or_create(name=note)
                manual.notes.add(note_obj)
                min_price, max_price = array[random.randint(0, len(array) - 1)]
                if random.randint(0, 10) % 5 != 0:
                    Pipe.objects.create(name=str("pistalka-" + registry + "-" + note),
                                        registry=cat_obj,
                                        note=note_obj,
                                        manual=manual,
                                        price=random.randint(min_price, max_price)
                                        )


