from django.contrib import admin

from library.usuarios.models import Profile

# Register your models here.


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'city', 'state', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone', 'city')
    list_filter = ('state', 'created_at')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Usuário', {'fields': ('user',)}),
        ('Informações Pessoais', {'fields': ('bio', 'avatar', 'phone', 'birth_date')}),
        ('Endereço', {'fields': ('cep', 'address', 'city', 'state', 'country')}),
        ('Datas', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
