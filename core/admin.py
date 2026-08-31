from django.contrib import admin

from .models import Category, Domain, Track, Camp


admin.site.register(Category)
admin.site.register(Track)
admin.site.register(Domain)

@admin.register(Camp)
class CampAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'is_active', 'get_students_count')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('title', 'description')
    
    # تحسين طريقة اختيار الطلاب (واجهة مربّعين سهلة للنقل بينهما)
    filter_horizontal = ('students',)

    def get_students_count(self, obj):
        return obj.students.count()
    get_students_count.short_description = 'عدد الطلاب'