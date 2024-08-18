from django.db import models
from django.core.exceptions import ValidationError
from accounts.models import CustomUser


class UPARegistration(models.Model):
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name='Address')
    state = models.CharField(max_length=100, blank=True, null=True, verbose_name='State')
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name='City')
    pincode = models.CharField(max_length=10, blank=True, null=True, verbose_name='Pincode')
    reference_id = models.CharField(max_length=50, blank=True, null=True, verbose_name='Reference ID')
    
    def save(self, *args, **kwargs):
        # Ensure the reference_id is valid before saving
        if not CustomUser.objects.filter(uid_no=self.reference_id).exists():
            raise ValidationError("No user found with the provided reference UID.")
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.address or self.reference_id or str(self.pk)

