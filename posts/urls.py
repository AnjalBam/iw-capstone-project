from django.urls import path
from . import views

app_name = 'posts'
urlpatterns = [
    path('comment/list/', views.ListComments.as_view(), name='comment_list'),
    path('post/list/', views.ListPosts.as_view(), name='posts_list'),
    path('post/create/', views.CreatePost.as_view(), name='post_create'),
    path('post/<str:post_slug>/', views.CreatePost.as_view(),
         name='post_create'),
    path('post/<str:post_slug>/update/', views.CreatePost.as_view(),
         name='post_create'),
]