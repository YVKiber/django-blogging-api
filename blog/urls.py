from email.policy import default

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, PostViewSet, CommentViewSet

router = DefaultRouter()
router.register('categories', CategoryViewSet)
router.register("posts", PostViewSet, basename="post")
router.register('comments', CommentViewSet)
urlpatterns = [
    path('', include(router.urls)),
]