# news/tests/test_trial.py
from django.test import TestCase

# Импортируем модель, чтобы работать с ней в тестах.
from notes.models import Note
from django.contrib.auth import get_user_model
import unittest

User = get_user_model()


# Создаём тестовый класс с произвольным названием, наследуем его от TestCase.
class TestNotes(TestCase):
    TITLE = 'Заголовок новости'
    TEXT = 'Тестовый текст'

    # В методе класса setUpTestData создаём тестовые объекты.
    # Оборачиваем метод соответствующим декоратором.    
    @classmethod
    def setUpTestData(cls):
        # Стандартным методом Django ORM create() создаём объект класса.
        # Присваиваем объект атрибуту класса: назовём его news.
        cls.note = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            slug='dfdfgdfg',
            author=User.objects.create(username='user1',password='123321')
        )

    # Проверим, что объект действительно было создан.
    @unittest.skip('Пропускаем тестовый тест')
    def test_successful_creation(self):
        # При помощи обычного ORM-метода посчитаем количество записей в базе.
        notes_count = Note.objects.count()
        # Сравним полученное число с единицей.
        self.assertEqual(notes_count, 1) 
    @unittest.skip('Пропускаем тестовый тест')
    def test_title(self):
        # Сравним свойство объекта и ожидаемое значение.
        self.assertEqual(self.note.title, self.TITLE)  