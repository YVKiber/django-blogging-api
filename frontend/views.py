import token
from multiprocessing import context

from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.tokens import default_token_generator
from django.db.migrations import serializer
from django.db.models import Q, Count
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, FormView, CreateView, UpdateView, DeleteView

from accounts.serializers import PasswordResetRequestSerializer, PasswordResetConfirmSerializer
from blog.models import Post, Category, Comment, Like, Bookmark
from frontend.forms import FrontendRegisterForm, FrontendPostForm, ResendVerificationForm, \
    PasswordResetRequestFrontendForm, PasswordResetConfirmFrontendForm

User = get_user_model()
class HomeView(TemplateView):
    template_name = "frontend/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['latest_posts'] = Post.objects.filter(
            is_published=True,
        ).select_related(
            'author',
            'category',
        ).annotate(
            likes_total=Count('likes'),
            comment_total=Count('comments'),
        ).order_by('-created_at')[:3]

        context['categories'] = Category.objects.all().order_by('name')[:6]

        context['posts_count'] = Post.objects.filter(
            is_published=True,
        ).count()

        context['categories_count'] = Category.objects.count()

        return context

class PostListPageView(ListView):
    model = Post
    template_name = "frontend/posts_list.html"
    context_object_name = "posts"
    paginate_by = 6

    def get_queryset(self):
        queryset = Post.objects.filter(
            is_published=True,
        ).select_related(
            'author',
            'category',
        ).annotate(
            likes_total=Count('likes'),
            comment_total=Count('comments'),
        ).order_by('-created_at')

        search_query = self.request.GET.get('q')
        category_id = self.request.GET.get('category')

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query)
                |Q(content__icontains=search_query)
                |Q(author__username__icontains=search_query)
            )

        if category_id:
            queryset = queryset.filter(
                category_id=category_id
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['categories'] = Category.objects.all().order_by('name')
        context['selected_category'] = self.request.GET.get('category', '')
        context['search_query'] = self.request.GET.get('q', '')

        return context

class PostDetailPageView(DetailView):
    model = Post
    template_name = "frontend/post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        return Post.objects.filter(
            is_published=True
        ).select_related(
            "author",
            "category",
        ).annotate(
            likes_total=Count("likes"),
            comments_total=Count("comments"),
            bookmarks_total=Count("bookmarks"),
        )

class FrontendLoginView(FormView):
    template_name = "frontend/login.html"
    form_class = AuthenticationForm
    success_url = reverse_lazy("frontend:dashboard")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("frontend:dashboard")

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs['request'] = self.request

        return kwargs

    def form_valid(self, form):
        user = form.get_user()

        login(self.request, user)

        messages.success(
            self.request,
            "You have been logged in successfully."
        )

        return super().form_valid(form)

class FrontendLogoutView(View):
    def post(self, request):
        logout(request)

        messages.success(
            self.request,
            "You have been logged out successfully."
        )

        return redirect("frontend:home")

