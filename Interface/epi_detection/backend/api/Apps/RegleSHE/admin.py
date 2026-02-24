from django.contrib import admin
from .models import HSERule

@admin.register(HSERule)
class HSERuleAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'epi_type', 'is_active', 'zone']
    list_filter = ['is_active', 'epi_type', 'zone']
    search_fields = ['name', 'zone']
# Register your models here.
