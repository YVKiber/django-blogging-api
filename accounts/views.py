from operator import pos

from django.contrib.auth.models import User

from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from blog.models import Bookmark, Post, Comment, Like
from blog.serializers import BookmarkSerializer, PostSerializer
from .models import UserProfile
from .serializers import RegisterSerializer, UserSerializer, ChangePasswordSerializer, UserProfileSerializer, \
    UserDashboardSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = request.user
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']

        if not user.check_password(old_password):
            return Response({'error': 'Wrong old password'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response( {"detail": "Password changed successfully."}, status=status.HTTP_200_OK)

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(
            user=self.request.user
        )
        return profile

class CurrentUserBookmarksView(generics.ListAPIView):
    serializer_class = BookmarkSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Bookmark.objects.filter(
            user=self.request.user
        ).select_related(
            "post",
            "post__author",
            "post__category",
        )

class CurrentUserPostsView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(
            author=self.request.user
        ).order_by("-created_at")

class CurrentUserDraftsView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(
            author=self.request.user,
            is_published=False
        ).order_by("-created_at")

class CurrentUserDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        posts_count = Post.objects.filter(
            author=user
        ).count()

        published_posts_count = Post.objects.filter(
            author=user,
            is_published=True
        ).count()

        drafts_count = Post.objects.filter(
            author=user,
            is_published=False
        ).count()

        comments_count = Comment.objects.filter(
            author=user
        ).count()

        likes_given_count = Like.objects.filter(
            user=user
        ).count()

        likes_received_count = Like.objects.filter(
            post__author=user,
        ).count()

        bookmarks_count = Bookmark.objects.filter(
            user=user
        ).count()

        data = {
            "posts_count": posts_count,
            "published_posts_count": published_posts_count,
            "drafts_count": drafts_count,
            "comments_count": comments_count,
            "likes_given_count": likes_given_count,
            "likes_received_count": likes_received_count,
            "bookmarks_count": bookmarks_count,
        }

        serializer = UserDashboardSerializer(data)

        return Response(serializer.data)

class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            {
                "detail": "If an account with this email exists, a password reset email has been sent."
            },
            status=status.HTTP_200_OK,
        )

class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            {
                "detail": "Password has been reset successfully."
            },
            status=status.HTTP_200_OK,
        )