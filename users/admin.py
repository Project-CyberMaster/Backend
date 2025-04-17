from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser,Profile
from .forms import CustomUserCreationForm,CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
    add_form=CustomUserCreationForm
    form=CustomUserChangeForm
    model=CustomUser

    list_display=('email','username','red_team_percent','blue_team_percent')

    fieldsets = (
        (None,{'fields':('username','email','password')}),
        ("stats",{'fields':('red_team_percent','blue_team_percent')})
    )

    add_fieldsets = (
        (None,{
            'classes':('wide',),
            'fields':('username','email','password1','password2')
        }),
    )

    search_fields = ('email','username')
    ordering = ('username',)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'location', 'points', 'rank')
    search_fields = ('user__username', 'full_name', 'location')
    list_filter = ('rank',)
    
    
    raw_id_fields = ('user',)
    autocomplete_fields = ['user']
    
    fieldsets = (
        (None, {
            'fields': ('user', 'bio', 'profile_picture')
        }),
        ('Personal Info', {
            'fields': ('full_name', 'location')
        }),
        ('Social Media', {
            'fields': ('github', 'linkedin', 'twitter', 'facebook'),
            'classes': ('collapse',)
        }),
        ('Stats', {
            'fields': ('points', 'rank')
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin)