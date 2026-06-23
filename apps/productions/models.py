
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.utils import timezone


class MilkProductionLog(models.Model):
    """
    Model for daily milk production logs.
    """
    SESSION_CHOICES = [
        ('morning', _('Morning')),
        ('afternoon', _('Afternoon')),
        ('evening', _('Evening')),
    ]
    
    QUALITY_CHOICES = [
        ('excellent', _('Excellent')),
        ('good', _('Good')),
        ('average', _('Average')),
        ('poor', _('Poor')),
    ]
    
    animal = models.ForeignKey('animals.Animal', on_delete=models.CASCADE, related_name='milk_production_logs', verbose_name=_('animal'), limit_choices_to={'gender': 'female'})
    farm = models.ForeignKey('farms.Farm', on_delete=models.CASCADE, related_name='milk_production_logs', verbose_name=_('farm'))
    
    date = models.DateField(_('date'))
    session = models.CharField(_('session'), max_length=20, choices=SESSION_CHOICES)
    quantity = models.DecimalField(_('quantity (liters)'), max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    quality = models.CharField(_('quality'), max_length=20, choices=QUALITY_CHOICES, default='good')
    fat_percentage = models.DecimalField(_('fat percentage'), max_digits=5, decimal_places=2, validators=[MinValueValidator(0)], null=True, blank=True)
    snf_percentage = models.DecimalField(_('SNF percentage'), max_digits=5, decimal_places=2, validators=[MinValueValidator(0)], null=True, blank=True)
    protein_percentage = models.DecimalField(_('protein percentage'), max_digits=5, decimal_places=2, validators=[MinValueValidator(0)], null=True, blank=True)
    lactose_percentage = models.DecimalField(_('lactose percentage'), max_digits=5, decimal_places=2, validators=[MinValueValidator(0)], null=True, blank=True)
    temperature = models.DecimalField(_('temperature (°C)'), max_digits=5, decimal_places=2, validators=[MinValueValidator(0)], null=True, blank=True)
    
    price_per_liter = models.DecimalField(_('price per liter'), max_digits=10, decimal_places=2, null=True, blank=True)
    total_value = models.DecimalField(_('total value'), max_digits=15, decimal_places=2, null=True, blank=True)
    
    notes = models.TextField(_('notes'), blank=True, null=True)
    
    recorded_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='recorded_milk_logs', verbose_name=_('recorded by'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('milk production log')
        verbose_name_plural = _('milk production logs')
        unique_together = ('animal', 'date', 'session')
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['animal', 'date']),
            models.Index(fields=['farm', 'date']),
            models.Index(fields=['date', 'session']),
        ]
        
    def __str__(self):
        return f"{self.animal.tag_number} - {self.date} - {self.get_session_display()}"
    
    def save(self, *args, **kwargs):
        # Calculate total value if price_per_liter and quantity are provided
        if self.price_per_liter is not None and self.quantity is not None:
            self.total_value = self.price_per_liter * self.quantity
        
        # Use farm's default price if not set
        if not self.price_per_liter and self.farm:
            try:
                self.price_per_liter = self.farm.settings.default_milk_price
            except:
                pass
        
        super().save(*args, **kwargs)

