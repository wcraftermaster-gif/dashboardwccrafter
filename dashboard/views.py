from django.contrib import messages
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView

from blog.models import Post, Category, Tag
from .decorators import staff_required, superuser_required
from .forms import PostForm, CategoryForm, TagForm, UserCreateForm, UserUpdateForm, ProfileForm

User = get_user_model()


# --- Mixins de permisos ---

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


# --- Utilidad compartida para registrar acciones en LogEntry ---

def log_dashboard_action(request, instance, action_flag, change_message=''):
    """
    Registra una accion (crear/editar/eliminar) en el LogEntry nativo de Django,
    el mismo historial que usa el admin. Usada por vistas basadas en funcion
    (category_list, tag_list); las vistas basadas en clase usan DashboardLogMixin.
    """
    LogEntry.objects.create(
        user_id=request.user.pk,
        content_type_id=ContentType.objects.get_for_model(instance).pk,
        object_id=str(instance.pk),
        object_repr=str(instance)[:200],
        action_flag=action_flag,
        change_message=change_message,
    )


# --- Mixin para registrar acciones del dashboard en LogEntry (vistas basadas en clase) ---

class DashboardLogMixin:
    """
    Registra automáticamente las acciones del dashboard en LogEntry
    usando .create() para máxima compatibilidad con Django.
    """
    action_flag = None  # ADDITION, CHANGE, DELETION

    def log_action(self, instance, action_flag, change_message=''):
        log_dashboard_action(self.request, instance, action_flag, change_message)

    def form_valid(self, form):
        response = super().form_valid(form)
        self.log_action(self.object, self.action_flag)
        return response

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.log_action(self.object, DELETION)
        return super().delete(request, *args, **kwargs)


# --- Dashboard Home ---

class DashboardHomeView(StaffRequiredMixin, TemplateView):
    template_name = 'dashboard/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Estadísticas de posts
        context['total_posts'] = Post.objects.count()
        context['published_count'] = Post.objects.filter(status=Post.Status.PUBLISHED).count()
        context['draft_count'] = Post.objects.filter(status=Post.Status.DRAFT).count()
        context['scheduled_count'] = Post.objects.filter(status=Post.Status.SCHEDULED).count()

        # Posts recientes
        context['recent_posts'] = Post.objects.select_related(
            'author', 'category'
        ).order_by('-created_at')[:5]

        # Logs de Django Admin + Dashboard (acciones recientes)
        context['admin_logs'] = LogEntry.objects.select_related(
            'user', 'content_type'
        ).order_by('-action_time')[:5]

        # Logs de Axes: accesos correctos (AccessLog) y fallidos (AccessAttempt)
        try:
            from axes.models import AccessLog, AccessAttempt
            context['axes_logs'] = AccessLog.objects.order_by('-attempt_time')[:5]
            context['axes_failed'] = AccessAttempt.objects.order_by('-attempt_time')[:5]
        except ImportError:
            context['axes_logs'] = []
            context['axes_failed'] = []

        from django.utils import timezone

        context['upcoming_scheduled'] = Post.objects.filter(
            status=Post.Status.SCHEDULED,
            scheduled_at__gte=timezone.now()
        ).order_by('scheduled_at')[:5]

        return context


# --- Posts ---

class DashboardPostListView(StaffRequiredMixin, ListView):
    model = Post
    template_name = 'dashboard/posts/post_list.html'
    context_object_name = 'posts'
    paginate_by = 20

    def get_queryset(self):
        return Post.objects.select_related('author', 'category').order_by('-created_at')


