from django.urls import path

from . import views

urlpatterns = [
    path("follow/", views.follow_index, name="follow_index"),
    path("<username>/follow", views.profile_follow, name="profile_follow"), 
    path("<username>/unfollow", views.profile_unfollow, name="profile_unfollow"),
    path("new/", views.post_new, name="new_post"),
    path("group/<slug:slug>/",views.group_posts, name="group"),
    # Профайл пользователя
    path("<username>/", views.profile, name="profile"),
    # Просмотр записи
    path("<username>/<int:post_id>/", views.post_view, name="post"),
    path("<username>/<int:post_id>/edit/", views.post_edit, name="post_edit"),
    path("<username>/<int:post_id>/comment/", views.add_comment, name="add_comment"),
    path("", views.index, name="index"),
]
