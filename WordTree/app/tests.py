"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".
"""

import django
django.setup()

from django.test import TestCase
from django.utils.http import urlquote
from django.contrib.auth.models import User

from app.views import menu_add, menu_edit, change_parent
from app.models import Menu, Submenu
from app.api_impl import MenuItem, ChildMenu, gather_children

from xml.sax.saxutils import escape

import logging
import json

logger = logging.getLogger(__name__)

THE_APP_NAME = 'RU App'

def custom_escape(s):
    entities = { "'":'&#39;' }
    return escape(s, entities)

class ImplementationTests(TestCase):

    def test_MenuItem(self):
        """
        Confirm the operation of MenuItem.__str__()
        """
        menuitem = MenuItem(id=1, name='A', data='D')
        self.assertEqual(str(menuitem), "{'id': 1, 'name': 'A', 'data': 'D'}")

    def test_ChildMenu(self):
        """
        Confirm the operation of MenuItem.__str__()
        """
        menuitem = ChildMenu(id=2, name='A', data='D', parentid=1, ordinal=3)
        self.assertEqual(str(menuitem), "{'id': 2, 'name': 'A', 'data': 'D', 'parentid': 1, 'ordinal': 3}")

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
        self.assertContains(response, THE_APP_NAME, 1, 200)

    def test_contact(self):
        """Tests the contact page."""
        response = self.client.get('/contact/')
        self.assertContains(response, 'Contact', 1, 200)

    def test_about(self):
        """Tests the about page."""
        response = self.client.get('/about/')
        self.assertContains(response, 'About', 1, 200)


class MenuTests(TestCase):
    """Tests for the menu views."""
    def setUp(self):
        self.user = User.objects.create_user('dex2', 'dex@gmail.com', 'dex2')

    def test_no_menu(self):
        with self.assertRaises(Menu.DoesNotExist):
            Menu.objects.get(id=9999)

    def test_no_submenu(self):
        with self.assertRaises(Submenu.DoesNotExist):
            Submenu.objects.get(child=9999)


    def test_menu_anonymous(self):
        """Tests the menu/1 page. With anonymous access, i.e. no login."""
        response = self.client.get('/menu/1/')
        self.assertRedirects(response, '/login/?next=/menu/1/', 302)

    def test_menu_auth_user(self):
        self.assertTrue(self.client.login(username='dex2', password='dex2'))
        self.assertIn('_auth_user_id', self.client.session)
        response = self.client.get('/menu/1/')
        self.assertContains(response, THE_APP_NAME, 1, 200)


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

    def menu_add_item(self, parent, name):
        self.assertTrue(self.client.login(username='dex2', password='dex2'))
        self.assertIn('_auth_user_id', self.client.session)

        # Test menu_add() as if it were deployed at /menu/1/add/
        # This initial get operation is necessary
        # to force the creation of the root menu.
        response = self.client.get('/menu/1/')
        self.assertContains(response, THE_APP_NAME, 1, 200)
        # Add a new top level menu item.
        response_get = self.client.get('/menu/1/add/', {'parent': '1', 'next': '1'})
        self.assertContains(response_get, 'Parent', 1, 200)
        self.assertContains(response_get, 'Enter the menu name', 1, 200)
        self.assertContains(response_get, 'Add', 1, 200)
        self.assertContains(response_get, 'menu', 2, 200)
        response_post_add = self.client.post('/menu/1/add/', {'parent': parent, 'name': name, 'next': '1'})
        # Check we're redirected back to the parent menu.
        self.assertEqual(response_post_add.status_code, 302)
        self.assertEqual(response_post_add.url, '/menu/1/')

    def api_menu_add_item(self, parent, name):
        self.assertTrue(self.client.login(username='dex2', password='dex2'))
        self.assertIn('_auth_user_id', self.client.session)

        # Add a new menu item to the given parent menu.
        response_post_add = self.client.post('/menu/{0}/api_add/?name={1}'.format(parent, urlquote(name)))
        response_json = json.loads(response_post_add.content.decode('utf-8'))
        # Check that the JSON response text contains the expected two field names and the new name.
        self.assertEqual(response_json['name'], name)
        # Check the new menu item now exists at the correct URL.
        response_get2 = self.client.get('/menu/{0}/{1}/'.format(parent, response_json['id']))
        escaped_name = custom_escape(name)
        self.assertContains(response_get2, escaped_name, 1, 200)
        # This return value allows for writing adaptive tests.
        return response_json['id']

    def test_menu_add(self):
        self.menu_add_item('1', 'Add1')

    def test_api_menu_add(self):
        names = ["Add &<>:' -2", 'Add 1']
        for name in names:
            id = self.api_menu_add_item('1', name)
            # Check the new menu item now exists at the correct URL.
            response_get = self.client.get('/menu/1/{0}/'.format(id))
            escaped_name = custom_escape(name)
            self.assertContains(response_get, escaped_name, 1, 200)

    def test_menu_delete(self):
        self.test_menu_add()
        # Delete new menu item.
        response_del = self.client.get('/menu/1/2/delete/')
        self.assertEqual(response_del.status_code, 302)
        self.assertEqual(response_del.url, '/menu/1/')
        # Check that it is really gone.
        response_get2 = self.client.get('/menu/1/2/')
        self.assertEqual(response_get2.status_code, 404)

    def test_menu_edit(self):
        self.test_menu_add()
        # Retrieve the edit form.
        response_get_edit = self.client.get('/menu/1/2/edit/')
        self.assertContains(response_get_edit,'Enter the menu name', 1, 200)
        # Modify the new item's text.
        response_post_edit = self.client.post('/menu/1/2/edit/', {'id': '2', 'name': 'Edit1', 'next': '1'})
        self.assertEqual(response_post_edit.status_code, 302)
        self.assertEqual(response_post_edit.url, '/menu/1/')
        # Check the update worked.
        response_get2 = self.client.get('/menu/1/2/')
        self.assertContains(response_get2, 'Edit1', 1, 200)

    def setup_for_move_tests(self):
        id1 = self.api_menu_add_item('1', 'Test')
        id2 = self.api_menu_add_item(str(id1), 'Add1')
        id3 = self.api_menu_add_item(str(id1), 'Add2')

        children = gather_children(id1)
        self.assertEqual(children[0].id, id2)
        self.assertEqual(children[0].name, 'Add1')
        self.assertEqual(children[0].ordinal, 1)
        self.assertEqual(children[1].id, id3)
        self.assertEqual(children[1].name, 'Add2')
        self.assertEqual(children[1].ordinal, 2)

        return ['1', id1, id2, id3]

    def verify_move(self, id):
        children = gather_children(id[1])
        self.assertEqual(children[0].id, id[3])
        self.assertEqual(children[0].name, 'Add2')
        self.assertEqual(children[0].ordinal, 1)
        self.assertEqual(children[1].id, id[2])
        self.assertEqual(children[1].name, 'Add1')
        self.assertEqual(children[1].ordinal, 2)

    def test_menu_move_next(self):
        id = self.setup_for_move_tests()
        # Retrieve the edit form.
        response_post_edit = self.client.post('/menu/{0}/move_next/'.format('/'.join([str(id[0]), str(id[1]), str(id[2])])))
        self.assertEqual(response_post_edit.status_code, 302)
        self.assertEqual(response_post_edit.url, '/menu/{0}/'.format('/'.join([str(id[0]), str(id[1])])))
        # Check the update worked.
        self.verify_move(id)

    def test_menu_move_prev(self):
        id = self.setup_for_move_tests()
        # Retrieve the edit form.
        response_post_edit = self.client.post('/menu/{0}/move_prev/'.format('/'.join([str(id[0]), str(id[1]), str(id[3])])))
        self.assertEqual(response_post_edit.status_code, 302)
        self.assertEqual(response_post_edit.url, '/menu/{0}/'.format('/'.join([str(id[0]), str(id[1])])))
        # Check the update worked.
        self.verify_move(id)

    def create_menu_structure(self):
        # Create a simple two element menu structure
        # /M1
        #  /M3
        # /M2
        #  /M4
        #   /M5
        id1 = self.api_menu_add_item('1', 'M1')
        id2 = self.api_menu_add_item('1', 'M2')
        id3 = self.api_menu_add_item('/'.join(['1', str(id1)]), 'M3')
        id4 = self.api_menu_add_item('/'.join(['1', str(id2)]), 'M4')
        id5 = self.api_menu_add_item('/'.join(['1', str(id2), str(id4)]), 'M5')
        # The returned structure has an implicit root node 'id':'1', 'name':'RU App'
        return {THE_APP_NAME:'1', 'children': [
                {'M1':id1, 'children': [
                 {'M3':id3 } ] },
                {'M2':id2, 'children': [
                 {'M4':id4, 'children': [
                  {'M5':id5 }] }] }] }

    def test_menu_change_parent(self):
        c='children'
        themenu = self.create_menu_structure()
        # Retrieve the change parent form.
        # moving M5
        m5id = themenu[c][1][c][0][c][0]['M5']

        m5url = '/menu/{0}/change_parent/'.format('/'.join(
            [str(i) for i in [themenu[THE_APP_NAME],
             themenu[c][1]['M2'],
             themenu[c][1][c][0]['M4'],
             m5id]]))

        # to new parent M1
        m1id = themenu[c][0]['M1']
        m1url = '/menu/{0}/'.format('/'.join(
            [str(i) for i in [themenu[THE_APP_NAME],themenu[c][0]['M1']]]))

        response_post_edit = self.client.post(m5url, {'id':str(m5id), 'name':'M5', 'parentid':str(m1id)})
        self.assertEqual(response_post_edit.status_code, 302)
        self.assertEqual(response_post_edit.url, m1url)
        # Check the update actually worked
        # by verifying that M5 appears in menu M1 now
        response_get2 = self.client.get(m1url)
        self.assertContains(response_get2, 'M5', 2, 200)
        # Verify that the ordinal of M5 was adjusted correctly.
        children = gather_children(m1id)
        self.assertEqual(children[1].id, m5id)
        self.assertEqual(children[1].name, 'M5')
        self.assertEqual(children[1].ordinal, 2)
