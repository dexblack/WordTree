"""
Definition of urls for WordTree.
"""

from datetime import datetime
from django.conf.urls import url
from django.contrib.auth.views import login, logout
from app.forms import BootstrapAuthenticationForm
from app.views import home, contact, about, rootmenu, menu

# Uncomment the next lines to enable the admin:
# from django.conf.urls import include
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = [
    # Examples:
    url(r'^$', home, name='home'),
    url(r'^menu/$', rootmenu),
    url(r'^menu/(?P<menu>[\d/]*)(?P<child>\d{1,2})/$', menu, name='menu'),
    url(r'^contact$', contact, name='contact'),
    url(r'^about', about, name='about'),
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
    url(r'^logout$',
        logout,
        {
            'next_page': '/',
        },
        name='logout'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
]
