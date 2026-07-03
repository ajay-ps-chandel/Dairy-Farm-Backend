
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator





class ExpenseCategory(models.Model):
    """
    Model for expense categories.
    """
    
    CATEGORY_TYPE_CHOICES = [
        ('operational', _('Operational')),
        ('capital', _('Capital')),
        ('maintenance', _('Maintenance')),
        ('labor', _('Labor')),
        ('feed', _('Feed')),
        ('medical', _('Medical')),
        ('utility', _('Utility')),
        ('transport', _('Transport')),
        ('other', _('Other')),
    ]
    
    name = models.CharField(_('name'), max_length=100, unique=True)
    category_type = models.CharField(_('category type'), max_length=20, choices=CATEGORY_TYPE_CHOICES, default='operational')
    description = models.TextField(_('description'), blank=True, null=True)
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('expense category')
        verbose_name_plural = _('expense categories')
        ordering = ['name']
        
    def __str__(self):
        return self.name
    
class Expense(models.Model):
    """
    Model for tracking expenses.
    """
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', _('Cash')),
        ('bank_transfer', _('Bank Transfer')),
        ('check', _('Check')),
        ('credit_card', _('Credit Card')),
        ('debit_card', _('Debit Card')),
        ('upi', _('UPI')),
        ('other', _('Other')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('paid', _('Paid')),
    ]
    
    # Basic Info
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True, null=True)
    
    # Farm
    farm = models.ForeignKey('farms.Farm', on_delete=models.CASCADE, related_name='expenses', verbose_name=_('farm'))
    
    # Category
    category = models.ForeignKey(ExpenseCategory, on_delete=models.SET_NULL, related_name='expenses', verbose_name=_('category'), null=True, blank=True)
    
    # Amount
    amount = models.DecimalField(_('amount'), max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    tax_amount = models.DecimalField(_('tax amount'), max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(_('total amount'), max_digits=12, decimal_places=2)
    
    # Date
    expense_date = models.DateField(_('expense date'))
    
    # Payment
    payment_method = models.CharField(_('payment method'),max_length=20,choices=PAYMENT_METHOD_CHOICES,default='cash')
    payment_reference = models.CharField(_('payment reference'),max_length=100,blank=True, null=True)
    
    # Vender
    vendor_name = models.CharField(_('vendor name'), max_length=200, blank=True, null=True)
    vendor_contact = models.CharField(_('vendor contact'), max_length=20, blank=True, null=True)
    
    # Status
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Invoice/Receipt
    invoice_number = models.CharField(_('invoice number'), max_length=100, blank=True, null=True)
    receipt = models.FileField(_('receipt'), upload_to='expense_receipts/', blank=True, null=True)
    
    # Related to
    related_animal = models.ForeignKey('animals.Animal', on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses', verbose_name=_('related animal'))
    
    # Approval
    approved_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_expenses', verbose_name=_('approved by'))
    approved_at = models.DateTimeField(_('approved at'), null=True, blank=True)
    
    # Notes
    notes = models.TextField(_('notes'), blank=True)
    
    # Recorded by
    recorded_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='recorded_expenses', verbose_name=_('recorded by'))
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('expense')
        verbose_name_plural = _('expenses')
        ordering = ['-expense_date', '-created_at']
        indexes = [
            models.Index(fields=['farm', 'expense_date']),
            models.Index(fields=['category']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.amount} - {self.expense_date}"
    
    def save(self, *args, **kwargs):
        # Calculate total amount
        self.total_amount = self.amount + self.tax_amount
        super().save(*args, **kwargs)
    