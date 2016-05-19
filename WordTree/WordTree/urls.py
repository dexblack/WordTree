"""
Definition of urls for WordTree.
"""

from datetime import datetime
from django.conf.urls import url
from django.contrib.auth.views import login, logout
from app.forms import BootstrapAuthenticationForm
from app.views import home, contact, about, rootmenu, menu, \
    menu_add_root, menu_add, \
    menu_delete, \
    menu_edit, menu_edit_root, \
    menu_report

# Uncomment the next lines to enable the admin:
from django.conf.urls import include
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    # Examples:
    url(r'^$', home, name='home'),
    url(r'^menu/$', rootmenu),
    url(r'^menu/(?P<menu>(\d+/)*)(?P<child>\d+)/$', menu, name='menu'),
    url(r'^menu/add/$', menu_add_root, name='add_root'),
    url(r'^menu/(?P<menu>(\d+/)*)(?P<child>\d+)/add/$', menu_add, name='add'),
    url(r'^menu/(?P<menu>(\d+/)*)(?P<child>\d+)/delete/$', menu_delete, name='delete'),
    url(r'^menu/edit/$', menu_edit_root, name='menu_edit_root'),
    url(r'^menu/(?P<menu>(\d+/)*)(?P<child>\d+)/edit/$', menu_edit, name='edit'),
    url(r'^report/$', menu_report, name='report'),
    url(r'^contact/$', contact, name='contact'),
    url(r'^about/', about, name='about'),
    url(r'^login/$',
        login,
        {
            'template_name': 'app/login.html',
            'authentication_form': BootstrapAuthenticationForm,
            'extra_context':
            {
                'title':'Log in',
                'year':datetime.now().year,
            }
        },
        name='login'),
    url(r'^logout/$',
        logout,
        {
            'next_page': '/',
        },
        name='logout'),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
]
