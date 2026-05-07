from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator


class Farm(models.Model):
    """
    Model for managing multiple farms.
    """
    
    FARM_TYPE_CHOICES = [
        ('dairy', _('Dairy Farm')),
        ('mixed', _('Mixed Farming')),
        ('organic', _('Organic Dairy')),
        ('commercial', _('Commercial Dairy')),
    ]
    
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('inactive', _('Inactive')),
        ('suspended', _('Suspended')),
    ]
    
    # Basic Information
    name = models.CharField(_('farm name'), max_length=200)
    code = models.CharField(_('farm code'), max_length=50, unique=True, blank=True)
    description = models.TextField(_('description'), blank=True)
    farm_type = models.CharField(
        _('farm type'),
        max_length=20,
        choices=FARM_TYPE_CHOICES,
        default='dairy'
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    
    # Owner
    owner = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='owned_farms',
        verbose_name=_('owner'),
        limit_choices_to={'role': 'owner'}
    )
    
    # Location
    address = models.TextField(_('address'))
    city = models.CharField(_('city'), max_length=100)
    state = models.CharField(_('state'), max_length=100)
    country = models.CharField(_('country'), max_length=100, default='India')
    pincode = models.CharField(_('pincode'), max_length=20)
    latitude = models.DecimalField(
        _('latitude'),
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(-90)],
        blank=True,
        null=True
    )
    longitude = models.DecimalField(
        _('longitude'),
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(-180)],
        blank=True,
        null=True
    )
    
    #Contact
    contact_person = models.CharField(_('contact person'), max_length=150, blank=True)
    contact_phone = models.CharField(_('contact phone'), max_length=20, blank=True)
    contact_email = models.EmailField(_('contact email'), blank=True)
    
     # Farm Details
    total_area = models.DecimalField(
        _('total area (acres)'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    grazing_area = models.DecimalField(
        _('grazing area (acres)'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    built_up_area = models.DecimalField(
        _('built-up area (sq ft)'),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    
    # Capacity
    max_animals = models.PositiveIntegerField(_('maximum animals'), default=0)
    current_animals = models.PositiveIntegerField(_('current animals'), default=0)
    
    # Facilities
    has_milking_parlor = models.BooleanField(_('has milking parlor'), default=False)
    has_cold_storage = models.BooleanField(_('has cold storage'), default=False)
    has_veterinary_facility = models.BooleanField(_('has veterinary facility'), default=False)
    has_feed_storage = models.BooleanField(_('has feed storage'), default=False)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    is_active = models.BooleanField(_('is active'), default=True)
    
    class Meta:
        verbose_name = _('farm')
        verbose_name_plural = _('farms')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner']),
            models.Index(fields=['status']),
            models.Index(fields=['code']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code()
        super().save(*args, **kwargs)
    
    def generate_code(self):
        """Generate unique farm code."""
        import uuid
        return f"FARM-{uuid.uuid4().hex[:8].upper()}"
    
    @property
    def available_capacity(self):
        """Calculate available animal capacity."""
        return self.max_animals - self.current_animals
    
    @property
    def capacity_percentage(self):
        """Calculate capacity utilization percentage."""
        if self.max_animals == 0:
            return 0
        return (self.current_animals / self.max_animals) * 100
    
    def update_animal_count(self):
        """Update current animal count."""
        self.current_animals = self.animals.filter(is_active=True).count()
        self.save(update_fields=['current_animals'])
        
class FarmDocument(models.Model):
    """
    Model for storing farm-related documents.
    """
    
    DOCUMENT_TYPE_CHOICES = [
        ('registration', _('Registration Certificate')),
        ('license', _('License')),
        ('insurance', _('Insurance')),
        ('land_title', _('Land Title')),
        ('permit', _('Permit')),
        ('other', _('Other')),
    ]
    
    farm = models.ForeignKey(
        Farm,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name=_('farm')
    )
    document_type = models.CharField(
        _('document type'),
        max_length=20,
        choices=DOCUMENT_TYPE_CHOICES
    )
    title = models.CharField(_('title'), max_length=200)
    file = models.FileField(_('file'), upload_to='farm_documents/')
    description = models.TextField(_('description'), blank=True)
    issue_date = models.DateField(_('issue date'), null=True, blank=True)
    expiry_date = models.DateField(_('expiry date'), null=True, blank=True)
    document_number = models.CharField(_('document number'), max_length=100, blank=True)
    is_verified = models.BooleanField(_('is verified'), default=False)
    uploaded_at = models.DateTimeField(_('uploaded at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('farm document')
        verbose_name_plural = _('farm documents')
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.title} - {self.farm.name}"
    
class FarmNote(models.Model):
    """
    Model for farm notes/observations.
    """
    
    farm = models.ForeignKey(
        Farm,
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name=_('farm')
    )
    title = models.CharField(_('title'), max_length=200)
    content = models.TextField(_('content'))
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='farm_notes',
        verbose_name=_('created by')
    )
    is_important = models.BooleanField(_('is important'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('farm note')
        verbose_name_plural = _('farm notes')
        ordering = ['-is_important', '-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.farm.name}"


class FarmSettings(models.Model):
    """
    Model for farm-specific settings.
    """
    
    farm = models.OneToOneField(
        Farm,
        on_delete=models.CASCADE,
        related_name='settings',
        verbose_name=_('farm')
    )
    
    # Milk Production Settings
    milking_sessions_per_day = models.PositiveIntegerField(
        _('milking sessions per day'),
        default=2
    )
    default_milk_price = models.DecimalField(
        _('default milk price per liter'),
        max_digits=10,
        decimal_places=2,
        default=50.00
    )
    
    # Alert Settings
    low_inventory_threshold = models.PositiveIntegerField(
        _('low inventory threshold (%)'),
        default=20
    )
    animal_health_alert_days = models.PositiveIntegerField(
        _('animal health alert days'),
        default=30
    )
    
    # Notification Settings
    email_notifications = models.BooleanField(_('email notifications'), default=True)
    sms_notifications = models.BooleanField(_('SMS notifications'), default=False)
    
    # Currency and Units
    currency = models.CharField(_('currency'), max_length=10, default='INR')
    weight_unit = models.CharField(_('weight unit'), max_length=10, default='kg')
    volume_unit = models.CharField(_('volume unit'), max_length=10, default='liter')
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('farm settings')
        verbose_name_plural = _('farm settings')
    
    def __str__(self):
        return f"Settings - {self.farm.name}"
