from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.utils import timezone
from datetime import datetime, timedelta


class Animal(models.Model):
    """
    Modal for tracking cows and buffalows.
    """
    SPECIES_CHOICES = [
        ('cow', _('Cow')),
        ('buffalow', _('Buffalow')),
    ]
    
    BREED_CHOICES = [
        # cows breeds
        ('holstein', _('Holstein Friesian')),
        ('jersey', _('Jersey')),
        ('gir', _('Gir')),
        ('sahiwal', _('Sahiwal')),
        ('red_sindhi', _('Red Sindhi')),
        ('tharparkar', _('Tharparkar')),
        ('kankrej', _('Kankrej')),
        ('ongole', _('Ongole')),
        ('rathi', _('Rathi')),
        ('hariana', _('Hariana')),
        ('crossbred', _('Crossbred')),
        
        # Buffalo breeds
        ('murrah', _('Murrah')),
        ('surti', _('Surti')),
        ('jaffarabadi', _('Jaffarabadi')),
        ('bhadawari', _('Bhadawari')),
        ('nili_ravi', _('Nili-Ravi')),
        ('mehsana', _('Mehsana')),
        ('other', _('Other')),
    ]
    
    GENDER_CHOICES = [
        ('female', _('Female')),
        ('male', _('Male')),
    ]
    
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('inactive', _('Inactive')),
        ('sold', _('Sold')),
        ('deceased', _('Deceased')),
        ('pregnant', _('Pregnant')),
        ('lactating', _('Lactating')),
        ('dry', _('Dry')),
        ('heifer', _('Heifer')),
        ('calf', _('Calf')),
    ]
    
    # Basic Information
    tag_number = models.CharField(max_length=50, unique=True, verbose_name=_('Tag Number'))
    name = models.CharField(_('name'), max_length=100, blank=True, null=True)
    species = models.CharField(_('species'), max_length=20, choices=SPECIES_CHOICES)
    breed = models.CharField(_('breed'), max_length=20, choices=BREED_CHOICES)
    gender = models.CharField(_('gender'), max_length=20, choices=GENDER_CHOICES)
    
    # farm association
    farm = models.ForeignKey('farms.Farm', on_delete=models.CASCADE, related_name='animals', verbose_name=_('farm'))
    
    # birth details
    date_of_birth = models.DateField(_('Date of Birth'), blank=True, null=True)
    birth_weight = models.DecimalField(_('Birth Weight (kg)'), max_digits=6, decimal_places=2, blank=True, null=True)
    
    # parentage
    mother = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='offspring_as_mother', verbose_name=_('mother'), limit_choices_to={'gender': 'female'})
    father = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='offspring_as_father', verbose_name=_('father'), limit_choices_to={'gender': 'male'})

    # physical characteristics
    color = models.CharField(_('color/markings'), max_length=100, blank=True, null=True)
    current_weight = models.DecimalField(_('Current Weight (kg)'), max_digits=6, decimal_places=2, blank=True, null=True)
    height = models.DecimalField(_('Height (cm)'), max_digits=6, decimal_places=2, blank=True, null=True)
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='active')
    is_active = models.BooleanField(_('is active'), default=True)
    
    # reproductive details
    lactation_number = models.PositiveIntegerField(_('lactation number'), default=0)
    last_calving_date = models.DateField(_('last calving date'), null=True, blank=True)
    expected_calving_date = models.DateField(_('expected calving date'), null=True, blank=True)
    is_pregnant = models.BooleanField(_('is pregnant'), default=False)
    
    # purchase details
    is_purchased = models.BooleanField(_('is purchased'), default=False)
    purchase_date = models.DateField(_('purchase date'), null=True, blank=True)
    purchase_price = models.DecimalField(_('purchase price'), max_digits=12, decimal_places=2, null=True, blank=True)
    purchase_farm = models.CharField(_('purchase farm'), max_length=255, blank=True, null=True)
    
    # sale details
    is_sold = models.BooleanField(_('is sold'), default=False)
    sale_date = models.DateField(_('sale date'), null=True, blank=True)
    sale_price = models.DecimalField(_('sale price'), max_digits=12, decimal_places=2, null=True, blank=True)
    sale_to = models.CharField(_('sale to'), max_length=255, blank=True, null=True)
    
    # image
    image = models.ImageField(_('animal image'), upload_to='animal_images/', blank=True, null=True)
    
    # timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('animal')
        verbose_name_plural = _('animals')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tag_number']),
            models.Index(fields=['farm']),
            models.Index(fields=['species']),
            models.Index(fields=['breed']),
            models.Index(fields=['status']),
            models.Index(fields=['is_active']),
        ]
        
    def __str__(self):
        name = f"({self.name})" if self.name else ""
        return f"{self.tag_number} {name} - {self.get_species_display()} "
    
    @property
    def age(self):
        """Calculate age in years and months."""
        if not self.date_of_birth:
            return None
        
        today = timezone.now().date()
        born = self.date_of_birth
        
        years = today.year - born.year
        months = today.month - born.month
        
        if today.day < born.day:
            months -= 1
        
        if months < 0:
            years -= 1
            months += 12
        
        return {'years': years, 'months': months}
    
    @property
    def age_in_days(self):
        """Calculate age in days."""
        if not self.date_of_birth:
            return None
        return (timezone.now().date() - self.date_of_birth).days
    
    @property
    def is_adult(self):
        """Check if animal is adult (2+ years)."""
        age = self.age
        if age:
            return age['years'] >= 2
        return False
    
    @property
    def current_lactation_days(self):
        """Calculate days in current lactation."""
        if self.last_calving_date:
            return (timezone.now().date() - self.last_calving_date).days
        return None
    
    def update_lactation_number(self):
        """Update lactation number based on calving history."""
        if self.gender == 'female':
            self.lactation_number = self.calvings.count()
            self.save(update_fields=['lactation_number'])
            
            
            
