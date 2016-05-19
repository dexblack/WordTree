"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".
"""

import django
django.setup()

from django.test import TestCase
from django.contrib.auth.models import User
#from django.contrib.auth.models import Group


# TODO: Configure your database in settings.py and sync before running tests.

class ViewTest(TestCase):
    """Tests for the application views."""

    if django.VERSION[:2] >= (1, 7):
        # Django 1.7 requires an explicit setup() when running tests in PTVS
        @classmethod
        def setUpClass(cls):
            super(ViewTest, cls).setUpClass()
            django.setup()

    def test_home(self):
        """Tests the home page."""
        response = self.client.get('/')
        self.assertContains(response, 'Home Page', 1, 200)

    def test_contact(self):
        """Tests the contact page."""
        response = self.client.get('/contact/')
        self.assertContains(response, 'Contact', 3, 200)

    def test_about(self):
        """Tests the about page."""
        response = self.client.get('/about/')
        self.assertContains(response, 'About', 3, 200)

class MenuTest(TestCase):
    """Tests for the menu views."""
    def setUp(self):
        user = User.objects.create_user('dex2', 'dex@gmail.com', 'dex2')

    def test_menu_anonymous(self):
        """Tests the menu/1 page. With anonymous access, i.e. no login."""
        response = self.client.get('/menu/1/')
        self.assertRedirects(response, '/login/?next=/menu/1/', 302)

    def test_menu_auth_user(self):
        self.assertTrue(self.client.login(username='dex2', password='dex2'))
        self.assertIn('_auth_user_id', self.client.session)
        response = self.client.get('/menu/1/')
        self.assertContains(response, 'Menu', 2, 200)