class DashboardPostCreateView(DashboardLogMixin, StaffRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'dashboard/posts/post_form.html'
    success_url = reverse_lazy('dashboard:post_list')
    action_flag = ADDITION

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class DashboardPostUpdateView(DashboardLogMixin, StaffRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'dashboard/posts/post_form.html'
    success_url = reverse_lazy('dashboard:post_list')
    action_flag = CHANGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class DashboardPostDeleteView(DashboardLogMixin, StaffRequiredMixin, DeleteView):
    model = Post
    template_name = 'dashboard/posts/post_confirm_delete.html'
    success_url = reverse_lazy('dashboard:post_list')
    action_flag = DELETION


# --- Categorías ---

@staff_required
def category_list(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            instance = form.save()
            log_dashboard_action(request, instance, ADDITION)
            messages.success(request, 'Categoría creada correctamente.')
            return redirect('dashboard:category_list')
    else:
        form = CategoryForm()

    categories = Category.objects.annotate(post_count=Count('posts')).order_by('name')
    return render(request, 'dashboard/categories/category_list.html', {
        'form': form,
        'categories': categories,
    })


class CategoryUpdateView(DashboardLogMixin, StaffRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'dashboard/categories/category_form.html'
    success_url = reverse_lazy('dashboard:category_list')
    action_flag = CHANGE

    def form_valid(self, form):
        messages.success(self.request, 'Categoría actualizada.')
        return super().form_valid(form)


class CategoryDeleteView(DashboardLogMixin, StaffRequiredMixin, DeleteView):
    model = Category
    template_name = 'dashboard/categories/category_confirm_delete.html'
    success_url = reverse_lazy('dashboard:category_list')
    action_flag = DELETION


# --- Etiquetas ---

@staff_required
def tag_list(request):
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            instance = form.save()
            log_dashboard_action(request, instance, ADDITION)
            messages.success(request, 'Etiqueta creada correctamente.')
            return redirect('dashboard:tag_list')
    else:
        form = TagForm()

    tags = Tag.objects.annotate(post_count=Count('posts')).order_by('name')
    return render(request, 'dashboard/tags/tag_list.html', {
        'form': form,
        'tags': tags,
    })


class TagUpdateView(DashboardLogMixin, StaffRequiredMixin, UpdateView):
    model = Tag
    form_class = TagForm
    template_name = 'dashboard/tags/tag_form.html'
    success_url = reverse_lazy('dashboard:tag_list')
    action_flag = CHANGE

    def form_valid(self, form):
        messages.success(self.request, 'Etiqueta actualizada.')
        return super().form_valid(form)


class TagDeleteView(DashboardLogMixin, StaffRequiredMixin, DeleteView):
    model = Tag
    template_name = 'dashboard/tags/tag_confirm_delete.html'
    success_url = reverse_lazy('dashboard:tag_list')
    action_flag = DELETION


# --- Usuarios ---

class UserListView(SuperuserRequiredMixin, ListView):
    model = User
    template_name = 'dashboard/users/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        return User.objects.all().order_by('username').prefetch_related('groups')


class UserCreateView(DashboardLogMixin, SuperuserRequiredMixin, CreateView):
    model = User
    form_class = UserCreateForm
    template_name = 'dashboard/users/user_form.html'
    success_url = reverse_lazy('dashboard:user_list')
    action_flag = ADDITION

    def form_valid(self, form):
        messages.success(self.request, 'Usuario creado correctamente.')
        return super().form_valid(form)


class UserUpdateView(DashboardLogMixin, SuperuserRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'dashboard/users/user_form.html'
    success_url = reverse_lazy('dashboard:user_list')
    action_flag = CHANGE

    def form_valid(self, form):
        if form.instance.pk == self.request.user.pk:
            if (not form.cleaned_data.get('is_active')
                    or not form.cleaned_data.get('is_staff')
                    or not form.cleaned_data.get('is_superuser')):
                form.add_error(
                    None,
                    'No puedes quitarte a ti mismo el acceso de staff, superusuario, o desactivar tu cuenta.'
                )
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

        log_dashboard_action(
            request, user_obj, CHANGE,
            change_message=f'Usuario {"activado" if user_obj.is_active else "desactivado"}',
        )

        estado = 'activado' if user_obj.is_active else 'desactivado'
        messages.success(request, f'Usuario {estado} correctamente.')
    return redirect('dashboard:user_list')


# --- Perfil ---

class ProfileUpdateView(DashboardLogMixin, StaffRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'dashboard/users/user_profile.html'
    success_url = reverse_lazy('dashboard:profile')
    action_flag = CHANGE

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Perfil actualizado correctamente.')
        return super().form_valid(form)