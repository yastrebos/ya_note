from django.test import TestCase
from http import HTTPStatus
from django.urls import reverse
from notes.models import Note
from django.contrib.auth import get_user_model

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.author = User.objects.create(username='Лев толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.notes = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='dfdfgdfg',
            author=cls.author
        )

    def test_pages_availability(self):
        urls = (
            ('notes:home', None),
            ('notes:detail', {'slug': self.notes.slug}),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, kwargs in urls:
            with self.subTest(name=name):
                self.client.force_login(self.author)
                url = reverse(name, kwargs=kwargs)
                response = self.client.get(url)
                self.assertEqual(
                    response.status_code, HTTPStatus.OK,
                    msg=f'Страница {url} недоступна'
                )

    def test_availability_for_comment_edit_and_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            # Логиним пользователя в клиенте:
            self.client.force_login(user)
            # Для каждой пары "пользователь - ожидаемый ответ"
            # перебираем имена тестируемых страниц:
            for name in ('notes:edit', 'notes:delete'):  
                with self.subTest(user=user, name=name):        
                    url = reverse(name, kwargs={'slug': self.notes.slug})
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)
    
    def test_redirect_for_anonymous_client(self):
        # Сохраняем адрес страницы логина:
        login_url = reverse('users:login')
        # В цикле перебираем имена страниц, с которых ожидаем редирект:
        for name in ('notes:edit', 'notes:delete'):
            with self.subTest(name=name):
                # Получаем адрес страницы редактирования или удаления комментария:
                url = reverse(name, kwargs={'slug': self.notes.slug})
                # Получаем ожидаемый адрес страницы логина, 
                # на который будет перенаправлен пользователь.
                # Учитываем, что в адресе будет параметр next, в котором передаётся
                # адрес страницы, с которой пользователь был переадресован.
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                # Проверяем, что редирект приведёт именно на указанную ссылку.
                self.assertRedirects(response, redirect_url) 
