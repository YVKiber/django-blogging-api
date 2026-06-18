from urllib import response

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

class AccountsAPITests(APITestCase):
    def test_user_registration(self):
        response = self.client.post(
            '/api/accounts/register/',
            {'username': 'testAPIUser',
             'email': 'testAPIUser@mail.com',
             'password': 'StrongPassword123!'},
        format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'testAPIUser')
        self.assertEqual(response.data['email'], 'testAPIUser@mail.com')
        self.assertNotIn('password', response.data)
        self.assertTrue(User.objects.filter(username='testAPIUser').exists())

    def test_user_registration_with_weak_password_fails(self):
        response = self.client.post(
            "/api/accounts/register/",
            {
                "username": "weakuserpassword",
                "email": "weakuserpassword@example.com",
                "password": "12345678",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_jwt_login(self):
        User.objects.create_user(
            username="testuserJWT",
            email="testuserJWT@example.com",
            password="StrongPassword123!",
        )

        response = self.client.post(
             "/api/token/",
            {
                "username": "testuserJWT",
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
        user = User.objects.create_user(
            username="testuserauthentication",
            email="testuserauthentication@example.com",
            password="StrongPassword123!",
        )

        self.client.force_authenticate(user=user)

        response = self.client.get("/api/accounts/me/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuserauthentication")
        self.assertEqual(response.data["email"], "testuserauthentication@example.com")

    def test_profile_endpoint_returns_authenticated_user_profile(self):
        user = User.objects.create_user(
            username="testuserprofile",
            email="testuserprofile@example.com",
            password="StrongPassword123!",
        )

        self.client.force_authenticate(user=user)

        response = self.client.get("/api/accounts/profile/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuserprofile")
        self.assertIn("bio", response.data)
        self.assertIn("location", response.data)

    def test_profile_update(self):
        user = User.objects.create_user(
            username="testuserprofileupdate",
            email="testuserprofileupdate@example.com",
            password="StrongPassword123!",
        )

        self.client.force_authenticate(user=user)

        response = self.client.patch(
            "/api/accounts/profile/",
            {
                "bio": "I am learning Django REST Framework.",
                "location": "Netherlands",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["bio"], "I am learning Django REST Framework.")
        self.assertEqual(response.data["location"], "Netherlands")