from django.test import Client, TestCase
from django.urls import reverse_lazy


# Create your tests here.
class TemplatesTest(TestCase):
    """Testes para páginas públicas (não requerem login)"""

    def setUp(self):
        self.client = Client()

    def test_home_page_loads(self):
        """Testa se a página inicial carrega"""
        response = self.client.get(reverse_lazy('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
