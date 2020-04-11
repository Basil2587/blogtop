from django.test import TestCase, Client, override_settings
from .models import Post, User, Group
from django.conf import settings
from django.core.cache import cache
import tempfile
from django.core.files.images import ImageFile
from PIL import Image


class SimpleTestCase(TestCase):
    test_post = 'Тестовый текст для моего проекта'
    new_post = 'Создали новый пост для ника testname'
    edit_post = 'Тестовый текст для моего проекта, новоя редакция.'
    
    def setUp(self):
        self.client = Client()
                # создаём пользователя
        self.user = User.objects.create_user(
                        username="testname", email="myname@test.com", password="12345678"
                )
        self.client.force_login(self.user)
        self.group = Group.objects.create(title="king12", slug="lion")
        self.post = Post.objects.create(author=self.user, text= self.test_post)

    def test_profile(self):
        response = self.client.get("/testname/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
    
    @override_settings(CACHES=settings.TEST_CACHES)
    def test_authorization_post(self):
        response = self.client.get('/')
        self.assertContains(response, self.test_post)

    def test_not_authorization(self):
        self.client.logout()
        response = self.client.get('/new/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/auth/login/?next=/new/')

    @override_settings(CACHES=settings.TEST_CACHES)
    def test_create_post(self):
        self.client.post("/new/", {"text": self.new_post})
        response = self.client.get('/')
        self.assertContains(response, self.new_post)
        response = self.client.get("/testname/")
        self.assertContains(response, self.new_post)
        posts = Post.objects.get(author=self.user, text= self.new_post)
        response = self.client.get(f'/testname/{posts.id}/')
        self.assertContains(response, self.new_post)

    @override_settings(CACHES=settings.TEST_CACHES)
    def test_edit_post(self):
        self.client.post(f'/testname/{self.post.id}/edit/', {"text": self.edit_post})
        response = self.client.get("/testname/")
        self.assertContains(response, self.edit_post)  
        response = self.client.get(f'/testname/{self.post.id}/')
        self.assertContains(response, self.edit_post) 
        response = self.client.get("/")
        self.assertContains(response, self.edit_post)

    def test_404(self):
        response = self.client.get("/name/1000/")
        self.assertEqual(response.status_code, 404)

    def test_IMG_Tag_On_Page(self):
        # Создаю временную картинку и проверяю, что ее могу вставить в пост.
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            image = Image.new('RGB', (350, 200), 'green')
            image.save(f, 'PNG')
        with open(f.name, mode='rb') as img:
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
        with open('tmp/01.txt','rb') as im:
            self.client.post("/new/", {'text': 'post with txt', 'image': im})
        response = self.client.get(f'/')
        self.assertNotContains(response, 'post with txt') 

    def test_cash(self):
        self.client.post("/new/", {"text":'Текст который появляется после 20 секунд'}, follow=True)
        response = self.client.get("/")
        self.assertNotContains(response, 'Текст который появляется после 20 секунд')
        cache.clear() 
        response = self.client.get("/")
        self.assertContains(response, 'Текст который появляется после 20 секунд')
    
    def tearDown(self):
        print('Excellent')


class Follower_TestCase(TestCase):
    text_post1= "Здесь пост первого юзера"

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
        self.client.post("/new/", {"text": self.text_post1})
        self.client.logout()
        self.client.force_login(self.user_2)
        self.client.get(f'/testname_1/follow')
        #Авторизованный пользователь подписался на self.user_1 и видет его посты
        response = self.client.get("/follow/")
        self.assertContains(response,  self.text_post1)
        self.client.logout()
        self.client.force_login(self.user_3)
        response = self.client.get("/follow/")
        self.assertNotContains(response, self.text_post1)
        self.client.logout()
        self.client.force_login(self.user_2)
        self.client.get(f'/testname_1/unfollow')
        response = self.client.get("/follow/")
        self.assertNotContains(response, self.text_post1)

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
        posts = Post.objects.get(author=self.user_2)
        self.client.post(f'/{self.user_2.username}/{posts.id}/comment/', {"text": comment_text})
        response = self.client.get(f'/{self.user_2.username}/{posts.id}/')
        self.assertContains(response, comment_text)
