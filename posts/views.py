from django.shortcuts import render, redirect, get_object_or_404
from .forms import PostForm, CommentForm
from .models import Post, Group, User, Comment, Follow
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.apps import apps
from django.db.models import Count


def index(request):
    post_list = Post.objects.order_by("-pub_date").all()
    paginator = Paginator(post_list, 5) # показывать по 10 записей на странице.
    page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number) # получить записи с нужным смещением
    return render(request, 'index.html', {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    # функция get_object_or_404 позволяет получить объект из базы данных 
    # по заданным критериям или вернуть сообщение об ошибке если объект не найден
    group = get_object_or_404(Group, slug=slug)
    # Метод .filter позволяет ограничить поиск по критериям. Это аналог добавления
    # условия WHERE group_id = {group_id}
    posts = Post.objects.filter(group=group).order_by("-pub_date").all()
    paginator = Paginator(posts, 12) # показывать по 12 записей на странице.
    page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"group": group, 'page': page, "paginator": paginator})


@login_required
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST or None, files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
    else:
        form = PostForm()
    return render(request, 'post_edit.html', {'form': form})


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    post_numbers = Post.objects.filter(author=profile).all().count()
    posts = Post.objects.filter(author=profile).order_by("-pub_date").all()
    paginator = Paginator(posts, 5) # показывать по 5 записей на странице.
    page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)
    if request.user.is_authenticated:
        following = Follow.objects.filter(user=request.user).filter(author=profile)
        if not following:
            following = None
        else:
            following = True
        context = {
            'following': following,
            'post_numbers': post_numbers,  
            "profile": profile, 
            'page': page, 
            "paginator": paginator,
            }
        return render(request, "profile.html", context)
    return render(request, "profile.html", {'post_numbers': post_numbers, "profile": profile,'page': page, "paginator": paginator})


def post_view(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    post_numbers = Post.objects.filter(author=profile).all().count()
    post = get_object_or_404(Post, id=post_id)
    items = Comment.objects.filter(post=post_id)
    form = CommentForm()
    return render(request, "post.html", {'form':form, 'items': items, 'post': post, 'post_numbers': post_numbers, "profile": profile})


@login_required
def post_edit(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author=profile)
    if request.user != profile:
        return redirect("post", username=request.user.username, post_id=post_id)
    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect("post", username=request.user.username, post_id=post_id)
    return render(request, "post_edit.html", {"form": form, "post": post})


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию, 
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):  
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect("post", username, post_id)
    else:
        form = CommentForm()
    return render(request,'comments.html', {'post': post, 'form':form})


@login_required
def follow_index(request):
    follows = Follow.objects.filter(user=request.user).values('author')
    following_list = Post.objects.filter(author_id__in=follows).order_by("-pub_date")
    paginator = Paginator(following_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {'page':page, 'paginator':paginator})

@login_required
def profile_follow(request, username):
    profile = get_object_or_404(User, username=username)
    following = Follow.objects.filter(user=request.user).filter(author=profile)
    if request.user != profile:
        if not following:
            Follow.objects.create(user=request.user, author=profile)
            return redirect ("profile", username) 
    return redirect ("profile", username) 

@login_required
def profile_unfollow(request, username):
    profile = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user).filter(author=profile).delete()
    return redirect ("profile", username)