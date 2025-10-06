from django.contrib import admin
from .models import Cliente
from django.utils.html import format_html

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'compania', 'identificacion', 'logo_tag')
    search_fields = ('nombre', 'compania', 'identificacion')

    def logo_tag(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="50" />', obj.logo.url)
        return '-'
    logo_tag.short_description = 'Logo'
