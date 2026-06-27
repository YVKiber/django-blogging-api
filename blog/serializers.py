from rest_framework import serializers
from .models import Category, Post, Comment, Like, Bookmark


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]

class PostSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(
        source="author.username",
        read_only=True
    )
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    bookmarks_count = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "content",
            "author",
            "author_username",
            "category",
            "likes_count",
            "is_liked",
            "bookmarks_count",
            "is_bookmarked",
            "created_at",
            "updated_at",
            "is_published",
            "image",
        ]
        read_only_fields = ["author", "likes_count",
            "is_liked", "bookmarks_count",
            "is_bookmarked", "created_at", "updated_at"]

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get("request")

        if request is None or request.user.is_anonymous:
            return False

        return Like.objects.filter(user=request.user, post=obj).exists()

    def get_bookmarks_count(self, obj):
        return obj.bookmarks.count()

    def get_is_bookmarked(self, obj):
        request = self.context.get("request")

        if request is None or request.user.is_anonymous:
            return False

        return Bookmark.objects.filter(user=request.user, post=obj).exists()

class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(
        source="author.username",
        read_only=True
    )

    class Meta:
        model = Comment
        fields = [
            "id",
            "post",
            "author",
            "author_username",
            "text",
            "created_at",
        ]
        read_only_fields = ["author", "created_at"]

class BookmarkSerializer(serializers.ModelSerializer):
    post = PostSerializer(read_only=True)

    class Meta:
        model = Bookmark
        fields = [
            "id",
            "post",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "post",
            "created_at",
        ]