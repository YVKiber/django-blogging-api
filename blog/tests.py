from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Post, Category, Comment


class BlogAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="author",
            email="author@example.com",
            password="StrongPassword123!",
        )
        self.other_user = User.objects.create_user(
            username="other",
            email="other@example.com",
            password="StrongPassword123!",
        )
        self.category = Category.objects.create(
            name="Django"
        )
        self.post = Post.objects.create(
            title="Existing post",
            content="Existing post content",
            author=self.user,
            category=self.category,
            is_published=True,
        )

    def test_posts_list_is_public(self):
        response = self.client.get("/api/posts/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_user_cannot_create_post(self):
        response = self.client.post(
            "/api/posts/",
            {
                "title": "Anonymous post",
                "content": "This should not be created.",
                "category": self.category.id,
                "is_published": True,
            },
            format="json",
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )

    def test_authenticated_user_can_create_post(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            "/api/posts/",
            {
                "title": "Authenticated post",
                "content": "Created by authenticated user.",
                "category": self.category.id,
                "is_published": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Authenticated post")
        self.assertEqual(response.data["author"], self.user.id)

    def test_user_cannot_update_another_users_post(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.patch(
            f"/api/posts/{self.post.id}/",
            {
                "title": "Hacked title"
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Existing post")

    def test_author_can_update_own_post(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            f"/api/posts/{self.post.id}/",
            {
                "title": "Updated title"
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Updated title")

    def test_authenticated_user_can_create_comment(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.post(
            "/api/comments/",
            {
                "post": self.post.id,
                "text": "This is a test comment.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["post"], self.post.id)
        self.assertEqual(response.data["author"], self.other_user.id)

    def test_user_cannot_update_another_users_comment(self):
        comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            text="Original comment",
        )

        self.client.force_authenticate(user=self.other_user)

        response = self.client.patch(
            f"/api/comments/{comment.id}/",
            {
                "text": "Changed comment"
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        comment.refresh_from_db()
        self.assertEqual(comment.text, "Original comment")

    def test_posts_search(self):
        response = self.client.get("/api/posts/?search=Existing")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["count"], 1)

    def test_posts_filter_by_category(self):
        response = self.client.get(f"/api/posts/?category={self.category.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["count"], 1)