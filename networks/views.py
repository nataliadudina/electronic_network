from django.db.models import Count
from rest_framework import viewsets, generics
from rest_framework.filters import SearchFilter

from networks.models import NetworkNode, Product, Contacts
from networks.pagination import CustomPaginator
from networks.serializers import NetworkNodeSerializer, ContactsSerializer, NetworkNodeDetailSerializer, \
    ProductSerializer, NetworkNodeCreateSerializer


class ProductViewSet(viewsets.ModelViewSet):
    """ API эндпоинт для управления продуктами """
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    pagination_class = CustomPaginator


class ContactsViewSet(viewsets.ModelViewSet):
    """ API эндпоинт для управления контактами """
    serializer_class = ContactsSerializer
    queryset = Contacts.objects.all()
    pagination_class = CustomPaginator


class NetworkNodeAPIView(generics.ListCreateAPIView):
    """ API эндпоинт для получения списка и создания узлов сети """
    queryset = NetworkNode.objects.all()
    filter_backends = [SearchFilter]
    search_fields = ['contacts__country']
    pagination_class = CustomPaginator

    def get_serializer_class(self):
        """ Определяет класс сериализатора в зависимости от метода запроса """
        if self.request.method == 'POST':
            return NetworkNodeCreateSerializer
        elif self.request.method in ['GET']:
            return NetworkNodeSerializer

    def get_queryset(self):
        """ Добавляет аннотацию к queryset с количеством связанных продуктов """
        queryset = super().get_queryset()
        queryset = queryset.annotate(
            items_quantity=Count('products')
        )
        return queryset


class NetworkNodeRetrieveAPIView(generics.RetrieveUpdateDestroyAPIView):
    """ API эндпоинт для получения, обновления и удаления конкретного узла сети """
    serializer_class = NetworkNodeDetailSerializer
    queryset = NetworkNode.objects.all()
