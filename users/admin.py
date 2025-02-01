from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import CustomUserCreationForm,CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
    add_form=CustomUserCreationForm
    form=CustomUserChangeForm
    model=CustomUser

    list_display=('email','username','red_team_precent','blue_team_precent')

    fieldsets = (
        (None,{'fields':('username','email','password')}),
        ("stats",{'fields':('red_team_precent','blue_team_precent')})
    )

    add_fieldsets = (
        (None,{
            'classes':('wide',),
            'fields':('username','email','password1','password2')
        }),
    )

    search_fields = ('email','username')
    ordering = ('username',)

admin.site.register(CustomUser,CustomUserAdmin)