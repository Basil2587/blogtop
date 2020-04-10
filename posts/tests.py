from django.test import TestCase, Client, override_settings
from .models import Post, User, Group, Comment
from users.forms import User
from django.core.files.images import ImageFile
from .forms import PostForm, CommentForm
import time
from django.conf import settings


class SimpleTestCase(TestCase):
    def setUp(self):
        self.client = Client()
                # создаём пользователя
        self.user = User.objects.create_user(
                        username="testname", email="myname@test.com", password="12345678"
                )
        self.client.force_login(self.user)
        self.group = Group.objects.create(title="king12", slug="lion")
        self.post = Post.objects.create(author=self.user, text='Тестовый текст для моего проекта')

    def test_profile(self):
        response = self.client.get("/testname/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
    
    @override_settings(CACHES=settings.TEST_CACHES)
    def test_authorization_post(self):
        response = self.client.get('/')
        self.assertContains(response,"Тестовый текст для моего проекта")

    def test_not_authorization(self):
        self.client.logout()
        response = self.client.get('/new/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/auth/login/?next=/new/')

    @override_settings(CACHES=settings.TEST_CACHES)
    def test_create_post(self):
        self.client.post("/new/", {"text":'Создали новый пост для ника testname'})
        response = self.client.get('/')
        self.assertContains(response, 'Создали новый пост для ника testname')
        response = self.client.get("/testname/")
        self.assertContains(response, 'Создали новый пост для ника testname')
        posts = Post.objects.get(author=self.user, text='Создали новый пост для ника testname')
        response = self.client.get(f'/testname/{posts.id}/')
        self.assertContains(response, 'Создали новый пост для ника testname')

    @override_settings(CACHES=settings.TEST_CACHES)
    def test_edit_post(self):
        self.client.post(f'/testname/{self.post.id}/edit/', {"text":'Тестовый текст для моего проекта, новоя редакция.'}, follow=True)
        response = self.client.get("/testname/")
        self.assertContains(response, 'Тестовый текст для моего проекта, новоя редакция.')  
        response = self.client.get(f'/testname/{self.post.id}/')
        self.assertContains(response, 'Тестовый текст для моего проекта, новоя редакция.') 
        response = self.client.get("/")
        self.assertContains(response, 'Тестовый текст для моего проекта, новоя редакция.')

    def test_404(self):
        response = self.client.get("/name/1000/")
        self.assertEqual(response.status_code, 404)

    def test_IMG_Tag_On_Page(self):
        with open('media/posts/fora.jpg','rb') as img:
            self.client.post("/new/", {'text': 'Пост с картинкой', 'group': self.group.id, 'image': img})
        new = Post.objects.get(text='Пост с картинкой')
        response = self.client.get(f"/testname/")
        self.assertContains(response, 'img')
        response = self.client.get(f"/group/{self.group.slug}/")
        self.assertContains(response, 'img')
        response = self.client.get("/")
        self.assertContains(response, 'img')
        response = self.client.get(f"/testname/{new.id}/")
        self.assertContains(response, 'img')

    @override_settings(CACHES=settings.TEST_CACHES)
    def test_Not_IMG_Tag_On_Page(self):
       # Поверяем, что не загружается пост с текстом, если файл не являющийся картинкой
        with open('media/posts/01.txt','rb') as im:
            self.client.post("/new/", {'text': 'post with txt', 'image': im})
        response = self.client.get(f'/')
        self.assertNotContains(response, 'post with txt') 

    def test_cash(self):
        self.client.post("/new/", {"text":'Текст который появляется после 20 секунд'}, follow=True)
        response = self.client.get("/")
        self.assertNotContains(response, 'Текст который появляется после 20 секунд')
        time.sleep(20) 
        response = self.client.get("/")
        self.assertContains(response, 'Текст который появляется после 20 секунд')
    
    def tearDown(self):
        print('Excellent')


class Follower_TestCase(TestCase):
    def setUp(self):
        self.client = Client()
                # создаём пользователей
        self.user_1 = User.objects.create_user(
                        username="testname_1", email="myname1@test.com", password="12345678")
        self.user_2 = User.objects.create_user(
                        username="testname_2", email="myname2@test.com", password="12345678two")
        self.user_3 = User.objects.create_user(
                        username="testname_3", email="myname3@test.com", password="12345678three")

    def test_follower(self):
        self.client.force_login(self.user_1)
        self.client.post("/new/", {"text": "Здесь пост первого юзера"})
        self.client.logout()
        self.client.force_login(self.user_2)
        self.client.get(f'/testname_1/follow')
        #Авторизованный пользователь подписался на self.user_1 и видет его посты
        response = self.client.get("/follow/")
        self.assertContains(response, "Здесь пост первого юзера")
        self.client.logout()
        self.client.force_login(self.user_3)
        response = self.client.get("/follow/")
        self.assertNotContains(response, "Здесь пост первого юзера")
        self.client.logout()
        self.client.force_login(self.user_2)
        self.client.get(f'/testname_1/unfollow')
        response = self.client.get("/follow/")
        self.assertNotContains(response, "Здесь пост первого юзера")

    def test_notauth_user_follow(self):
        #Неавторизованный пользователь не может подписаться на self.user_1
        self.client.logout()
        response = self.client.get('/testname_1/follow', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/auth/login/?next=/testname_1/follow')
            
    def test_comment(self):
        #Авторизованный пользователь может оставить комментарий
        self.client.force_login(self.user_2)
        comment_text = 'Мой первый комментарий'
        self.client.post("/new/", {"text": "Текст поста второго юзера"})
        posts = Post.objects.get(author=self.user_2, text="Текст поста второго юзера")
        self.client.post(f'/{self.user_2.username}/{posts.id}/comment/', {"text": comment_text})
        response = self.client.get(f'/{self.user_2.username}/{posts.id}/')
        self.assertContains(response, comment_text)
