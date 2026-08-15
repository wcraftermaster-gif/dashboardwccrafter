from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView

from blog.models import Post
from .forms import PostForm


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Exige sesion iniciada Y is_staff=True. Si falla login, redirige a login;
    si esta logueado pero no es staff, devuelve 403."""

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        from django.core.exceptions import PermissionDenied
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


class DashboardPostUpdateView(StaffRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'dashboard/post_form.html'
    success_url = reverse_lazy('dashboard:post_list')


class DashboardPostDeleteView(StaffRequiredMixin, DeleteView):
    model = Post
    template_name = 'dashboard/post_confirm_delete.html'
    success_url = reverse_lazy('dashboard:post_list')