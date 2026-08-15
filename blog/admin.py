from django.contrib import admin
from .models import Post, Category, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'published_at', 'scheduled_at')
    list_filter = ('status', 'category', 'author', 'tags')
    search_fields = ('title', 'content', 'meta_title', 'meta_description')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('tags',)
    fieldsets = (
        ('Contenido', {
            'fields': ('title', 'slug', 'author', 'category', 'tags', 'excerpt', 'content', 'featured_image')
        }),
        ('Publicacion', {
            'fields': ('status', 'scheduled_at', 'published_at')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'canonical_url', 'noindex'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('published_at',)