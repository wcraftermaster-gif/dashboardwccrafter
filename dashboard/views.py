from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView

from blog.models import Post, Category, Tag
from .decorators import staff_required
from .forms import PostForm, CategoryForm, TagForm


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        raise PermissionDenied


class DashboardHomeView(StaffRequiredMixin, TemplateView):
    template_name = 'dashboard/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_posts'] = Post.objects.count()
        context['published_count'] = Post.objects.filter(status=Post.Status.PUBLISHED).count()
        context['draft_count'] = Post.objects.filter(status=Post.Status.DRAFT).count()
        return context


class DashboardPostListView(StaffRequiredMixin, ListView):
    model = Post
    template_name = 'dashboard/post_list.html'
    context_object_name = 'posts'
    paginate_by = 20

    def get_queryset(self):
        return Post.objects.select_related('author', 'category').order_by('-created_at')


class DashboardPostCreateView(StaffRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'dashboard/post_form.html'
    success_url = reverse_lazy('dashboard:post_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class DashboardPostUpdateView(StaffRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'dashboard/post_form.html'
    success_url = reverse_lazy('dashboard:post_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class DashboardPostDeleteView(StaffRequiredMixin, DeleteView):
    model = Post
    template_name = 'dashboard/post_confirm_delete.html'
    success_url = reverse_lazy('dashboard:post_list')


# --- Categorias ---

@staff_required
def category_list(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría creada correctamente.')
            return redirect('dashboard:category_list')
    else:
        form = CategoryForm()

    categories = Category.objects.annotate(post_count=Count('posts')).order_by('name')
    return render(request, 'dashboard/category_list.html', {'form': form, 'categories': categories})


class CategoryUpdateView(StaffRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'dashboard/category_form.html'
    success_url = reverse_lazy('dashboard:category_list')

    def form_valid(self, form):
        messages.success(self.request, 'Categoría actualizada.')
        return super().form_valid(form)


class CategoryDeleteView(StaffRequiredMixin, DeleteView):
    model = Category
    template_name = 'dashboard/category_confirm_delete.html'
    success_url = reverse_lazy('dashboard:category_list')


# --- Etiquetas ---

@staff_required
def tag_list(request):
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Etiqueta creada correctamente.')
            return redirect('dashboard:tag_list')
    else:
        form = TagForm()

    tags = Tag.objects.annotate(post_count=Count('posts')).order_by('name')
    return render(request, 'dashboard/tag_list.html', {'form': form, 'tags': tags})


class TagUpdateView(StaffRequiredMixin, UpdateView):
    model = Tag
    form_class = TagForm
    template_name = 'dashboard/tag_form.html'
    success_url = reverse_lazy('dashboard:tag_list')

    def form_valid(self, form):
        messages.success(self.request, 'Etiqueta actualizada.')
        return super().form_valid(form)


class TagDeleteView(StaffRequiredMixin, DeleteView):
    model = Tag
    template_name = 'dashboard/tag_confirm_delete.html'
    success_url = reverse_lazy('dashboard:tag_list')