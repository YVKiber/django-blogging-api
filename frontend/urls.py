from django.urls import path

from . import views


app_name = "frontend"


urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('posts/', views.PostListPageView.as_view(), name='posts-list'),
    path('posts/<int:pk>/', views.PostDetailPageView.as_view(), name='post-detail'),

    path('login/', views.FrontendLoginView.as_view(), name='login'),
    path('logout/', views.FrontendLogoutView.as_view(), name='logout'),
    path('register/', views.FrontendRegisterView.as_view(), name='register'),

    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),

    path('my-posts/', views.MyPostsView.as_view(), name='my-posts'),
    path('my-drafts/', views.MyDraftsView.as_view(), name='my-drafts'),

    path('posts/create/', views.PostCreateView.as_view(), name='post-create'),
    path('posts/<int:pk>/edit/', views.PostUpdateView.as_view(), name='post-edit'),
    path('posts/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post-delete'),

    path('posts/<int:pk>/publish/', views.PostPublishView.as_view(), name='post-publish'),
    path('posts/<int:pk>/unpublish/', views.PostUnpublishView.as_view(), name='post-unpublish'),
]