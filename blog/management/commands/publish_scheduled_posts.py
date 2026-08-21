from django.core.management.base import BaseCommand
from django.utils import timezone
from blog.models import Post


class Command(BaseCommand):
    help = "Publica automaticamente los posts programados cuya fecha ya llego."

    def handle(self, *args, **options):
        now = timezone.now()
        pending = Post.objects.filter(status=Post.Status.SCHEDULED, scheduled_at__lte=now)
        count = pending.count()

        for post in pending:
            post.status = Post.Status.PUBLISHED
            post.save()  # el save() del modelo ya asigna published_at automaticamente

        self.stdout.write(self.style.SUCCESS(f'{count} post(s) publicados.'))