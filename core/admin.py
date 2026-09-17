from django.contrib import admin

from core.models.core import Category, Domain, Track, Camp
from core.models.notification import Notification


admin.site.register(Category)
admin.site.register(Track)
admin.site.register(Domain)
admin.site.register(Notification)

@admin.register(Camp)
class CampAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'is_active', 'get_students_count')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('title', 'description')
    
    filter_horizontal = ('students',)

    def get_students_count(self, obj):
        return obj.students.count()
    get_students_count.short_description = 'عدد الطلاب'