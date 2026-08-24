from django.contrib import admin

from .models import Category, Domain, Track


admin.site.register(Category)
admin.site.register(Track)
admin.site.register(Domain)