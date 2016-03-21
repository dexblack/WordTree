"""
Definition of views.
"""

from django.shortcuts import render
from django.http import HttpRequest, Http404
from django.template import RequestContext
from django.db.utils import IntegrityError
from datetime import datetime
from app.models import Menu, Submenu

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        context_instance = RequestContext(request,
        {
            'title':'Home Page',
            'year':datetime.now().year,
        })
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        context_instance = RequestContext(request,
        {
            'title':'Contact',
            'message':'Your contact page.',
            'year':datetime.now().year,
        })
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        context_instance = RequestContext(request,
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        })
    )


def menu(request, submenu):
    """Renders the given menu item and shows links for the children"""
    assert isinstance(request, HttpRequest)
    try:
        menuid = int(submenu)
        menuid = menuid + 1
    except ValueError:
        raise Http404("No menu found")
    try:
        # Retrieve the matching submenu
        menu = Menu.objects.get(id=menuid)
    except Menu.DoesNotExist:
        if menuid == 1:
            # Initialise the root menu given that it doesn't exist yet
            try:
                menu = Menu(name='RU App', tag='root', data='')
                menu.save()
                menu2 = Menu(name='First', tag='first', data='')
                menu2.save()
                submenu1 = Submenu(parent=menu, ordinal=1, child=menu2)
                submenu1.save()
            except IntegrityError:
                raise Http404("Database initialisation error")
        else:
            raise Http404("Invalid menu id")

    # and its children
    class ChildMenu:
        def __init__(self, id, parent, name, tag, data):
            self.id = id
            self.parent = parent
            self.name = name
            self.tag = tag
            self.data = data

    submenus = Submenu.objects.filter(parent=menu).order_by('ordinal')
    children = []
    for submenu in submenus:
        menuitem = Menu.objects.get(id=submenu.child.id)
        childmenu = ChildMenu(id=submenu.child.id, parent=menu.id, name=menuitem.name, tag=menuitem.tag, data=menuitem.data)
        children.append(childmenu)

    # Package the results in the appropriate structures
    return render(request,
        'app/menu.html',
        context_instance = RequestContext(
            request,
            {
                'title':menu.name,
                'parent':menu,
                'children':children,
            }
        )
    )