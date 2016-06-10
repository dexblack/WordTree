"""
Definition of urls for WordTree.
"""

from datetime import datetime
from django.conf.urls import url
from django.contrib.auth.views import login, logout
from app.forms import BootstrapAuthenticationForm
from app.views import THIS_APP_NAME, \
    home, contact, about, rootmenu, menu, \
    menu_add, menu_delete, menu_edit, menu_report, \
    move_next, move_prev, change_parent

from app.api import \
    menu_api_add

# Uncomment the next lines to enable the admin:
from django.conf.urls import include
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    # Examples:
    url(r'^$', home, name='home'),
    url(r'^contact/', contact, name='contact'),
    url(r'^about/', about, name='about'),
    url(r'^login/',
        login,
        {
            'template_name': 'app/login.html',
            'authentication_form': BootstrapAuthenticationForm,
            'extra_context':
            {
                'title':'Log in',
                'year':datetime.now().year,
                'this_app_name':THIS_APP_NAME
            }
        },
        name='login'),
    url(r'^logout/',
        logout,
        {
            'next_page': '/',
        },
        name='logout'),

    url(r'^report/', menu_report, name='report'),

    # Menu view URLs
    url(r'^menu/(?P<menu>(\d+/)+)$', menu, name='menu'),
    url(r'^menu/(?P<menu>(\d+/)+)add/$', menu_add, name='add'),
    url(r'^menu/(?P<menu>(\d+/)+)delete/$', menu_delete, name='delete'),
    url(r'^menu/(?P<menu>(\d+/)+)edit/$', menu_edit, name='edit'),
    url(r'^menu/(?P<menu>(\d+/)+)move_next/$', move_next, name='next'),
    url(r'^menu/(?P<menu>(\d+/)+)move_prev/$', move_prev, name='prev'),
    url(r'^menu/(?P<menu>(\d+/)+)change_parent/$', change_parent, name='change_parent'),

    # API URLs
    url(r'^menu/(?P<menu>(\d+/)+)api_add/', menu_api_add, name='menu_api_add'),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
]
