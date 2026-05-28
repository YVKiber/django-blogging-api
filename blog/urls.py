from email.policy import default

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, PostViewSet, CommentViewSet

router = DefaultRouter()
router.register('category', CategoryViewSet)
router.register('post', PostViewSet)
router.register('comment', CommentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]