class FrontendRegisterView(FormView):
    template_name = "frontend/register.html"
    form_class = FrontendRegisterForm
    success_url = reverse_lazy("frontend:login")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("frontend:dashboard")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request,
            "Registration successful. Please verify your email before logging in."
        )

        return super().form_valid(form)

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'frontend/dashboard.html'
    login_url = reverse_lazy('frontend:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user

        context['posts_count'] = Post.objects.filter(
            author=user
        ).count()

        context['published_posts_count'] = Post.objects.filter(
            author=user,
            is_published=True
        ).count()

        context['drafts_count'] = Post.objects.filter(
            author=user,
            is_published=False
        ).count()

        context['comments_count'] = Comment.objects.filter(
            author=user
        ).count()

        context['likes_given_count'] = Like.objects.filter(
            user=user
        ).count()

        context['likes_received_count'] = Like.objects.filter(
            post__author=user
        ).count()

        context['bookmarks_count'] = Bookmark.objects.filter(
            user=user
        ).count()

        context['recent_posts'] = Post.objects.filter(
            author=user
        ).select_related(
            'category'
        ).order_by('-created_at')[:5]

        return context

class MyPostsView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "frontend/my_posts.html"
    context_object_name = "posts"
    paginate_by = 6
    login_url = reverse_lazy('frontend:login')

    def get_queryset(self):
        return Post.objects.filter(
            author=self.request.user
        ).select_related(
            'category'
        ).annotate(
            likes_total=Count("likes"),
            comments_total=Count("comments"),
        ).order_by('-created_at')

class MyDraftsView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "frontend/my_drafts.html"
    context_object_name = "posts"
    paginate_by = 6
    login_url = reverse_lazy("frontend:login")

    def get_queryset(self):
        return Post.objects.filter(
            author=self.request.user,
            is_published=False,
        ).select_related(
            'category'
        ).annotate(
            likes_total=Count("likes"),
            comments_total=Count("comments"),
        ).order_by('-updated_at')

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = FrontendPostForm
    template_name = "frontend/post_form.html"
    login_url = reverse_lazy("frontend:login")

    def form_valid(self, form):
        form.instance.author = self.request.user

        messages.success(
            self.request,
            "Post has been created successfully."
        )

        return super().form_valid(form)

    def get_success_url(self):
        if self.object.is_published:
            return reverse(
                "frontend:post-detail",
                kwargs={
                    "pk": self.object.pk,
                }
            )

        return reverse("frontend:my-drafts")

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = FrontendPostForm
    template_name = "frontend/post_form.html"
    login_url = reverse_lazy("frontend:login")

    def get_queryset(self):
        return Post.objects.filter(
            author=self.request.user
        )

    def test_func(self):
        post = self.get_object()

        return post.author == self.request.user

    def get_success_url(self):
        if self.object.is_published:
            return reverse(
                "frontend:post-detail",
                kwargs={
                    "pk": self.object.pk,
                }
            )

        return reverse("frontend:my-drafts")

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = "frontend/post_confirm_delete.html"
    success_url = reverse_lazy("frontend:my-posts")
    login_url = reverse_lazy("frontend:login")

    def get_queryset(self):
        return Post.objects.filter(
            author=self.request.user
        )

    def test_func(self):
        post = self.get_object()

        return post.author == self.request.user

    def form_valid(self, form):
        messages.success(
            self.request,
            "Post has been deleted successfully."
        )

        return super().form_valid(form)

class PostPublishView(LoginRequiredMixin, View):
    def post(self,request, pk):
        post = get_object_or_404(
            Post,
            pk=pk,
            author=request.user,
        )
        post.is_published = True
        post.save(
            update_fields=[
                "is_published",
                "updated_at",
            ]
        )

        messages.success(
            request,
            "Post has been published successfully."
        )

        return redirect("frontend:my-posts")

class PostUnpublishView(LoginRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(
            Post,
            pk=pk,
            author=request.user,
        )

        post.is_published = False
        post.save(
            update_fields=[
                "is_published",
                "updated_at",
            ]
        )

        messages.success(
            request,
            "Post has been moved to drafts."
        )

        return redirect("frontend:my-drafts")

class VerifyEmailView(TemplateView):
        template_name = 'frontend/email_verification_result.html'

        def get(self, request, *args, **kwargs):
            uid = request.GET.get('uid')
            token = request.GET.get('token')

            if not uid or not token:
                return self.render_to_response(
                    self.get_context_data(
                        success=False,
                        title="Invalid verification link",
                        message="The verification link is missing required data.",
                    )
                )

            try:
                user_id = force_str(
                    urlsafe_base64_decode(uid)
                )

                user = User.objects.get(pk=user_id)

            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                return self.render_to_response(
                    self.get_context_data(
                        success=False,
                        title="Invalid verification link",
                        message="The verification link is invalid or broken.",
                    )
                )

            if user.is_active:
                return self.render_to_response(
                    self.get_context_data(
                        success=True,
                        title="Email already verified",
                        message="Your account has already been verified. You can log in.",
                    )
                )

            if not default_token_generator.check_token(user, token):
                return self.render_to_response(
                    self.get_context_data(
                        success=False,
                        title="Invalid or expired link",
                        message="This verification link is invalid or has expired. You can request a new one.",
                    )
                )

            user.is_active = True
            user.save(
                update_fields=['is_active']
            )

            return self.render_to_response(
                self.get_context_data(
                    success=True,
                    title="Email verified successfully",
                    message="Your email has been verified. You can now log in to your account.",
                )
            )

class ResendVerificationView(FormView):
    template_name = "frontend/resend_verification.html"
    form_class = ResendVerificationForm
    success_url = reverse_lazy("frontend:login")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("frontend:dashboard")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()

        messages.success(
            self.request,
            "If an unverified account with this email exists, a verification email has been sent."
        )

        return super().form_valid(form)

class PasswordResetRequestFrontendView(FormView):
    template_name = "frontend/password_reset.html"
    form_class = PasswordResetRequestFrontendForm
    success_url = reverse_lazy("frontend:login")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("frontend:dashboard")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        serializer = PasswordResetRequestSerializer(
            data = {
                "email": form.cleaned_data["email"],
            }
        )

        serializer.is_valid(raise_exception=True)

        serializer.save()

        messages.success(
            self.request,
            "If an account with this email exists, a password reset email has been sent."
        )

        return super().form_valid(form)

class PasswordResetConfirmFrontendView(FormView):
    template_name = "frontend/password_reset_confirm.html"
    form_class = PasswordResetConfirmFrontendForm
    success_url = reverse_lazy("frontend:login")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("frontend:dashboard")

        self.uid = self.request.GET.get('uid')
        self.token = self.request.GET.get('token')

        if not self.uid or not self.token:
            messages.error(
                request,
                "Invalid password reset link."
            )

            return redirect("frontend:password-reset")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        serializer = PasswordResetConfirmSerializer(
            data = {
                "uid": self.uid,
                "token": self.token,
                "new_password": form.cleaned_data["new_password"],
            }
        )
        if not serializer.is_valid():
            for error_list in serializer.errors.values():
                for error in error_list:
                    form.add_error(
                        None,
                        error
                    )

            return self.form_invalid(form)

        serializer.save()

        messages.success(
            self.request,
            "Your password has been reset successfully. You can now log in."
        )

        return super().form_valid(form)
