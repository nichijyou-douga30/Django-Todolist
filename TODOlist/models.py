from django.db import models

# Create your models here.
class Todo(models.Model):
    Todo_theme = models.CharField(max_length=200)
    Todo_text = models.TextField()
    pub_date = models.DateTimeField('date published', auto_now=True)
    Edit_flag = models.BooleanField(default=True)
    def __str__(self):
        return self.Todo_theme