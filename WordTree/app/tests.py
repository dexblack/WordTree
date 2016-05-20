"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".
"""

import django
django.setup()

from django.test import TestCase
from django.contrib.auth.models import User
from app.views import menu_add, menu_edit

class ViewTests(TestCase):
    """Tests for the simple application views."""

    if django.VERSION[:2] >= (1, 7):
        # Django 1.7 requires an explicit setup() when running tests in PTVS
        @classmethod
        def setUpClass(cls):
            super(ViewTests, cls).setUpClass()
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


class MenuTests(TestCase):
    """Tests for the menu views."""
    def setUp(self):
        self.user = User.objects.create_user('dex2', 'dex@gmail.com', 'dex2')

    def test_menu_anonymous(self):
        """Tests the menu/1 page. With anonymous access, i.e. no login."""
        response = self.client.get('/menu/1/')
        self.assertRedirects(response, '/login/?next=/menu/1/', 302)

    def test_menu_auth_user(self):
        self.assertTrue(self.client.login(username='dex2', password='dex2'))
        self.assertIn('_auth_user_id', self.client.session)
        response = self.client.get('/menu/1/')
        self.assertContains(response, 'Menu', 2, 200)


class MenuOperationTests(TestCase):
    """
    Tests for the menu operations.
    'add_menu','add_submenu'
    'change_menu','change_submenu'
    'delete_menu','delete_submenu'

    19|7|add_menu|Can add menu
    20|7|change_menu|Can change menu
    21|7|delete_menu|Can delete menu
    22|8|add_submenu|Can add submenu
    23|8|change_submenu|Can change submenu
    24|8|delete_submenu|Can delete submenu
    """
    def setUp(self):
        # Every test needs specific user access permissions.
        self.user = User.objects.create_user('dex2', 'dex@gmail.com', 'dex2')
        self.user.user_permissions.add(19,20,21,22,23,24) # See list above in doc string.

    def test_menu_add(self):
        self.assertTrue(self.client.login(username='dex2', password='dex2'))
        self.assertIn('_auth_user_id', self.client.session)

        # Test menu_add() as if it were deployed at /menu/1/add/
        response = self.client.get('/menu/1/')
        self.assertContains(response, 'Menu', 2, 200)
        # Add a new top level menu item.
        response_get = self.client.get('/menu/1/add/', {'parent': '1', 'next': '1'})
        response_post_add = self.client.post('/menu/1/add/', {'parent': '1', 'name': 'Add1', 'next': '1'})
        # Check we're redirected back to the parent menu.
        self.assertEqual(response_post_add.status_code, 302)
        self.assertEqual(response_post_add.url, '/menu/1/')
        # Check the new menu item exists.
        response_get2 = self.client.get('/menu/1/3/')
        self.assertEqual(response_get2.status_code, 200)

    def test_menu_delete(self):
        self.test_menu_add()
        # Delete new menu item.
        response_del = self.client.get('/menu/1/3/delete/')
        self.assertEqual(response_del.status_code, 302)
        self.assertEqual(response_del.url, '/menu/1/')
        # Check that it is really gone.
        response_get2 = self.client.get('/menu/1/3/')
        self.assertEqual(response_get2.status_code, 404)

    def test_menu_edit(self):
        self.test_menu_add()
        # Modify the new item's text.
        response_post_edit = self.client.post('/menu/1/3/edit/', {'id': '3', 'name': 'Edit1', 'next': '1'})
        self.assertEqual(response_post_edit.status_code, 302)
        self.assertEqual(response_post_edit.url, '/menu/1/')
        # Check the update worked.
        response_get2 = self.client.get('/menu/1/3/')
        self.assertContains(response_get2, 'Edit1', 2, 200)
