from django.urls import path
from . import views_main
from . import views_admin
from .views_main import UserPostList



urlpatterns = [

    path('blog/', views_main.blog_post, name='blog'),
    path('blog-detail/<int:post_id>/', views_main.blog_post, name='blog-detail'),
    path('search-post/', UserPostList.as_view(), name='post-list'),
    path('similar_blog/<int:category_id>/', views_main.similar_blog_view, name='similar_blog'),
    path('popular-blog/<int:pk>/', views_main.get_popular_post, name='popular-blog'),
    path('popular-blogs/', views_main.get_all_popular_posts, name='popular-blogs'),



    # ADMIN RELATED URLS
    path('create-post/', views_admin.create_post, name='create-post'),
    path('admin-all-post/', views_admin.get_all_posts, name='admin-all-post'),
    path('admin-post/<int:pk>/', views_admin.get_post_by_id, name='admin-all-post'),
    path('post-details/<int:pk>/', views_admin.update_post, name='post-details'),
    path('admin-popular-posts/', views_admin.manage_popular_posts, name='admin-popular-posts'),
    path('admin-popular-posts/<int:pk>/', views_admin.update_popular_post_status, name='admin-popular-posts'),
    path('admin_blog_category/', views_admin.admin_category, name='admin_blog_category'),
    
]
