import bleach
from django import forms
from django.utils.text import slugify
from blog.models import Post, Category, Tag


INPUT_CLASSES = (
    'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 bg-white text-sm text-dark '
    'placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-500 '
    'focus:border-brand-500 transition-colors'
)

ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 's', 'a', 'ul', 'ol', 'li',
    'blockquote', 'h2', 'h3', 'h4', 'img', 'figure', 'figcaption',
    'table', 'thead', 'tbody', 'tr', 'th', 'td', 'code', 'pre',
    'sub', 'sup', 'mark', 'span',
]
ALLOWED_ATTRS = {
    'a': ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'width', 'height', 'class', 'style'],
    'figure': ['class', 'style'],
    'span': ['style', 'class'],
    'td': ['style'],
    'th': ['style'],
}


def generate_unique_slug(instance, base_slug):
    slug = base_slug
    counter = 2
    while Post.objects.filter(slug=slug).exclude(pk=instance.pk).exists():
        slug = f'{base_slug}-{counter}'
        counter += 1
    return slug


class StyledClearableFileInput(forms.ClearableFileInput):
    template_name = 'dashboard/widgets/clearable_file_input.html'

class PostForm(forms.ModelForm):
    category_name = forms.CharField(
        label='Categoría',
        required=False,
        widget=forms.HiddenInput(attrs={'id': 'id_category_name'}),
    )
    tags_input = forms.CharField(
        label='Etiquetas',
        required=False,
        widget=forms.HiddenInput(attrs={'id': 'id_tags_input'}),
    )

    class Meta:
        model = Post
        fields = [
            'title', 'slug', 'excerpt', 'content',
            'featured_image', 'status', 'scheduled_at',
            'meta_title', 'meta_description', 'canonical_url', 'noindex',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full text-3xl font-semibold text-dark placeholder-gray-300 '
                         'border-none focus:outline-none focus:ring-0 p-0',
                'placeholder': 'Añadir título',
                'id': 'id_title',
            }),
            'slug': forms.TextInput(attrs={
                'class': 'px-2 py-1 rounded border border-gray-300 text-sm text-dark '
                         'focus:outline-none focus:ring-2 focus:ring-brand-500',
                'id': 'id_slug',
            }),
            'excerpt': forms.Textarea(attrs={'class': INPUT_CLASSES, 'rows': 3}),
            'featured_image': StyledClearableFileInput(attrs={'id': 'id_featured_image', 'class': 'hidden'}),
            'status': forms.Select(attrs={'class': INPUT_CLASSES}),
            'scheduled_at': forms.DateTimeInput(attrs={'class': INPUT_CLASSES, 'type': 'datetime-local'}),
            'meta_title': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'meta_description': forms.Textarea(attrs={'class': INPUT_CLASSES, 'rows': 2}),
            'canonical_url': forms.URLInput(attrs={'class': INPUT_CLASSES}),
            'noindex': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 rounded border-gray-300 text-brand-500 focus:ring-brand-500'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False
        if self.instance.pk:
            if self.instance.category:
                self.fields['category_name'].initial = self.instance.category.name
            self.fields['tags_input'].initial = ', '.join(
                t.name for t in self.instance.tags.all()
            )

    def save(self, commit=True):
        instance = super().save(commit=False)

        base_slug = slugify(instance.slug) if instance.slug else slugify(instance.title)
        instance.slug = generate_unique_slug(instance, base_slug)

        instance.content = bleach.clean(
            instance.content,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRS,
            strip=True,
        )

        category_name = self.cleaned_data.get('category_name', '').strip()
        if category_name:
            category, _ = Category.objects.get_or_create(
                name__iexact=category_name,
                defaults={'name': category_name},
            )
            instance.category = category
        else:
            instance.category = None

        if commit:
            instance.save()
            self._save_tags(instance)
        return instance

    def _save_tags(self, instance):
        raw = self.cleaned_data.get('tags_input', '')
        names = [n.strip() for n in raw.split(',') if n.strip()]
        tags = []
        for name in names:
            tag, _ = Tag.objects.get_or_create(name__iexact=name, defaults={'name': name})
            tags.append(tag)
        instance.tags.set(tags)



class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Nombre de la categoría'}),
        }


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Nombre de la etiqueta'}),
        }
