"""
API implementation.
"""

from django.http import JsonResponse
from django.db import transaction

import logging
from app.models import Menu, Submenu

logger = logging.getLogger(__name__)

# Permissions checks will already have been done
# This is an implementation only, never exposed directly.
def menu_add(parentid, new_name):
    logger.info("api_impl.menu_add(parentid={0}, new_name='{1}')".format(parentid, new_name))

    parentmenu = Menu.objects.get(id=int(parentid))

    with transaction.atomic():
        newmenu = Menu.objects.create(name=new_name, data='')
        submenu = Submenu.objects.create(parent=parentmenu, child=newmenu)
    #
    # Output is a JSON string built from this dict.
    #
    return JsonResponse({ 'id': newmenu.id, 'name': new_name })
