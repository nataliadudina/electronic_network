from decimal import Decimal

from django.db import models
from django.core.exceptions import ValidationError


class Contacts(models.Model):
    department = models.CharField(max_length=255, null=True, blank=True, verbose_name='department')
    email = models.EmailField(max_length=255, verbose_name='email')
    country = models.CharField(max_length=85, verbose_name='Country')
    city = models.CharField(max_length=85, verbose_name='City')
    street = models.CharField(max_length=135, null=True, blank=True, verbose_name='St.')
    building = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='"Bld.')
    network_node = models.ForeignKey('NetworkNode', null=True, blank=True, on_delete=models.CASCADE,
                                     related_name='data')

    def clean(self):
        super().clean()
        if self.building and len(str(self.building)) > 5:
            raise ValidationError({
                'building': 'Number of building should not exceed 5 characters.'
            })

    def __str__(self):
        return f"{self.country}, {self.city} - {self.email}"

    class Meta:
        verbose_name = 'Contacts'
        verbose_name_plural = 'Contacts'
        ordering = ('network_node',)


class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name='Product')
    model = models.CharField(max_length=255, verbose_name='Model')
    release_date = models.DateField(null=True, blank=True, verbose_name='Release Date')
    sales_channel = models.ManyToManyField('NetworkNode', blank=True, related_name='product')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ('name',)


class NetworkNode(models.Model):
    LEVELS_CHOICES = [
        (0, 'Factory'),
        (1, 'Retailer'),
        (2, 'Consumer'),
    ]

    name = models.CharField(max_length=255, unique=True, verbose_name='Network Node')
    contacts = models.ManyToManyField(Contacts, verbose_name='Contacts', related_name='organisation')
    products = models.ManyToManyField(Product, verbose_name='Products', related_name='seller')
    supplier = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Supplier',
                                 related_name='supplied_by')
    debt_amount = models.DecimalField(max_digits=10, decimal_places=2, default='0.00', verbose_name='Debt')
    creation_time = models.DateTimeField(auto_now_add=True, verbose_name='Creation Time')
    level = models.IntegerField(choices=LEVELS_CHOICES, default=1)

    def clean(self):
        """ Валидация данных при работе через админ-панель """
        super().clean()

        """ Проверка, что организация не ссылается на себя как на своего поставщика """
        if self.supplier == self:
            raise ValidationError("An organisation cannot be its own supplier.")

        """ Проверка, что завод не может иметь задолженности """
        if self.level == 0:
            if self.debt_amount:
                raise ValidationError("The factory cannot be in debt as it has no supplier.")

            """ Проверка, что завод не иметь поставщика, а ретейл и ИП могут ссылаться на другие уровни """
            if self.supplier:
                raise ValidationError("Factory cannot have a supplier.")
        elif self.level in (1, 2) and not self.supplier:
            raise ValidationError("Retail or Consumer must have a supplier.")

    def save(self, *args, **kwargs):
        self.full_clean()    # Вызов полной валидации
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Network Node'
        verbose_name_plural = 'Network Nodes'
        ordering = ('pk',)
