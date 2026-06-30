from django import forms
from .models import Goal


class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ['title', 'emoji', 'category', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Add details...'}),
            'title': forms.TextInput(attrs={'placeholder': 'Enter goal...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].label = 'Goal Name'
        self.fields['emoji'].label = 'Emoji'
        self.fields['category'].label = 'Category'
        self.fields['description'].label = 'Description (optional)'