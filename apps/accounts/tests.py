from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class AccountViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_logout_redirects_to_index(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('accounts:logout'))
        self.assertRedirects(response, reverse('index'))
