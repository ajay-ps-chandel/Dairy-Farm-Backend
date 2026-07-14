
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


class InventoryItem(models.Model):
    """
    Model for inventory items.
    """
    
    ITEM_TYPE_CHOICES = [
        ('feed', _('Animal Feed')),
        ('medicine', _('Medicine')),
        ('equipment', _('Equipment')),
        ('supply', _('Supply')),
        ('fodder', _('Fodder')),
        ('mineral', _('Mineral Supplement')),
        ('vaccine', _('Vaccine')),
        ('other', _('Other')),
    ]
    
    UNIT_CHOICES = [
        ('kg', _('Kilogram')),
        ('gm', _('Gram')),
        ('liter', _('Liter')),
        ('ml', _('Milliliter')),
        ('piece', _('Piece')),
        ('pack', _('Pack')),
        ('box', _('Box')),
        ('bag', _('Bag')),
        ('bottle', _('Bottle')),
        ('unit', _('Unit')),
    ]
    
    # Basic Info
    name = models.CharField(_('name'), max_length=200)
    code = models.CharField(_('item code'), max_length=50, unique=True, blank=True)
    description = models.TextField(_('description'), blank=True)
    category = models.ForeignKey(InventoryCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='items', verbose_name=_('category'))
    item_type = models.CharField(_('item type'), max_length=20, choices=ITEM_TYPE_CHOICES, default='other')
    
    # Farm
    farm = models.ForeignKey('farms.Farm', on_delete=models.CASCADE, related_name='inventory_items', verbose_name=_('farm'))
    
    # Unit
    unit = models.CharField(_('unit'), max_length=20, choices=UNIT_CHOICES, default='kg')
    
    # Stock
    quantity = models.DecimalField(_('current quantity'), max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    reorder_level = models.DecimalField(_('reorder level'), max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    max_stock = models.DecimalField(_('maximum stock'), max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Pricing
    unit_cost = models.DecimalField(_('unit cost'), max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    
    # Supplier
    supplier_name = models.CharField(_('supplier name'), max_length=200, blank=True)
    supplier_contact = models.CharField(_('supplier contact'), max_length=20, blank=True)
    
    # Status
    is_active = models.BooleanField(_('is active'), default=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('inventory item')
        verbose_name_plural = _('inventory items')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['farm']),
            models.Index(fields=['category']),
            models.Index(fields=['item_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code()
        super().save(*args, **kwargs)
    
    def generate_code(self):
        """Generate unique item code."""
        import uuid
        return f"INV-{uuid.uuid4().hex[:8].upper()}"
    
    @property
    def stock_value(self):
        """Calculate stock value."""
        return self.quantity * self.unit_cost
    
    @property
    def stock_status(self):
        """Get stock status."""
        if self.quantity <= 0:
            return 'out_of_stock'
        elif self.quantity <= self.reorder_level:
            return 'low_stock'
        return 'in_stock'
    
    @property
    def needs_reorder(self):
        """Check if item needs reordering."""
        return self.quantity <= self.reorder_level


class StockTransaction(models.Model):
    """
    Model for stock transactions.
    """
    
    TRANSACTION_TYPE_CHOICES = [
        ('purchase', _('Purchase')),
        ('consumption', _('Consumption')),
        ('adjustment', _('Adjustment')),
        ('return', _('Return')),
        ('transfer_in', _('Transfer In')),
        ('transfer_out', _('Transfer Out')),
        ('wastage', _('Wastage')),
    ]
    
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='transactions', verbose_name=_('item'))
    transaction_type = models.CharField(_('transaction type'), max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    date = models.DateField(_('date'))
    quantity = models.DecimalField(_('quantity'), max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    # For purchase transactions
    unit_cost = models.DecimalField(_('unit cost'), max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], null=True, blank=True)
    total_cost = models.DecimalField(_('total cost'), max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], null=True, blank=True)
    
    # Supplier info for purchases
    supplier_name = models.CharField(_('supplier name'), max_length=200, blank=True)
    supplier_contact = models.CharField(_('supplier contact'), max_length=20, blank=True)
    invoice_number = models.CharField(_('invoice number'), max_length=100, blank=True)
    
    # Reference
    reference = models.CharField(_('reference'), max_length=200, blank=True)
    notes = models.TextField(_('notes'), blank=True)
    
    # Balance after transaction
    balance_after = models.DecimalField(_('balance after'), max_digits=10, decimal_places=2)
    
    # Recorded by
    recorded_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='recorded_stock_transactions', verbose_name=_('recorded by'))
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('stock transaction')
        verbose_name_plural = _('stock transactions')
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['item', 'date']),
            models.Index(fields=['transaction_type']),
        ]
    
    def __str__(self):
        return f"{self.item.name} - {self.get_transaction_type_display()} - {self.quantity}"
    
    def save(self, *args, **kwargs):
        # Calculate total cost
        if self.unit_cost and self.quantity:
            self.total_cost = self.unit_cost * self.quantity
        
        # Update item quantity
        if self.transaction_type in ['purchase', 'transfer_in', 'return', 'adjustment']:
            self.item.quantity += self.quantity
        else:  # consumption, transfer_out, wastage
            self.item.quantity -= self.quantity
        
        self.balance_after = self.item.quantity
        self.item.save()
        
        super().save(*args, **kwargs)


class FeedFormula(models.Model):
    """
    Model for feed formulas/recipes.
    """
    name = models.CharField(_('name'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    
    farm = models.ForeignKey('farms.Farm', on_delete=models.CASCADE, related_name='feed_formulas', verbose_name=_('farm'))
    
    # Target animal group
    target_animal = models.CharField(_('target animals'), max_length=200, blank=True)
    
    # Ingredients
    preparation_instructions = models.TextField(_('preparation instructions'), blank=True)
    feeding_instructions = models.TextField(_('feeding instructions'), blank=True)
    
    is_active = models.BooleanField(_('is active'), default=True)
    
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_feed_formulas', verbose_name=_('created by'))
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('feed formula')
        verbose_name_plural = _('feed formulas')
        ordering = ['-created_at']
        
    def __str__(self):
        return self.name
    
    @property
    def total_quantity(self):
        """Calculate total quantity of ingredients."""
        return self.ingredients.aggregate(
            total=models.Sum('quantity')
        )['total'] or 0
        

class FeedFormulaIngredient(models.Model):
    """
    Model for ingredients in a feed formula.
    """
    formula = models.ForeignKey(FeedFormula, on_delete=models.CASCADE, related_name='ingredients', verbose_name=_('formula'))
    ingredient = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='used_in_formulas', verbose_name=_('ingredient'), limit_choices_to={'item_type__in': ['feed', 'fodder', 'mineral']})
    quantity = models.DecimalField(_('quantity'), max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    notes = models.TextField(_('notes'), blank=True)
    
    class Meta:
        verbose_name = _('feed formula ingredient')
        verbose_name_plural = _('feed formula ingredients')
        ordering = ['formula', 'ingredient']
        
    def __str__(self):
        return f"{self.formula.name} - {self.ingredient.name} ({self.quantity})"
    
    
