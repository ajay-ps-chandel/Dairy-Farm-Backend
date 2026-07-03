
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
        
        
class DailyProductionSummary(models.Model):
    """
    Model for summarizing milk production over a period.
    """
    farm = models.ForeignKey('farms.Farm', on_delete=models.CASCADE, related_name='daily_summaries', verbose_name=_('farm'))
    date = models.DateField(_('date'))
    
    # Aggregate fields
    total_quantity = models.DecimalField(_('total quantity (liters)'), max_digits=15, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    total_animals_milked = models.PositiveIntegerField(_('total animals milked'), default=0)
    average_quantity_per_animal = models.DecimalField(_('average quantity per animal'), max_digits=10, decimal_places=2, default=0)
    
    # Session-wise quantities
    morning_quantity = models.DecimalField(_('morning quantity (liters)'), max_digits=15, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    afternoon_quantity = models.DecimalField(_('afternoon quantity (liters)'), max_digits=15, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    evening_quantity = models.DecimalField(_('evening quantity (liters)'), max_digits=15, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    
    # Average quality metrics
    average_fat = models.DecimalField(_('average fat percentage'), max_digits=5, decimal_places=2, validators=[MinValueValidator(0)], null=True, blank=True)
    average_snf = models.DecimalField(_('average SNF percentage'), max_digits=5, decimal_places=2, validators=[MinValueValidator(0)], null=True, blank=True)
    
    # Financial summary fields
    total_value = models.DecimalField(_('total value'), max_digits=20, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    average_price_per_liter = models.DecimalField(_('average price per liter'), max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('milk production summary')
        verbose_name_plural = _('milk production summaries')
        ordering = ['-date']
        indexes = [
            models.Index(fields=['farm', 'date']),
        ]
        
    def __str__(self):
        return f"{self.farm.name} - {self.date} - {self.total_quantity}L"


class AnimalProductionSummary(models.Model):
    """
    Model for summarizing milk production for individual animals over a period.
    """
    animal = models.ForeignKey('animals.Animal', on_delete=models.CASCADE, related_name='production_summaries', verbose_name=_('animal'))
    farm = models.ForeignKey('farms.Farm', on_delete=models.CASCADE, related_name='animal_production_summaries', verbose_name=_('farm'))
    
    # Period fields
    period_start = models.DateField(_('period start'))
    period_end = models.DateField(_('period end'))
    period_type = models.CharField(_('period type'), max_length=20, choices=[('daily', _('Daily')), ('weekly', _('Weekly')), ('monthly', _('Monthly'))], default='daily')
    
    # Production metrics
    total_quantity = models.DecimalField(_('total quantity (liters)'), max_digits=15, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    total_sessions = models.PositiveIntegerField(_('total sessions'), default=0)
    average_per_session = models.DecimalField(_('average per session'), max_digits=10, decimal_places=2, default=0)
    average_per_day = models.DecimalField(_('average per day'), max_digits=10, decimal_places=2, default=0)
    
    # Peak production metrics
    peak_quantity = models.DecimalField(_('peak quantity (liters)'), max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    peak_date = models.DateField(_('peak date'), null=True, blank=True)
    
    # Average quality metrics
    average_fat = models.DecimalField(_('average fat percentage'), max_digits=5, decimal_places=2, validators=[MinValueValidator(0)], null=True, blank=True)
    average_snf = models.DecimalField(_('average SNF percentage'), max_digits=5, decimal_places=2, validators=[MinValueValidator(0)], null=True, blank=True)
    
    # Financial summary fields
    total_value = models.DecimalField(_('total value'), max_digits=20, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('animal production summary')
        verbose_name_plural = _('animal production summaries')
        unique_together = ('animal', 'period_start', 'period_end')
        ordering = ['-period_end']
        indexes = [
            models.Index(fields=['animal', 'period_start', 'period_end']),
        ]
        
    def __str__(self):
        return f"{self.animal.tag_number} - {self.period_start} to {self.period_end}"


class MilkSale(models.Model):
    """
    Model for recording milk sales.
    """
    SALE_TYPE_CHOICES = [
        ('direct', _('Direct Sale')),
        ('dairy', _('Dairy/Cooperative')),
        ('wholesale', _('Wholesale')),
        ('retail', _('Retail')),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('partial', _('Partial')),
        ('paid', _('Paid')),
    ]
    
    farm = models.ForeignKey('farms.Farm', on_delete=models.CASCADE, related_name='milk_sales', verbose_name=_('farm'))
    
    # Sale details
    date = models.DateField(_('date'))
    sale_type = models.CharField(_('sale type'), max_length=20, choices=SALE_TYPE_CHOICES, default='direct')
    
    # Buyer details
    buyer_name = models.CharField(_('buyer name'), max_length=255)
    buyer_contact = models.CharField(_('buyer contact'), max_length=255, blank=True, null=True)
    buyer_address = models.TextField(_('buyer address'), blank=True, null=True)
    
    # Sale metrics
    quantity = models.DecimalField(_('quantity (liters)'), max_digits=15, decimal_places=2, validators=[MinValueValidator(0)])
    price_per_liter = models.DecimalField(_('price per liter'), max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    total_amount = models.DecimalField(_('total amount'), max_digits=20, decimal_places=2, validators=[MinValueValidator(0)], blank=True)
    
    # Quality metrics
    fat_percentage = models.DecimalField(_('fat percentage'), max_digits=5, decimal_places=2, validators=[MinValueValidator(0)], null=True, blank=True)
    snf_percentage = models.DecimalField(_('SNF percentage'), max_digits=5, decimal_places=2, validators=[MinValueValidator(0)], null=True, blank=True)
    
    # Payment details
    payment_status = models.CharField(_('payment status'), max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    amount_paid = models.DecimalField(_('amount paid'), max_digits=20, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    payment_date = models.DateField(_('payment date'), null=True, blank=True)
    payment_method = models.CharField(_('payment method'), max_length=50, blank=True, null=True)
    
    # Additional notes
    notes = models.TextField(_('notes'), blank=True, null=True)
    
    # Recorded by and timestamps
    recorded_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='recorded_milk_sales', verbose_name=_('recorded by'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('milk sale')
        verbose_name_plural = _('milk sales')
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['farm', 'date']),
            models.Index(fields=['payment_status']),
        ]
        
    def __str__(self):
        return f"{self.buyer_name} - {self.date} - {self.quantity}L"
    
    def save(self, *args, **kwargs):
        # Calculate total value if not set
        if self.price_per_liter is not None and self.quantity is not None:
            self.total_value = self.price_per_liter * self.quantity
        
        super().save(*args, **kwargs)
    
    @property
    def balance_due(self):
        return self.total_value - self.amount_paid