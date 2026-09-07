from django.shortcuts import render

from core.models import Category


def category_list(request):
    categories = Category.objects.prefetch_related('domains').all() 
    return render(request, 'core/category_list.html', {'categories': categories})

