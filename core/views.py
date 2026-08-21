from django.views.generic import TemplateView
from blog.models import Post
import io
from django.conf import settings
from django.core.management import call_command
from django.http import JsonResponse, HttpResponseForbidden

class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_posts'] = Post.published.select_related('author', 'category')[:3]
        return context

def cron_publish_scheduled(request, token):
    if token != settings.CRON_SECRET:
        return HttpResponseForbidden('Token invalido.')

    output = io.StringIO()
    call_command('publish_scheduled_posts', stdout=output)
    return JsonResponse({'result': output.getvalue().strip()})