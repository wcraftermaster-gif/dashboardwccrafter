from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=110, unique=True, blank=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class PublishedManager(models.Manager):
    """Devuelve solo posts visibles publicamente: publicados,
    o programados cuya fecha ya llego."""

    def get_queryset(self):
        now = timezone.now()
        return super().get_queryset().filter(
            models.Q(status=Post.Status.PUBLISHED) |
            models.Q(status=Post.Status.SCHEDULED, scheduled_at__lte=now)
        )


class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Borrador'
        SCHEDULED = 'scheduled', 'Programado'
        PUBLISHED = 'published', 'Publicado'
        ARCHIVED = 'archived', 'Archivado'

    # --- Contenido principal ---
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    excerpt = models.CharField(max_length=300, blank=True)
    content = CKEditor5Field(config_name='default')
    featured_image = models.ImageField(upload_to='blog/featured/%Y/%m/', blank=True, null=True)

    # --- Estado y fechas ---
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    scheduled_at = models.DateTimeField(null=True, blank=True, help_text='Fecha y hora de publicacion programada.')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    # --- SEO ---

    focus_keyword = models.CharField(
        max_length=100, blank=True,
        help_text='Frase clave principal para optimizar este contenido.'
    )

    meta_title = models.CharField(
        max_length=60, blank=True,
        help_text='Si se deja vacio, se usa el titulo del post. Recomendado: 50-60 caracteres.'
    )
    meta_description = models.CharField(
        max_length=160, blank=True,
        help_text='Descripcion para buscadores. Recomendado: 120-160 caracteres.'
    )
    canonical_url = models.URLField(blank=True, help_text='Solo si este contenido existe tambien en otra URL.')
    noindex = models.BooleanField(default=False, help_text='Marca para pedirle a buscadores que NO indexen este post.')

    objects = models.Manager()       # manager por defecto: todo, incluye borradores (para el dashboard/admin)
    published = PublishedManager()   # manager para el sitio publico

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.status == self.Status.PUBLISHED and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    @property
    def seo_title(self):
        return self.meta_title or self.title

    @property
    def seo_description(self):
        return self.meta_description or self.excerpt