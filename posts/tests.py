from django.test import TestCase, Client
from .models import Post, User, Group, Comment
from users.forms import User
from django.core.files.images import ImageFile
from .forms import PostForm
import time


class SimpleTestCase(TestCase):
    def setUp(self):
        self.client = Client()
                # создаём пользователя
        self.user = User.objects.create_user(
                        username="testname", email="myname@test.com", password="12345678"
                )
        self.client.force_login(self.user)
        self.group = Group.objects.create(title="king12", slug="lion")

    def test_profile(self):
        response = self.client.get("/testname/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')

    def test_authorization_post(self):
        test_post = 'Создали новый пост для ника testname'
        self.client.post("/new/", {"text":test_post})
        time.sleep(20)
        response = self.client.get('/')
        self.assertContains(response, test_post)

    def test_not_authorization(self):
        self.client.logout()
        response = self.client.get('/new/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/auth/login/?next=/new/')

    def test_create_post(self):
        test_post = 'Создали новый пост для ника testname'
        self.client.post("/new/", {"text":test_post})
        response = self.client.get('/')
        self.assertContains(response, test_post)
        response = self.client.get("/testname/")
        self.assertContains(response, test_post)
        post = Post.objects.get(author=self.user)
        response = self.client.get(f'/testname/{post.id}/')
        self.assertContains(response, test_post)

    def test_edit_post(self):
        test_post = 'Здесь находится пост testname'
        self.client.post("/new/", {"text":test_post}, follow=True)
        post = Post.objects.get(author=self.user)
        test_2 = 'Здесь находится пост testname, новоя редакция.' 
        self.client.post(f'/testname/{post.id}/edit/', {"text":test_2}, follow=True)
        response = self.client.get("/testname/")
        self.assertContains(response, test_2)  
        response = self.client.get(f'/testname/{post.id}/')
        self.assertContains(response, test_2) 
        time.sleep(20)
        response = self.client.get("/")
        self.assertContains(response, test_2)

    def test_404(self):
        response = self.client.get("/name/1000/")
        self.assertEqual(response.status_code, 404)
        
    def tearDown(self):
        print('Excellent')

    def test_IMG_Tag_On_Page(self):
        with open('media/posts/fora.jpg','rb') as img:
            self.client.post("/new/", {'text': 'post with image', 'group': self.group.id, 'image': img})
        post = Post.objects.get(text='post with image')
        #print(post.id, post.image)
        response = self.client.get(f"/testname/")
        self.assertContains(response, 'img')
        response = self.client.get(f"/group/{self.group.slug}/")
        self.assertContains(response, 'img')
        response = self.client.get("/")
        self.assertContains(response, 'img')
        response = self.client.get(f"/testname/{post.id}/")
        self.assertContains(response, 'img')
        #print(response.content.decode('utf-8')) 

