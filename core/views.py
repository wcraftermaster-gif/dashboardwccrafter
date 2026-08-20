from django.views.generic import TemplateView
from blog.models import Post


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_posts'] = Post.published.select_related('author', 'category')[:3]
        return context

