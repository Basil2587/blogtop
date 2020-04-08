from django.contrib import admin
# из файла models импортируем модель Post
from .models import Post, Group, Comment

class PostAdmin(admin.ModelAdmin):
    # перечисляем поля, которые должны отображаться в админке
    list_display = ("pk", "text", "pub_date", "author") 
    # добавляем интерфейс для поиска по тексту постов
    search_fields = ("text",) 
    # добавляем возможность фильтрации по дате
    list_filter = ("pub_date",) 
    empty_value_display = '-пусто-' # это свойство сработает для всех колонок: где пусто - там будет эта строка
# при регистрации модели Post источником конфигурации для неё назначаем класс PostAdmin
admin.site.register(Post, PostAdmin)

class GroupAdmin(admin.ModelAdmin):
    # перечисляем поля, которые должны отображаться в админке
    list_display = ("pk", "title", "description")
    # добавляем интерфейс для поиска по тексту постов
    search_fields = ("text",)
    # добавляем возможность фильтрации по дате
    list_filter = ("title",)
    empty_value_display = '-пусто-'
admin.site.register(Group, GroupAdmin) 

class CommentAdmin(admin.ModelAdmin):  
    list_display = ('author', 'text', 'created', 'post')  
    list_filter = ('created', 'author',)  
    search_fields = ("text",)
admin.site.register(Comment, CommentAdmin)