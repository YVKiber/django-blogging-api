from django.urls import path

from .views import RegisterView, CurrentUserView, ChangePasswordView, UserProfileView, CurrentUserBookmarksView, \
    CurrentUserPostsView, CurrentUserDraftsView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", CurrentUserView.as_view(), name="current-user"),
    path("me/posts/", CurrentUserPostsView.as_view(), name="current-user-posts"),
    path("me/drafts/", CurrentUserDraftsView.as_view(), name="current-user-drafts"),
    path("me/bookmarks/", CurrentUserBookmarksView.as_view(), name="current-user-bookmarks"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("profile/", UserProfileView.as_view(), name="user-profile"),
]