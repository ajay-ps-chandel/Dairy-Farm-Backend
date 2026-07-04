
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
    

class RecurringExpense(models.Model):
    """
    Model for recurring expenses.
    """
    
    FREQUENCY_CHOICES = [
        ('daily', _('Daily')),
        ('weekly', _('Weekly')),
        ('monthly', _('Monthly')),
        ('quarterly', _('Quarterly')),
        ('yearly', _('Yearly')),
    ]
    
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True, null=True)
    
    farm = models.ForeignKey('farms.Farm', on_delete=models.CASCADE, related_name='recurring_expenses', verbose_name=_('farm'))
    
    category = models.ForeignKey(ExpenseCategory, on_delete=models.SET_NULL, related_name='recurring_expenses', verbose_name=_('category'), null=True, blank=True)
    
    amount = models.DecimalField(_('amount'), max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    
    frequency = models.CharField(_('frequency'), max_length=20, choices=FREQUENCY_CHOICES, default='monthly')
    
    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'), null=True, blank=True)
    
    next_due_date = models.DateField(_('next due date'), null=True, blank=True)
    
    vendor_name = models.CharField(_('vendor name'), max_length=200, blank=True, null=True)
    vendor_contact = models.CharField(_('vendor contact'), max_length=20, blank=True, null=True)
    
    is_active = models.BooleanField(_('is active'), default=True)
    
    created_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='created_recurring_expenses', verbose_name=_('created by'))
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('recurring expense')
        verbose_name_plural = _('recurring expenses')
        ordering = ['next_due_date']
    
    def __str__(self):
        return f"{self.title} - {self.get_frequency_display()} - {self.amount}"


class ExpenseBudget(models.Model):
    """
    Model for expense budgets.
    """
    PERIOD_CHOICES = [
        ('monthly', _('Monthly')),
        ('quarterly', _('Quarterly')),
        ('yearly', _('Yearly')),
    ]
    
    farm = models.ForeignKey('farms.Farm', on_delete=models.CASCADE, related_name='budgets', verbose_name=_('farm'))
    
    category = models.ForeignKey(ExpenseCategory, on_delete=models.SET_NULL, related_name='budgets', verbose_name=_('category'))
    
    period = models.CharField(_('period'), max_length=20, choices=PERIOD_CHOICES, default='monthly')
    
    period_start = models.DateField(_('period start'))
    period_end = models.DateField(_('period end'))
    
    budget_amount = models.DecimalField(_('budget amount'), max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    
    notes = models.TextField(_('notes'), blank=True, null=True)
    
    created_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='created_budgets', verbose_name=_('created by'))
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('expense budget')
        verbose_name_plural = _('expense budgets')
        ordering = ['-period_start']
        unique_together = ['farm', 'category', 'period_start']
    
    def __str__(self):
        return f"{self.farm.name} - {self.category.name} - {self.period_start}"
    
    @property
    def spent_amount(self):
        """Calculate spent amount for this budget period."""
        from django.db.models import Sum
        return Expense.objects.filter(
            farm=self.farm,
            category=self.category,
            expense_date__gte=self.period_start,
            expense_date__lte=self.period_end,
            status='paid'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    @property
    def remaining_amount(self):
        """Calculate remaining budget."""
        return self.budget_amount - self.spent_amount
    
    @property
    def utilization_percentage(self):
        """Calculate budget utilization percentage."""
        if self.budget_amount > 0:
            return (self.spent_amount / self.budget_amount) * 100
        return 0