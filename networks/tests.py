from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from networks.models import Product, Contacts, NetworkNode


class NetworkNodeTestCase(APITestCase):
    """ Тестирование модели узла сети """

    def setUp(self) -> None:
        self.client = APIClient()

        # Создание экземпляров продуктов и контактов
        self.product1 = Product.objects.create(name='Product 1', model='M-1000', release_date='2020-09-05')
        self.product2 = Product.objects.create(name='Product 2', model='M-2000', release_date='2020-10-05')

        self.contacts1 = Contacts.objects.create(email='info@factory.com', country='Russia', city='Moscow')
        self.contacts2 = Contacts.objects.create(email='sales@factory.com', country='Russia', city='Moscow')

        # Создание экземпляров узлов сети
        self.network_node1 = NetworkNode.objects.create(
            name='Factory',
            debt_amount=0.00,
            creation_time=timezone.now(),
            level=0
        )
        self.network_node1.contacts.add(self.contacts1.pk)
        self.network_node1.products.add(self.product1, self.product2)

        self.network_node2 = NetworkNode.objects.create(
            name='Retail',
            supplier=self.network_node1,
            debt_amount=0.00,
            creation_time=timezone.now(),
            level=1
        )
        self.network_node2.contacts.add(self.contacts2.pk)
        self.network_node2.products.add(self.product1)

    def test_create_network_node(self):
        """ Тестирование создания узла сети """

        data = {
            'name': 'New Factory',
            'contacts': [self.contacts1.pk],
            'products': [self.product1.pk],
            'debt_amount': 0.00,
            'creation_time': '2022-09-05',
            'level': 0
        }
        response = self.client.post(reverse('networks:networks-list-create'), data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(response.data['name'], data['name'])
        self.assertEqual(response.data['level'], data['level'])
        self.assertTrue(NetworkNode.objects.all().exists())

    def test_factory_debt(self):
        """ Тестирование валидации задолженности у завода: у завода не может быть задолженности """

        data = {
            'name': 'Factory1',
            'contacts': [self.contacts2.pk],
            'products': [self.product2.pk],
            'debt_amount': 1.00,
            'creation_time': '2022-09-05',
            'level': 0
        }
        response = self.client.post(reverse('networks:networks-list-create'), data=data)

        self.assertIn("The factory cannot be in debt as it has no supplier.", response.content.decode())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_network_node(self):
        """ Тестирование редактирования узла сети """

        network_data = {
            'name': 'Best Factory'
        }

        url = reverse('networks:network-detail', kwargs={'pk': self.network_node1.pk})
        response = self.client.patch(url, data=network_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], network_data['name'])

    def test_update_supplier(self):
        """ Тестирование редактирования поля 'supplier' """

        network_data = {
            'supplier': self.network_node1
        }

        url = reverse('networks:network-detail', kwargs={'pk': self.network_node1.pk})
        response = self.client.patch(url, data=network_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validate_supplier(self):
        """ Тестирование валидации поля 'supplier': у ретейла и ИП должен быть поставщик """

        network_data = {
            'level': 1,
            'supplier': []
        }

        url = reverse('networks:network-detail', kwargs={'pk': self.network_node2.pk})
        response = self.client.patch(url, data=network_data)

        self.assertIn("Retail or Consumer must have a supplier.", response.content.decode())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_network_nodes(self):
        """ Вывод списка узлов сети """

        response = self.client.get(reverse('networks:networks-list-create'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data['results']), 2)

        network_names = [node['name'] for node in response.data['results']]
        self.assertIn('Factory', network_names)
        self.assertIn('Retail', network_names)

    def test_delete_network_node(self):
        """ Тестирование удаления узла сети """

        url = reverse('networks:network-detail', kwargs={'pk': self.network_node1.id})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(NetworkNode.DoesNotExist):
            NetworkNode.objects.get(id=self.network_node1.id)


class ProductTestCase(APITestCase):
    """ Тестирование модели продукта """

    def setUp(self) -> None:
        self.client = APIClient()
        self.product1 = Product.objects.create(name='Product 1', model='M-1000', release_date='2020-09-05')
        self.product2 = Product.objects.create(name='Product 2', model='M-2000', release_date='2020-10-05')

    def test_create_product(self):
        """ Тестирование создания продукта """

        data = {
            'name': 'Test Product',
            'model': 'Test Model',
            'release_date': '2024-09-05',
            'sales_channel': []
        }
        response = self.client.post('/products/', data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(response.data['name'], data['name'])
        self.assertEqual(response.data['model'], data['model'])
        self.assertTrue(Product.objects.all().exists())

    def test_update_product(self):
        """ Тестирование редактирования продукта """

        product_data = {
            'model': 'M-1001'
        }
        response = self.client.patch(reverse('networks:products-detail', kwargs={'pk': self.product1.pk}),
                                     data=product_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['model'], product_data['model'])

    def test_list_products(self):
        """ Вывод списка продуктов """

        response = self.client.get(reverse('networks:products-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data['results']), 2)

        product_names = [product['name'] for product in response.data['results']]
        self.assertIn('Product 1', product_names)
        self.assertIn('Product 2', product_names)

    def test_read_product(self):
        """ Тестирование просмотра продукта """
        response = self.client.get(reverse('networks:products-detail', kwargs={'pk': self.product2.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['name'], 'Product 2')
        self.assertEqual(response.data['model'], 'M-2000')

    def test_delete_product(self):
        """ Тестирование удаления продукта """
        url = reverse('networks:products-detail', kwargs={'pk': self.product1.id})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(Product.DoesNotExist):
            Product.objects.get(id=self.product1.id)


class ContactsTestCase(APITestCase):
    """ Тестирование модели контактов """

    def setUp(self) -> None:
        self.client = APIClient()
        self.contacts1 = Contacts.objects.create(email='info@factory.com', country='Russia', city='Moscow')
        self.contacts2 = Contacts.objects.create(email='sales@factory.com', country='Russia', city='Moscow')

    def test_create_contacts(self):
        """ Тестирование создания контактов """
        data = {
            'email': 'production@factory.com',
            'country': 'Russia',
            'city': 'Moscow'
        }
        response = self.client.post('/contacts/', data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(response.data['email'], data['email'])
        self.assertEqual(response.data['country'], data['country'])

        self.assertTrue(Contacts.objects.all().exists())

    def test_update_contacts(self):
        """ Тестирование редактирования контактов """

        contacts_data = {
            'email': 'prod@factory.com'
        }
        response = self.client.patch(reverse('networks:contacts-detail', kwargs={'pk': self.contacts1.pk}),
                                     data=contacts_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], contacts_data['email'])

    def test_list_contacts(self):
        """ Вывод списка контактов """

        response = self.client.get(reverse('networks:contacts-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data['results']), 2)

        contacts_emails = [contacts['email'] for contacts in response.data['results']]
        self.assertIn('info@factory.com', contacts_emails)
        self.assertIn('sales@factory.com', contacts_emails)

    def test_read_contacts(self):
        """ Тестирование просмотра одной записи контактов """
        response = self.client.get(reverse('networks:contacts-detail', kwargs={'pk': self.contacts2.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['email'], 'sales@factory.com')
        self.assertEqual(response.data['country'], 'Russia')

    def test_delete_contacts(self):
        """ Тестирование удаления контактов """
        url = reverse('networks:contacts-detail', kwargs={'pk': self.contacts1.id})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(Contacts.DoesNotExist):
            Contacts.objects.get(id=self.contacts1.id)