class AnimalHealthRecord (models.Model):
    """
    Model for animal health records.
    """
    
    RECORD_TYPE_CHOICES = [
        ('checkup', _('Regular Checkup')),
        ('vaccination', _('Vaccination')),
        ('deworming', _('Deworming')),
        ('treatment', _('Treatment')),
        ('surgery', _('Surgery')),
        ('pregnancy_check', _('Pregnancy Check')),
        ('other', _('Other')),
    ]
    
    # Basic Information
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='health_records', verbose_name=_('animal'))
    record_type = models.CharField(_('record type'), max_length=20, choices=RECORD_TYPE_CHOICES)
    date = models.DateField(_('date'))
    
    # health details
    description = models.TextField(_('description'), blank=True, null=True)
    symptoms = models.TextField(_('symptoms'), blank=True, null=True)
    diagnosis = models.TextField(_('diagnosis'), blank=True, null=True)
    treatment = models.TextField(_('treatment'), blank=True, null=True)
    
    # medication details
    medications = models.TextField(_('medications'), blank=True, null=True)
    dosage = models.CharField(_('dosage'), max_length=255, blank=True, null=True)
    
    # veterinarian details
    veterinarian_name = models.CharField(_('veterinarian name'), max_length=255, blank=True, null=True)
    veterinarian_contact = models.CharField(_('veterinarian contact'), max_length=255, blank=True, null=True)
    
    # cost details
    cost = models.DecimalField(_('cost'), max_digits=12, decimal_places=2, default=0.00)
    
    # follow-up details
    follow_up_date = models.DateField(_('follow-up date'), null=True, blank=True)
    follow_up_notes = models.TextField(_('follow-up notes'), blank=True, null=True)
    
    # Document Details
    documents = models.FileField(_('documents'), upload_to='health_records/', blank=True, null=True)
    recorded_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, blank=True, null=True, related_name='recorded_health_records', verbose_name=_('recorded by'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('animal health record')
        verbose_name_plural = _('animal health records')
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['animal']),
            models.Index(fields=['record_type']),
            models.Index(fields=['date']),
        ]
        
    def __str__(self):
        return f"{self.animal.tag_number} - {self.get_record_type_display()} - {self.date}"
    

class AnimalWeightLog(models.Model):
    """
    Model for tracking animal weight over time.
    """
    
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='weight_log', verbose_name=_('animal'))
    date = models.DateField(_('date'), default=timezone.now)
    weight = models.DecimalField(_('weight (kg)'), max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
    notes = models.TextField(_('notes'), blank=True, null=True)
    recorded_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, blank=True, null=True, related_name='recorded_weight_logs', verbose_name=_('recorded by'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('animal weight log')
        verbose_name_plural = _('animal weight logs')
        ordering = ['-date', '-created_at']
        unique_together = ['animal', 'date']
        indexes = [
            models.Index(fields=['animal']),
            models.Index(fields=['date']),
        ]
        
    def __str__(self):
        return f"{self.animal.tag_number} - {self.weight}kg on {self.date}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update current weight in Animal model
        self.animal.current_weight = self.weight
        self.animal.save(update_fields=['current_weight'])
    