from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
import random
import string


# Импортируем из файла с формами список стоп-слов и предупреждение формы.
# Загляните в news/forms.py, разберитесь с их назначением.
# from news.forms import BAD_WORDS, WARNING
from notes.models import Note

User = get_user_model()

def randomword(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

class TestNoteCreation(TestCase):
    # Текст комментария понадобится в нескольких местах кода, 
    # поэтому запишем его в атрибуты класса.
    NOTE_TITLE = 'Заметка'
    NOTE_TEXT = 'Текст заметки'
    NOTE_SLUG = randomword(10)

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев толстой')
        cls.user = User.objects.create(username='Мимо Крокодил')
        # Адрес страницы с новостью.
        cls.url = reverse('notes:add')
        cls.url_done = reverse('notes:success')
        # Создаём пользователя и клиент, логинимся в клиенте.
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        # Данные для POST-запроса при создании комментария.
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'slug': cls.NOTE_SLUG
        }

    def test_anonymous_user_cant_create_note(self):
        # Совершаем запрос от анонимного клиента, в POST-запросе отправляем
        # предварительно подготовленные данные формы с текстом комментария.     
        self.client.post(self.url, data=self.form_data)
        # Считаем количество комментариев.
        notes_count = Note.objects.count()
        # Ожидаем, что комментариев в базе нет - сравниваем с нулём.
        self.assertEqual(notes_count, 0) 

    def test_user_can_create_note(self):
        # Совершаем запрос через авторизованный клиент.
        response = self.auth_client.post(self.url, data=self.form_data)
        # Проверяем, что редирект привёл к разделу с комментами.
        self.assertRedirects(response, f'{self.url_done}')
        # Считаем количество комментариев.
        notes_count = Note.objects.count()
        # Убеждаемся, что есть один комментарий.
        self.assertEqual(notes_count, 1)
        # Получаем объект комментария из базы.
        note = Note.objects.get()
        # Проверяем, что все атрибуты комментария совпадают с ожидаемыми.
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.slug, self.NOTE_SLUG)
        self.assertEqual(note.author, self.user) 


class TestNoteEditDelete(TestCase):
    # Тексты для комментариев не нужно дополнительно создавать 
    # (в отличие от объектов в БД), им не нужны ссылки на self или cls, 
    # поэтому их можно перечислить просто в атрибутах класса.
    NOTE_TITLE = 'Заметка'
    NEW_NOTE_TITLE = 'Новая аметка'
    NOTE_TEXT = 'Текст заметки'
    NEW_NOTE_TEXT = 'Новый текст заметки'
    NOTE_SLUG = randomword(10)
    NEW_NOTE_SLUG = randomword(10)
    
    @classmethod
    def setUpTestData(cls):
        # Создаём новость в БД.
        cls.author = User.objects.create(username='Автор комментария')
        cls.notes = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug=cls.NOTE_SLUG,
            author=cls.author
        )
        # Формируем адрес блока с комментариями, который понадобится для тестов.
        cls.url_done = reverse('notes:success')
        # Создаём пользователя - автора комментария.
        
        # Создаём клиент для пользователя-автора.
        cls.author_client = Client()
        # "Логиним" пользователя в клиенте.
        cls.author_client.force_login(cls.author)
        # Делаем всё то же самое для пользователя-читателя.
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        # URL для редактирования комментария.
        cls.edit_url = reverse(
            'notes:edit',
            kwargs={'slug': cls.notes.slug}
        )
        # URL для удаления комментария.
        cls.delete_url = reverse(
            'notes:delete',
            kwargs={'slug': cls.notes.slug}
        )
        # Формируем данные для POST-запроса по обновлению комментария.
        cls.form_data = {
            'title': cls.NEW_NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT,
            'slug': cls.NEW_NOTE_SLUG
        }
        
    def test_author_can_delete_note(self):
        # От имени автора комментария отправляем DELETE-запрос на удаление.
        response = self.author_client.delete(self.delete_url)
        # Проверяем, что редирект привёл к разделу с комментариями.
        # Заодно проверим статус-коды ответов.
        self.assertRedirects(response, self.url_done)
        # Считаем количество комментариев в системе.
        comments_count = Note.objects.count()
        # Ожидаем ноль комментариев в системе.
        self.assertEqual(comments_count, 0)
    
    def test_user_cant_delete_note_of_another_user(self):
        # Выполняем запрос на удаление от пользователя-читателя.
        response = self.reader_client.delete(self.delete_url)
        # Проверяем, что вернулась 404 ошибка.
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Убедимся, что комментарий по-прежнему на месте.
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        # Выполняем запрос на редактирование от имени автора комментария.
        response = self.author_client.post(self.edit_url, data=self.form_data)
        # Проверяем, что сработал редирект.
        self.assertRedirects(response, self.url_done)
        # Обновляем объект комментария.
        self.notes.refresh_from_db()
        # Проверяем, что текст комментария соответствует обновленному.
        self.assertEqual(self.notes.text, self.NEW_NOTE_TEXT)

    def test_user_cant_edit_comment_of_another_user(self):
        # Выполняем запрос на редактирование от имени другого пользователя.
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        # Проверяем, что вернулась 404 ошибка.
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Обновляем объект комментария.
        self.notes.refresh_from_db()
        # Проверяем, что текст остался тем же, что и был.
        self.assertEqual(self.notes.text, self.NOTE_TEXT) 
