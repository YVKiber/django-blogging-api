from rest_framework import serializers
from .models import Category, Post, Comment

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]

class PostSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(
        source="author.username",
        read_only=True
    )
    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "content",
            "author",
            "author_username",
            "category",
            "created_at",
            "updated_at",
            "is_published",
        ]
        read_only_fields = ["author", "created_at", "updated_at"]

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            "id",
            "post",
            "author_name",
            "text",
            "created_at",
        ]
        read_only_fields = ["created_at"]