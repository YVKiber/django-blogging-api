from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import override_settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from blog.models import Category, Post, Bookmark, Like, Comment


class AccountsAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="StrongPassword123!",
        )

        self.other_user = User.objects.create_user(
            username="otheruser",
            email="otheruser@example.com",
            password="StrongPassword123!",
        )

        self.category = Category.objects.create(
            name="Django"
        )

        self.user_published_post = Post.objects.create(
            title="My published post",
            content="My published content.",
            author=self.user,
            category=self.category,
            is_published=True,
        )

        self.user_draft_post = Post.objects.create(
            title="My draft post",
            content="My draft content.",
            author=self.user,
            category=self.category,
            is_published=False,
        )

        self.other_user_published_post = Post.objects.create(
            title="Other user published post",
            content="Other user published content.",
            author=self.other_user,
            category=self.category,
            is_published=True,
        )

        self.other_user_draft_post = Post.objects.create(
            title="Other user draft post",
            content="Other user draft content.",
            author=self.other_user,
            category=self.category,
            is_published=False,
        )

    def get_response_items(self, response):
        if "results" in response.data:
            return response.data["results"]

        return response.data

    def test_user_registration(self):
        response = self.client.post(
            "/api/accounts/register/",
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "StrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["username"], "newuser")
        self.assertEqual(response.data["email"], "newuser@example.com")
        self.assertNotIn("password", response.data)
        self.assertTrue(
            User.objects.filter(username="newuser").exists()
        )
        user = User.objects.get(username="newuser")
        self.assertFalse(user.is_active)

    def test_user_registration_with_invalid_email_fails(self):
        response = self.client.post(
            "/api/accounts/register/",
            {
                "username": "invalidemailuser",
                "email": "not-an-email",
                "password": "StrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertFalse(
            User.objects.filter(username="invalidemailuser").exists()
        )

    def test_user_registration_with_weak_password_fails(self):
        response = self.client.post(
            "/api/accounts/register/",
            {
                "username": "weakuser",
                "email": "weakuser@example.com",
                "password": "12345678",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.assertFalse(
            User.objects.filter(username="weakuser").exists()
        )

    def test_jwt_login(self):
        response = self.client.post(
            "/api/token/",
            {
                "username": "testuser",
                "password": "StrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_current_user_endpoint_requires_authentication(self):
        response = self.client.get("/api/accounts/me/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_current_user_endpoint_returns_authenticated_user(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get("/api/accounts/me/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")
        self.assertEqual(response.data["email"], "testuser@example.com")

    def test_profile_endpoint_requires_authentication(self):
        response = self.client.get("/api/accounts/profile/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_endpoint_returns_authenticated_user_profile(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get("/api/accounts/profile/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")
        self.assertEqual(response.data["email"], "testuser@example.com")
        self.assertIn("bio", response.data)
        self.assertIn("location", response.data)

    def test_profile_update(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            "/api/accounts/profile/",
            {
                "bio": "I am learning Django REST Framework.",
                "location": "Netherlands",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["bio"],
            "I am learning Django REST Framework."
        )
        self.assertEqual(response.data["location"], "Netherlands")

    def test_current_user_bookmarks_endpoint_requires_authentication(self):
        response = self.client.get("/api/accounts/me/bookmarks/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_current_user_bookmarks_endpoint_returns_only_user_bookmarks(self):
        Bookmark.objects.create(
            user=self.user,
            post=self.other_user_published_post,
        )

        Bookmark.objects.create(
            user=self.other_user,
            post=self.user_published_post,
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.get("/api/accounts/me/bookmarks/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        bookmarks = self.get_response_items(response)

        returned_titles = [
            item["post"]["title"]
            for item in bookmarks
        ]

        self.assertIn("Other user published post", returned_titles)
        self.assertNotIn("My published post", returned_titles)

    def test_current_user_posts_endpoint_requires_authentication(self):
        response = self.client.get("/api/accounts/me/posts/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_current_user_posts_endpoint_returns_only_user_posts(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get("/api/accounts/me/posts/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        posts = self.get_response_items(response)

        returned_titles = [
            post["title"]
            for post in posts
        ]

        self.assertIn("My published post", returned_titles)
        self.assertIn("My draft post", returned_titles)
        self.assertNotIn("Other user published post", returned_titles)
        self.assertNotIn("Other user draft post", returned_titles)

    def test_current_user_drafts_endpoint_requires_authentication(self):
        response = self.client.get("/api/accounts/me/drafts/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_current_user_drafts_endpoint_returns_only_user_drafts(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get("/api/accounts/me/drafts/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        drafts = self.get_response_items(response)

        returned_titles = [
            post["title"]
            for post in drafts
        ]

        self.assertIn("My draft post", returned_titles)
        self.assertNotIn("My published post", returned_titles)
        self.assertNotIn("Other user published post", returned_titles)
        self.assertNotIn("Other user draft post", returned_titles)


    def test_current_user_dashboard_requires_authentication(self):
        response = self.client.get("/api/accounts/me/dashboard/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_current_user_dashboard_returns_correct_statistics(self):
        Comment.objects.create(
            post=self.other_user_published_post,
            author=self.user,
            text="This is my comment.",
        )

        Like.objects.create(
            user=self.user,
            post=self.other_user_published_post,
        )

        Like.objects.create(
            user=self.other_user,
            post=self.user_published_post,
        )

        Bookmark.objects.create(
            user=self.user,
            post=self.other_user_published_post,
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.get("/api/accounts/me/dashboard/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data["posts_count"], 2)
        self.assertEqual(response.data["published_posts_count"], 1)
        self.assertEqual(response.data["drafts_count"], 1)
        self.assertEqual(response.data["comments_count"], 1)
        self.assertEqual(response.data["likes_given_count"], 1)
        self.assertEqual(response.data["likes_received_count"], 1)
        self.assertEqual(response.data["bookmarks_count"], 1)

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        FRONTEND_BASE_URL="http://frontend.test",
    )
    def test_password_reset_request_sends_email_for_existing_user(self):
        response = self.client.post(
            "/api/accounts/password-reset/",
            {
                "email": "testuser@example.com",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Password reset request", mail.outbox[0].subject)
        self.assertIn("http://frontend.test/password-reset-confirm", mail.outbox[0].body)

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        FRONTEND_BASE_URL="http://frontend.test",
    )
    def test_password_reset_request_with_unknown_email_returns_ok(self):
        response = self.client.post(
            "/api/accounts/password-reset/",
            {
                "email": "unknown@example.com",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 0)
        self.assertIn("detail", response.data)

    def test_password_reset_confirm_changes_password(self):
        uid = urlsafe_base64_encode(
            force_bytes(self.user.pk)
        )

        token = default_token_generator.make_token(
            self.user
        )

        response = self.client.post(
            "/api/accounts/password-reset-confirm/",
            {
                "uid": uid,
                "token": token,
                "new_password": "NewStrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertTrue(
            self.user.check_password("NewStrongPassword123!")
        )

    def test_password_reset_confirm_with_invalid_token_fails(self):
        uid = urlsafe_base64_encode(
            force_bytes(self.user.pk)
        )

        response = self.client.post(
            "/api/accounts/password-reset-confirm/",
            {
                "uid": uid,
                "token": "invalid-token",
                "new_password": "NewStrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.user.refresh_from_db()
        self.assertTrue(
            self.user.check_password("StrongPassword123!")
        )

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        FRONTEND_BASE_URL="http://frontend.test",
    )
    def test_user_registration_sends_verification_email(self):
        response = self.client.post(
            "/api/accounts/register/",
            {
                "username": "emailverifyuser",
                "email": "emailverifyuser@example.com",
                "password": "StrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(
            username="emailverifyuser"
        )

        self.assertFalse(user.is_active)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Verify your email address", mail.outbox[0].subject)
        self.assertIn("http://frontend.test/verify-email", mail.outbox[0].body)

    def test_user_can_verify_email(self):
        inactive_user = User.objects.create_user(
            username="inactiveuser",
            email="inactiveuser@example.com",
            password="StrongPassword123!",
            is_active=False,
        )

        uid = urlsafe_base64_encode(
            force_bytes(str(inactive_user.pk))
        )

        token = default_token_generator.make_token(
            inactive_user
        )

        response = self.client.post(
        "/api/accounts/verify-email/",
        {
            "uid": uid,
            "token": token,
        },
        format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        inactive_user.refresh_from_db()
        self.assertTrue(inactive_user.is_active)

    def test_email_verification_with_invalid_token_fails(self):
        inactive_user = User.objects.create_user(
            username="inactiveuser",
            email="inactiveuser@example.com",
            password="StrongPassword123!",
            is_active=False,
        )

        uid = urlsafe_base64_encode(
            force_bytes(str(inactive_user.pk))
        )

        response = self.client.post(
            "/api/accounts/verify-email/",
            {
                "uid": uid,
                "token": "invalid-token",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        inactive_user.refresh_from_db()
        self.assertFalse(inactive_user.is_active)

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        FRONTEND_BASE_URL="http://frontend.test",
    )
    def test_resend_email_verification_sends_email_for_inactive_user(self):
        inactive_user = User.objects.create_user(
            username="inactiveuser",
            email="inactiveuser@example.com",
            password="StrongPassword123!",
            is_active=False,
        )

        response = self.client.post(
            "/api/accounts/resend-verification/",
            {
                "email": inactive_user.email,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Verify your email address", mail.outbox[0].subject)

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        FRONTEND_BASE_URL="http://frontend.test",
    )
    def test_resend_email_verification_for_active_user_does_not_send_email(self):
        response = self.client.post(
            "/api/accounts/resend-verification/",
            {
                "email": self.user.email,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 0)
