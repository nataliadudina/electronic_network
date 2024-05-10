from rest_framework.exceptions import ValidationError


class SupplierValidator:
    """ Проверка, что завод не иметь поставщика, а ретейл и ИП могут ссылаться на другие уровни """

    def __call__(self, instance):
        if instance.get('level', None) == 0:
            if instance.get('supplier', None):
                raise ValidationError("Factory cannot have a supplier.")
        elif instance.get('level', None) in [1, 2]:
            if not instance.get('supplier', None):
                raise ValidationError("Retail or Consumer must have a supplier.")


class FactoryDebtValidator:
    """ Проверка, что завод не может иметь задолженности """

    def __call__(self, instance):
        if instance.get('level', None) == 0:
            if instance.get('debt_amount', None):
                raise ValidationError("The factory cannot be in debt as it has no supplier.")
