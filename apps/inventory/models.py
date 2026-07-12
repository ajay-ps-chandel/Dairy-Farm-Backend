
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator


class InventoryCategory(models.Model):
    """
    Model for inventory categories.
    """
    
    name = models.CharField(_('name'), max_length=100, unique=True)
    description = models.TextField(_('description'), blank=True)
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('inventory category')
        verbose_name_plural = _('inventory categories')
        ordering = ['name']
    
    def __str__(self):
        return self.name


