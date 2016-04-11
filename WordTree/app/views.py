"""
Definition of views.
"""

from django.shortcuts import render, redirect
from django.http import HttpRequest, Http404
from django.template import RequestContext
from django.db.utils import IntegrityError
from django.db import transaction

from datetime import datetime
from app.models import Menu, Submenu
from .forms import AddMenu


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
    return redirect("menu/", menu="1", child="")

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
                rootmenu = Menu(name='RU App', data='')
                rootmenu.save()
                firstmenu = Menu(name='First', data='')
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
        def __init__(self, id, parent, name, data):
            self.id = id
            self.parent = parent
            self.name = name
            self.data = data

    submenus = Submenu.objects.filter(parent=chosenmenu).order_by('ordinal')
    children = []
    for submenu in submenus:
        menuitem = Menu.objects.get(id=submenu.child.id)
        childmenu = ChildMenu(id=submenu.child.id, parent=request.get_raw_uri(), name=menuitem.name, data=menuitem.data)
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
                'add' : "http://" + request.get_host() + '/menu/add/' + '/'.join(menupath),
            }
        )
    )

def menu_add_root(request):
    return menu_add(request, menu="1", child="")

def menu_add(request, menu, child):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request
        form = AddMenu(request.POST)
        if form.is_valid():
            parentid = form.cleaned_data['parent']
            name = form.cleaned_data['name']

            parentmenu = Menu.objects.get(id=int(parentid))
            childcount = len(Submenu.objects.filter(parent=parentmenu)) + 1

            with transaction.atomic():
                newmenu = Menu(name=name, data='')
                newmenu.save()
                submenu = Submenu(parent=parentmenu, ordinal=childcount, child=newmenu)
                submenu.save()

            return render(request, 'app/menu_added.html')
    else:
        form = AddMenu({'parent': (menu or '1'), 'name':'Add word'})

    return render(request, 'app/menu_add.html', {'form': form})
