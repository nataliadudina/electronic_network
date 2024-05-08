from rest_framework import serializers

from networks.models import NetworkNode, Product, Contacts
from networks.validators import SupplierValidator, FactoryDebtValidator


class ContactsSerializer(serializers.ModelSerializer):
    """ Сериалайзер для вывода контактов списком """

    class Meta:
        model = Contacts
        fields = '__all__'


class ContactsSerializerBrief(serializers.ModelSerializer):
    """ Сериалайзер для вывода контактов при просмотре списка организаций """

    address = serializers.SerializerMethodField()

    class Meta:
        model = Contacts
        fields = ['department', 'email', 'address']

    def get_address(self, obj):
        """ Вывод адреса единой строкой """
        return f"{obj.country}, {obj.city}, {obj.street}-{obj.building}"


class ContactsSerializerCustom(serializers.ModelSerializer):
    """ Сериалайзер для вывода контактов при просмотре информации об отдельной организации """

    class Meta:
        model = Contacts
        fields = ['department', 'email', 'country', 'city', 'street', 'building']


class NetworkNodeSerializerBrif(serializers.Serializer):
    """Сериалайзер для вывода названия канала продаж времсто id при просмотре товаров"""

    name = serializers.CharField(max_length=255)


class ProductSerializerBase(serializers.ModelSerializer):
    """ Базовый сериалайзер для вывода краткой информации о товарах в списке организаций"""

    class Meta:
        model = Product
        fields = ['id', 'name', 'model']


class ProductSerializerCustom(ProductSerializerBase):
    """ Сериалайзер для вывода более подробной информации о товарах при чтении организации """

    release_date = serializers.DateField()

    class Meta(ProductSerializerBase.Meta):
        fields = ProductSerializerBase.Meta.fields + ['release_date']


class ProductSerializer(ProductSerializerBase):
    """ Сериалайзер для вывода информации о товарах в списке """

    number_of_sales_channels = serializers.IntegerField(read_only=True)
    sales_channel = NetworkNodeSerializerBrif(many=True, read_only=True)

    class Meta(ProductSerializerBase.Meta):
        fields = ProductSerializerCustom.Meta.fields + ['number_of_sales_channels', 'sales_channel']

    def to_representation(self, instance):
        """ Добавление поля количества каналов продаж для каждого товара """
        representation = super().to_representation(instance)
        representation['number_of_sales_channels'] = instance.sales_channel.count()
        return representation


class NetworkNodeCreateSerializer(serializers.ModelSerializer):
    """ Сериалайзер для создания новой записи организации """

    contacts = serializers.PrimaryKeyRelatedField(many=True, queryset=Contacts.objects.all())
    products = serializers.PrimaryKeyRelatedField(many=True, queryset=Product.objects.all())

    class Meta:
        model = NetworkNode
        fields = ['name', 'contacts', 'products', 'supplier', 'debt_amount', 'creation_time', 'level']
        validators = [SupplierValidator(), FactoryDebtValidator()]


class NetworkNodeSerializer(serializers.ModelSerializer):
    """ Сериалайзер для вывода информации об организациях в списке """

    contacts = ContactsSerializerBrief(many=True)
    items_quantity = serializers.IntegerField(read_only=True)

    class Meta:
        model = NetworkNode
        fields = ['id', 'name', 'contacts', 'items_quantity', 'supplier', 'debt_amount', 'level']


class NetworkNodeDetailSerializer(serializers.ModelSerializer):
    """ Сериалайзер для вывода и обновления информации об отдельной организации """

    contacts = ContactsSerializerCustom(many=True, read_only=True)
    products = ProductSerializerCustom(many=True, read_only=True)

    class Meta:
        model = NetworkNode
        fields = ['id', 'name', 'contacts', 'products', 'supplier', 'debt_amount', 'creation_time', 'level']
        validators = [SupplierValidator()]

    def validate_supplier(self, value):
        """ Проверка, что организация не ссылается на себя как на своего поставщика """
        if self.instance == value:
            raise serializers.ValidationError("An organisation cannot be its own supplier.")

    def validate_debt_amount(self, value):
        """Запрет на изменения поля 'debt_amount' по API"""
        raise serializers.ValidationError("This field is restricted to be changed.")
