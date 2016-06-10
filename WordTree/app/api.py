"""
Definition of API.
"""

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import redirect
from django.http import HttpRequest, Http404, JsonResponse

import logging

import app.api_impl

logger = logging.getLogger(__name__)

@login_required
@permission_required(['app.add_menu', 'app.add_submenu'])
def menu_api_add(request, menu):
    '''
    URL=/menu/id1/id2.../?name=new_name
    API returns JSON response containing new item's id.
    e.g. { 'id': 1, 'name': 'new_name' }
    '''
    if request.method == 'POST':
        # Retrieve the /?name=<new_name> part of the request.
        new_name = request.GET.get('name')
        logger.info("api_menu_add('{0}', menu='{1}', new_name='{2}')".format(request.get_raw_uri(), menu, new_name))

        menupath = menu.split("/")[0:-1] if menu else ['1']

        return app.api_impl.menu_add(menupath[-1], new_name)
    else:
        return redirect('/menu/{0}/'.format(menu))
