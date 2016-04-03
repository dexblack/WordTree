"""
Definition of views.
"""

from django.shortcuts import render, redirect
from django.http import HttpRequest, Http404
from django.template import RequestContext
from django.db.utils import IntegrityError
from datetime import datetime
from app.models import Menu, Submenu

def render_app_page(request, template_name, **kwargs):
    kwargs["context_instance"]["this_app_name"] = "RU App Editor prototype"
    template_name = "app/" + template_name
    return render(request, template_name, **kwargs)

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render_app_page(
        request,
        'index.html',
        context_instance = RequestContext(request,
        {
            'title':'Home Page',
            'year':datetime.now().year,
        })
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render_app_page(
        request,
        'contact.html',
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
    return render_app_page(
        request,
        'about.html',
        context_instance = RequestContext(request,
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        })
    )


def rootmenu(request):
    return redirect("menu", menu="1", child="")

def menu(request, menu, child):
    """Renders the given menu item and shows links for the children"""
    assert isinstance(request, HttpRequest)
    #raise Http404("Debugging: " + request.get_raw_uri() + " " + menu + " " + child)
    chosenmenu = None
    menupath = []
    try:
        # Retrieve the matching submenu
        menupath = menu.split("/")[0:-1]

        chosenid = child if child else menu
        chosenmenu = Menu.objects.get(id=int(chosenid))

    except ValueError:
        raise Http404("No menu found at: " + request.get_raw_uri() + "menu: " + menu + " child:" + (child if child else ""))

    except Menu.DoesNotExist:
        if chosenid == "1":
            # Initialise the root menu given that it doesn't exist yet
            try:
                rootmenu = Menu(name='RU App', tag='root', data='')
                rootmenu.save()
                firstmenu = Menu(name='First', tag='first', data='')
                firstmenu.save()
                submenu = Submenu(parent=rootmenu, ordinal=1, child=firstmenu)
                submenu.save()
                chosenmenu = rootmenu

            except IntegrityError:
                raise Http404("Database initialisation error")
        else:
            raise Http404("Invalid menu: '" + menu)

    # and its children
    class ChildMenu:
        def __init__(self, id, parent, name, tag, data):
            self.id = id
            self.parent = parent
            self.name = name
            self.tag = tag
            self.data = data

    submenus = Submenu.objects.filter(parent=chosenmenu).order_by('ordinal')
    children = []
    for submenu in submenus:
        menuitem = Menu.objects.get(id=submenu.child.id)
        childmenu = ChildMenu(id=submenu.child.id, parent=request.get_raw_uri(), name=menuitem.name, tag=menuitem.tag, data=menuitem.data)
        children.append(childmenu)

    # Package the results in the appropriate structures
    return render_app_page(
        request,
        'menu.html',
        context_instance = RequestContext(
            request,
            {
                'title' : chosenmenu.name,
                'parent' : "http://" + request.get_host() + '/menu/' + '/'.join(menupath),
                'children' : children,
            }
        )
    )