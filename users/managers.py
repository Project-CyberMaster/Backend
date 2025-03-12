from django.contrib.auth.base_user import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self,username,email,password,**extra_fields):
        if not username:
            raise ValueError("user must have an username")
        if not email:
            raise ValueError("user must have an email")
        
        email = self.normalize_email(email)
        extra_fields.setdefault('red_team_percent',0)
        extra_fields.setdefault('blue_team_percent',0)

        user= self.model(username=username,email=email,**extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self,username,email,password,**extra_fields):
        if not username:
            raise ValueError("user must have an username")
        if not email:
            raise ValueError("user must have an email")
        
        email = self.normalize_email(email)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault('red_team_percent',0)
        extra_fields.setdefault('blue_team_percent',0)

        user= self.model(username=username,email=email,**extra_fields)
        user.set_password(password)
        user.save()
        return user