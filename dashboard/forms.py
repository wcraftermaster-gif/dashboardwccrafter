from django import forms
from blog.models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'title', 'category', 'tags', 'excerpt', 'content',
            'featured_image', 'status', 'scheduled_at',
            'meta_title', 'meta_description', 'canonical_url', 'noindex',
        ]
        widgets = {
            'content': forms.Textarea(attrs={'rows': 12}),
            'excerpt': forms.Textarea(attrs={'rows': 3}),
        }