from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin

# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name','category','image')
    search_fields = ('product_name',)
    list_filter = ('category__name','tags__tag')
    ordering = ('product_name','category__name')

class CatAdmin(admin.ModelAdmin):
    list_display = ('id','name')
    search_fields = ('name',)

admin.site.register(Product,ProductAdmin)
admin.site.register(Categories,CatAdmin)
admin.site.register(Tags)
