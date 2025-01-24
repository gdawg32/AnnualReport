from django.contrib import admin
from . models import *
# Register your models here.

admin.site.register(Course)
admin.site.register(Student1)
admin.site.register(Batch)
admin.site.register(AcademicRecord)
admin.site.register(Institution)

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('title', 'achievement_type', 'awarded_to', 'date_awarded')
    list_filter = ('achievement_type', 'date_awarded')
    search_fields = ('title', 'awarded_to')