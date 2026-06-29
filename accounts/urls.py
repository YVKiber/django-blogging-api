from django.urls import path

from .views import RegisterView, CurrentUserView, ChangePasswordView, UserProfileView, CurrentUserBookmarksView, \
    CurrentUserPostsView, CurrentUserDraftsView, CurrentUserDashboardView, PasswordResetRequestView, \
    PasswordResetConfirmView, EmailVerificationView, ResendEmailVerificationView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-email/',EmailVerificationView.as_view(), name='verify-email',),
    path('resend-verification/', ResendEmailVerificationView.as_view(), name='resend-verification',),
    path('me/', CurrentUserView.as_view(), name='current-user'),
    path('me/posts/', CurrentUserPostsView.as_view(), name='current-user-posts'),
    path('me/drafts/', CurrentUserDraftsView.as_view(), name='current-user-drafts'),
    path('me/dashboard/', CurrentUserDashboardView.as_view(), name='current-user-dashboard'),
    path('me/bookmarks/', CurrentUserBookmarksView.as_view(), name='current-user-bookmarks'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('password-reset/', PasswordResetRequestView.as_view(), name="password-reset",),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name="password-reset-confirm",),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
]