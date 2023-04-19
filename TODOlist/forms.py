from django import forms
from .models import Todo

class todoform(forms.Form):
    Todo_theme = forms.CharField(label= "テーマ")
    Todo_text = forms.CharField( label= '', widget=forms.Textarea(), required=True)
    # Todo_text = forms.Textarea(label= "内容")
    # pub_date = forms.DateTimeField(label="日時")

    def save(self):
        # save data using the self.cleaned_data dictionary
        data = self.cleaned_data
        post = Todo(Todo_theme=data['Todo_theme'], Todo_text=data['Todo_text'])
        post.save()    