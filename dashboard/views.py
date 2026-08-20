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

from django.contrib.auth import get_user_model
from .forms import UserCreateForm, UserUpdateForm
from .decorators import staff_required, superuser_required

User = get_user_model()

class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        raise PermissionDenied

class SuperuserRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

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

class UserListView(SuperuserRequiredMixin, ListView):
    model = User
    template_name = 'dashboard/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        return User.objects.all().order_by('username').prefetch_related('groups')


class UserCreateView(SuperuserRequiredMixin, CreateView):
    model = User
    form_class = UserCreateForm
    template_name = 'dashboard/user_form.html'
    success_url = reverse_lazy('dashboard:user_list')

    def form_valid(self, form):
        messages.success(self.request, 'Usuario creado correctamente.')
        return super().form_valid(form)


class UserUpdateView(SuperuserRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'dashboard/user_form.html'
    success_url = reverse_lazy('dashboard:user_list')

    def form_valid(self, form):
        if form.instance.pk == self.request.user.pk:
            if not form.cleaned_data.get('is_active') or not form.cleaned_data.get('is_staff'):
                form.add_error(None, 'No puedes desactivarte a ti mismo ni quitarte el acceso de staff.')
                return self.form_invalid(form)
        messages.success(self.request, 'Usuario actualizado.')
        return super().form_valid(form)


@superuser_required
def user_toggle_active(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    if user_obj.pk == request.user.pk:
        messages.error(request, 'No puedes desactivar tu propia cuenta.')
        return redirect('dashboard:user_list')
    if request.method == 'POST':
        user_obj.is_active = not user_obj.is_active
        user_obj.save(update_fields=['is_active'])
        estado = 'activado' if user_obj.is_active else 'desactivado'
        messages.success(request, f'Usuario {estado} correctamente.')
    return redirect('dashboard:user_list')