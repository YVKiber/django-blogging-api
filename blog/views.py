from argparse import Action

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response

from .models import Category, Post, Comment, Like, Bookmark
from .permissions import IsAuthorOrReadOnly
from .serializers import CategorySerializer, PostSerializer, CommentSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        'category',
        'is_published',
        'author'
    ]

    search_fields = [
        'title',
        'content',
        'author__username',
    ]

    ordering_fields = [
        'created_at',
        'updated_at',
        'title',
    ]

    ordering = ['-created_at',]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated],
    )
    def like(self, request, pk=None):
        post = self.get_object()

        like, created = Like.objects.get_or_create(user=request.user, post=post)

        if not created:
            return Response(
                {"detail": "You have already liked this post."},
                status=status.HTTP_200_OK
            )

        return Response(
            {"detail": "Post liked successfully."},
            status=status.HTTP_201_CREATED
        )

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated],
    )
    def unlike(self, request, pk=None):
        post = self.get_object()

        deleted_count, _ = Like.objects.filter(user=request.user, post=post).delete()

        if deleted_count == 0:
            return Response(
                {"detail": "You have not liked this post yet."},
                status=status.HTTP_200_OK
            )

        return Response(
            {"detail": "Post unliked successfully."},
            status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated],
    )
    def bookmark(self, request, pk=None):
        post = self.get_object()

        bookmark, created = Bookmark.objects.get_or_create(user=request.user, post=post)

        if not created:
            return Response(
                {"detail": "You have already bookmarked this post."},
                status=status.HTTP_200_OK
            )

        return Response(
            {"detail": "Post bookmarked successfully."},
            status=status.HTTP_201_CREATED
        )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated],
    )
    def unbookmark(self, request, pk=None):
        post = self.get_object()

        deleted_count, _ = Bookmark.objects.filter(user=request.user, post=post).delete()

        if deleted_count == 0:
            return Response(
                {"detail": "You have not bookmarked this post yet."},
                status=status.HTTP_200_OK
            )
        return Response(
            {"detail": "Post removed from bookmarks successfully."},
            status=status.HTTP_200_OK
        )

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('-created_at')
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)