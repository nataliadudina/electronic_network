from django.urls import path, include
from rest_framework.routers import DefaultRouter

from networks.apps import NetworksConfig
from networks.views import NetworkNodeAPIView, ProductViewSet, ContactsViewSet, NetworkNodeRetrieveAPIView

app_name = NetworksConfig.name

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='products')
router.register(r'contacts', ContactsViewSet, basename='contacts')

urlpatterns = [
    path('', include(router.urls)),
    path('networks/', NetworkNodeAPIView.as_view(), name='networks-list-create'),
    path('networks/<int:pk>/', NetworkNodeRetrieveAPIView.as_view(), name='network-detail'),
]
