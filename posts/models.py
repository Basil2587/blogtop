from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()

class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, null=False)
    description = models.TextField()
    
    def __str__(self):
        return self.title 

class Post(models.Model):
    text = models.TextField(u'Текст поста')
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True, db_index=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post_author")
    group = models.ForeignKey(Group, blank=True, null=True, verbose_name=(u'Группа'), on_delete=models.CASCADE)  
        # поле для картинки
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    def __str__(self):
       # выводим текст поста 
        return self.text  


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments',on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment_author")
    text = models.TextField(u'Комментарий')
    created = models.DateTimeField(u'Дата комментария', auto_now_add=True)

    def __str__(self):
        return self.text  


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower") #ссылка на объект пользователя, который подписывается
    author = models.ForeignKey(User, on_delete=models.CASCADE,related_name="following")

    def __str__(self):
        return f'follower - {self.user} following - {self.author}'