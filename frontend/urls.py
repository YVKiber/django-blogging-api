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
]