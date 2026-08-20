from django.views.generic import TemplateView
from blog.models import Post
from django.http import JsonResponse


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_posts'] = Post.published.select_related('author', 'category')[:3]
        return context


def ping_view(request):
    """Endpoint para mantener despierto el servicio en Render"""
    return JsonResponse({"status": "OK"})