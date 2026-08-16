from django import forms
from blog.models import Post, Category, Tag


INPUT_CLASSES = (
    'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 bg-white text-sm text-dark '
    'placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-500 '
    'focus:border-brand-500 transition-colors'
)


class PostForm(forms.ModelForm):
    category_name = forms.CharField(
        label='Categoría',
        required=False,
        widget=forms.TextInput(attrs={
            'class': INPUT_CLASSES,
            'list': 'category-options',
            'placeholder': 'Escribe o elige una categoría existente',
        }),
    )
    tags_input = forms.CharField(
        label='Etiquetas',
        required=False,
        widget=forms.TextInput(attrs={
            'class': INPUT_CLASSES,
            'placeholder': 'django, tutorial, seguridad',
        }),
        help_text='Sepáralas con comas. Las que no existan se crean automáticamente.',
    )

    class Meta:
        model = Post
        fields = [
            'title', 'excerpt', 'content',
            'featured_image', 'status', 'scheduled_at',
            'meta_title', 'meta_description', 'canonical_url', 'noindex',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'excerpt': forms.Textarea(attrs={'class': INPUT_CLASSES, 'rows': 3}),
            'content': forms.Textarea(attrs={'class': INPUT_CLASSES, 'rows': 12}),
            'featured_image': forms.ClearableFileInput(attrs={'class': 'text-sm text-gray-600'}),
            'status': forms.Select(attrs={'class': INPUT_CLASSES}),
            'scheduled_at': forms.DateTimeInput(attrs={'class': INPUT_CLASSES, 'type': 'datetime-local'}),
            'meta_title': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'meta_description': forms.Textarea(attrs={'class': INPUT_CLASSES, 'rows': 2}),
            'canonical_url': forms.URLInput(attrs={'class': INPUT_CLASSES}),
            'noindex': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 rounded border-gray-300 text-brand-500 focus:ring-brand-500'
            }),
        }

    field_order = [
        'title', 'category_name', 'tags_input', 'excerpt', 'content',
        'featured_image', 'status', 'scheduled_at',
        'meta_title', 'meta_description', 'canonical_url', 'noindex',
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            if self.instance.category:
                self.fields['category_name'].initial = self.instance.category.name
            self.fields['tags_input'].initial = ', '.join(
                t.name for t in self.instance.tags.all()
            )

    def save(self, commit=True):
        instance = super().save(commit=False)

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