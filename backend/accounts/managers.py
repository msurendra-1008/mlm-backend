# accounts/managers.py

from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, mobile, name, password=None, **extra_fields):
        if not mobile:
            raise ValueError('The Mobile number must be set')
        mobile = self.normalize_email(mobile)
        user = self.model(mobile=mobile, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not password:
            raise ValueError('The Password must be set')

        if mobile:
            return self.create_user(mobile, name="Admin", password=password, **extra_fields)
        elif email:
            extra_fields.setdefault('name', 'Admin')
            return self.create_user(email, name="Admin", password=password, **extra_fields)
        else:
            raise ValueError('The superuser must have either a mobile number or an email')
