
import random
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from .managers import CustomUserManager

class CustomUser(AbstractUser):
    mobile = models.CharField(max_length=15, unique=True, blank=True, null=True, verbose_name=_('Mobile Number'))
    name = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Full Name'))
    
    uid_no = models.CharField(max_length=36, unique=True, blank=True, null=True, verbose_name=_('UID Number'))
    
# Legs
    left_leg = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='left_leg_set', on_delete=models.SET_NULL)
    middle_leg = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='middle_leg_set', on_delete=models.SET_NULL)
    right_leg = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='right_leg_set', on_delete=models.SET_NULL)
    
    account_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    verified = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    username = None
    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()
    
    def save(self, *args, **kwargs):
        if not self.uid_no:
            self.uid_no = self.generate_uid_no()
        super().save(*args, **kwargs)

    def generate_uid_no(self):
        """Generate a unique 6-digit UID number."""
        while True:
            uid = f"{random.randint(100000, 999999)}"
            if not CustomUser.objects.filter(uid_no=uid).exists():
                return uid
    
    # def assign_leg(self, new_user_uid):
    #     if not self.left:
    #         self.left = new_user_uid
    #     elif not self.middle:
    #         self.middle = new_user_uid
    #     elif not self.right:
    #         self.right = new_user_uid
    #     else:
    #         raise ValidationError("All legs are occupied. Cannot assign a new user.")
    #     self.save()
    
    def __str__(self):
        return self.mobile
    


from django.db import models
from django.utils.translation import gettext_lazy as _

class LegCategory(models.TextChoices):
    GENERAL = 'GEN', _('General')
    BPL = 'BPL', _('BPL')
    HANDICAP = 'HAN', _('Handicap')

class LegIncomeModel(models.Model):
    leg1 = models.CharField(
        max_length=3,
        choices=LegCategory.choices,
        default=LegCategory.GENERAL,
        verbose_name=_('Leg 1 Category')
    )
    leg2 = models.CharField(
        max_length=3,
        choices=LegCategory.choices,
        default=LegCategory.GENERAL,
        verbose_name=_('Leg 2 Category')
    )
    leg3 = models.CharField(
        max_length=3,
        choices=LegCategory.choices,
        default=LegCategory.GENERAL,
        verbose_name=_('Leg 3 Category')
    )
    income = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Income')
    )

    def __str__(self):
        return f"Leg Income Model - {self.id}"

    class Meta:
        verbose_name = _('Leg Income Model')
        verbose_name_plural = _('Leg Income Models')

