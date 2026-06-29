from multiprocessing import context

from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView
from django.db.models import Q, Count
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, FormView

from blog.models import Post, Category, Comment, Like, Bookmark
from frontend.forms import FrontendRegisterForm


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



