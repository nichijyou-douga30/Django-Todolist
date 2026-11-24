from django.contrib import admin

from .models import Todo, TodoEditHistory


class TodoEditHistoryInline(admin.TabularInline):
    model = TodoEditHistory
    extra = 0
    can_delete = False
    readonly_fields = (
        'previous_theme',
        'previous_text',
        'new_theme',
        'new_text',
        'edited_at',
    )

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ('Todo_theme', 'is_edited', 'pub_date')
    inlines = [TodoEditHistoryInline]

    @admin.display(boolean=True, description='編集済み')
    def is_edited(self, obj):
        return obj.is_edited
