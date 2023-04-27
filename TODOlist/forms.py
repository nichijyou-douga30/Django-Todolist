from django import forms
from .models import Todo

class Todoform(forms.ModelForm):
    class Meta:
        model = Todo
        fields = ('Todo_theme', 'Todo_text')