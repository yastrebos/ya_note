from django.test import TestCase
import random
import string
from django.contrib.auth import get_user_model
from notes.models import Note
from django.urls import reverse

User = get_user_model()


def randomword(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


# так как NOTES_COUNT_ON_HOME_PAGE нет в settings
NOTES_COUNT_ON_HOME_PAGE = 10
# лист из уникальных slug.
RANDSLUG = []
while len(RANDSLUG) < NOTES_COUNT_ON_HOME_PAGE + 1:
    slug = randomword(10)
    if slug not in RANDSLUG:
        RANDSLUG.append(slug)


class TestContent(TestCase):
    LIST_URL = reverse('notes:list')
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев толстой')
        Note.objects.bulk_create(
            Note(
                #Добавляем для тестирования по алфавиту
                title=randomword(3) + f'Заметка {index}', 
                text='Просто текст.',
                slug=RANDSLUG[index],
                author=cls.author
            )
            for index in range(NOTES_COUNT_ON_HOME_PAGE + 1)
        )

    def test_notes_count(self):
        self.client.force_login(self.author)
        # Загружаем главную страницу.
        response = self.client.get(self.LIST_URL)
        # Код ответа не проверяем, его уже проверили в тестах маршрутов.
        # Получаем список объектов из словаря контекста.
        object_list = response.context['object_list']
        # Определяем длину списка.
        notes_count = len(object_list)
        # Проверяем, что на странице именно 10 новостей.
        self.assertEqual(notes_count, NOTES_COUNT_ON_HOME_PAGE) 

    def test_notes_order(self):
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        # Получаем даты новостей в том порядке, как они выведены на странице.
        all_titles = [notes.title for notes in object_list]
        # Сортируем полученный список по убыванию.
        sorted_titles = sorted(all_titles, reverse=False)
        # Проверяем, что исходный список был отсортирован правильно.
        self.assertEqual(all_titles, sorted_titles)  