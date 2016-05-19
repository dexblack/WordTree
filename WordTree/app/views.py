"""
Definition of views.
"""
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect
from django.http import HttpRequest, Http404
from django.template import RequestContext
from django.db.utils import IntegrityError
from django.db import transaction

import logging
from datetime import datetime
from app.models import Menu, Submenu
from app.forms import AddMenu, EditMenu

# Get an instance of a logger
logger = logging.getLogger(__name__)

def render_app_page(**kwargs):
    try:
        kwargs["context_instance"]["this_app_name"] = "Editor prototype"
    except KeyError:
        pass
    kwargs["template_name"] = "app/" + kwargs["template_name"]
    return render(**kwargs)


def home(request):
    """ Renders the home page. """
    assert isinstance(request, HttpRequest)
    return render_app_page(
        request=request,
        template_name='index.html',
        context_instance = RequestContext(
            request=request,
            dict_={
                'title':'Home Page',
                'year':datetime.now().year,
            })
        )

def contact(request):
    """ Renders the contact page. """
    assert isinstance(request, HttpRequest)
    return render_app_page(
        request=request,
        template_name='contact.html',
        context_instance = RequestContext(
            request=request,
            dict_={
                'title':'Contact',
                'message':'Your contact page.',
                'year':datetime.now().year,
            })
        )

def about(request):
    """ Renders the about page. """
    assert isinstance(request, HttpRequest)
    return render_app_page(
        request=request,
        template_name='about.html',
        context_instance = RequestContext(
            request=request,
            dict_={
                'title':'About',
                'message':'R U Menu Editor Prototype.',
                'year':datetime.now().year,
            })
        )


class MenuItem(object):
    """
    Temporary data for gathering child menu items.
    This is effectively the output from a traversal of the tree
    which is intended to be stored in an (ordered) list.
    """
    def __init__(self, id, name, data):
        self.id = id
        self.name = name
        self.data = data

    def __str__(self):
        return "{{'id':{0}, 'name':{2}, 'data':{3} }}".format(self.id, self.parent, self.name, self.data if self.data else "")

class ChildMenu(MenuItem):
    """
    Temporary data for gathering child menu items.
    This is effectively the output from a traversal of the tree
    which is intended to be stored in an (ordered) list.
    """
    def __init__(self, parent, id, name, data):
        self.parent = parent
        super(ChildMenu, self).__init__(id=id, name=name, data=data)

    def __str__(self):
        return "{'parent':{0}, 'id':{1}, 'name':{2}, 'data':{3} }".format(self.parent, str(super(ChildMenu, self)))


def gather_children(parentid):
    """
    Returns a list of ChildMenu objects which are
    the direct first level descendants of Menu 'parentid'.
    """
    # parentid must be > 0.
    if parentid < 1:
        return []
    # parentid must correspond to an existing menu item.
    parentmenu = Menu.objects.get(id=parentid)

    children = []
    submenus = Submenu.objects.filter(parent=parentid).order_by('child_id')
    for submenu in submenus:
        menu = Menu.objects.get(id=submenu.child.id)
        childmenu = ChildMenu(parent=int(parentmenu.id), id=int(menu.id), name=menu.name, data=menu.data)
        children.append(childmenu)

    return children

def rootmenu(request):
    return redirect("/menu/1")

@login_required
def menu(request, menu, child):
    """ Renders the given menu with links for the children. """
    assert isinstance(request, HttpRequest)
    #raise Http404("Debugging: " + request.get_raw_uri() + " menu:" + menu + " child:" + child)
    chosenmenu = None
    menupath = []
    try:
        # Retrieve the matching submenu
        menupath = menu.split("/")[0:-1]

        # This is a consequence of the regex matching algorithm
        # used when parsing the application urls collection.
        chosenid = int(child if child else menu)

        chosenmenu = Menu.objects.get(id=chosenid)

    except ValueError:
        raise Http404("No menu found at: " + request.get_raw_uri() + "menu: " + menu + " child:" + (child if child else ""))

    except Menu.DoesNotExist:
        if chosenid == 1:
            # Initialise the root menu given that it doesn't exist yet
            try:
                rootmenu = Menu(name='RU App', data='')
                rootmenu.save()
                firstmenu = Menu(name='First Menu', data='')
                firstmenu.save()
                submenu = Submenu(parent=rootmenu, child=firstmenu)
                submenu.save()
                chosenmenu = rootmenu

            except IntegrityError:
                raise Http404("Database initialisation error")
        else:
            raise Http404("Invalid menu: '" + menu + "'")

    # and its children
    children = gather_children(chosenmenu.id)

    # Package the results in the appropriate structures
    return render_app_page(
        request=request,
        template_name='menu.html',
        context_instance = RequestContext(
            request=request,
            dict_={
                'title' : chosenmenu.name,
                'parent' : '/menu/' + '/'.join(menupath) + '/',
                'children' : children,
            })
        )

def menu_add_root(request):
    return menu_add(request, menu=None, child=None)

@login_required
@permission_required(['app.add_menu', 'app.add_submenu'])
def menu_add(request, menu, child):
    #raise Http404("Debugging: " + request.get_raw_uri() + " menu:" + menu + " child:" + child)
    # if this is a POST request we need to process the form data
    logger.info("menu_add('{0}', menu={1}, child={2})".format(request.get_raw_uri(), menu, child))
    if request.method == 'POST':
        # create a form instance and populate it with data from the request
        form = AddMenu(request.POST)
        if form.is_valid():
            parentid = form.cleaned_data['parent']
            name = form.cleaned_data['name']

            parentmenu = Menu.objects.get(id=int(parentid))

            with transaction.atomic():
                newmenu = Menu(name=name, data='')
                newmenu.save()
                submenu = Submenu(parent=parentmenu, child=newmenu)
                submenu.save()

            return redirect('/menu/{0}/'.format(form.cleaned_data['next']))
    else:
        # Retrieve the matching submenu
        menupath = menu.split("/")[0:-1]
        menupath = menupath[len(menupath)-1] if menupath else None 
        menupath = child or menupath or '1'
        form = AddMenu({'parent': menupath, 'next': menu + child})

    return render_app_page(request=request, template_name='menu_add.html',
                           context={'form':form})

def menu_edit_root(request):
    return menu_edit(request, menu=None, child=None)

@login_required
@permission_required(['app.change_menu', 'app.change_submenu'])
def menu_edit(request, menu, child):
    logger.info("menu_edit('{0}', menu={1}, child={2})".format(request.get_raw_uri(), menu, child))

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request
        form = EditMenu(request.POST)
        if form.is_valid():
            chosenid = form.cleaned_data['id']
            chosenmenu = Menu.objects.get(id=int(chosenid))
            chosenmenu.name = form.cleaned_data['name']
            chosenmenu.save()

            return redirect('/menu/{0}/'.format(form.cleaned_data['next']))
    else:
        try:
            chosenmenu = Menu.objects.get(id=int(child))

        except ValueError:
            raise Http404("No menu matching: " + request.get_raw_uri() + "menu: " + menu + " child:" + (child if child else ""))

        except Menu.DoesNotExist:
            raise Http404("Invalid menu: '" + menu)
        # Initialise the form with this menu's details
        form = EditMenu({'id':child, 'name':chosenmenu.name, 'next': menu})

    return render_app_page(request=request, template_name='menu_edit.html',
                           context={'form':form})

def gather_descendants(descendants, parentid, postorder=True, depth = -1):
    """
    Recursive post-order traversal of the tree.
    Stores the ChildMenu objects collected at each node
    in pre or post order.

    parentid: The menu item at which to begin the traversal.
    descendants: The output list of menu items.

    postorder: ==True is used for performing the delete branch operation.
    postorder: ==False Pre order is used for presentation (reporting) purposes.

    depth: ==-1 implies all children; == 0 is terminates the recursion.

    """
    # Don't include the parentid in the returned collection.
    if depth == 0:
        return
    elif depth > 0:
        depth = depth - 1

    # Gather the next descendants.
    children = gather_children(parentid=parentid)
    for child in children:
        # The order of operations here makes descendants a pre or post order list.
        if not postorder:
            descendants.append(child)
        gather_descendants(descendants=descendants, parentid=child.id, postorder=postorder, depth=depth)
        # The sequence will then be suitable for deleting children first.
        if postorder:
            descendants.append(child)
    # return the passed parameter for convenience.
    return descendants

def gather_all_descendants(chosenid, postorder):
    """
    Kick off the recursive descent of the menu tree.
    See gather_descendants for details of the postorder flag.
    """
    return gather_descendants(descendants=[], parentid=chosenid, postorder=postorder)


@login_required
@permission_required(['app.delete_menu', 'app.delete_submenu'])
def menu_delete(request, menu, child):
    """ Removes the given menu and all its children """
    #raise Http404("Debugging: " + request.get_raw_uri() + " menu:" + menu + " child:" + child)
    assert isinstance(request, HttpRequest)
    logger.info("menu_delete('{0}', menu={1}, child={2})".format(request.get_raw_uri(), menu, child))
    chosenmenu = None
    try:
        chosenid = int(child if child else menu)
        chosenmenu = Menu.objects.get(id=chosenid)

    except ValueError:
        raise Http404("No menu matching: " + request.get_raw_uri() + "menu: " + menu + " child:" + (child if child else ""))

    except Menu.DoesNotExist:
        raise Http404("Invalid menu: '" + menu)

    # and delete all its descendants
    descendants = gather_all_descendants(chosenid=chosenid, postorder=True)
    parentid = menu.split("/")[0:-1] if menu else None
    parentid = parentid[len(parentid)-1] if parentid else '1'

    todie = ChildMenu(parentid=int(parentid), id=int(chosenmenu.id), name=chosenmenu.name, data=chosenmenu.data)
    descendants.append(todie)

    with transaction.atomic():
        for descendant in descendants:
            # First find the parent Menu
            parentmenu = Menu.objects.get(id=descendant.parent)
            # Select the matching Submenu record.
            submenus = Submenu.objects.filter(parent=parentmenu, child_id=descendant.id)
            # There should only be one.
            assert(len(submenus)==1)
            submenu = submenus[0]
            logger.info('Deleting Submenu: parent:{0} id:{1}'.format(parentmenu.id, submenu.child.id))
            submenu.delete()
            # Select the matching Menu record for that child.
            themenu = Menu.objects.get(id=descendant.id)
            logger.info('Deleting Menu: {0} {1}'.format(themenu.id, themenu.name))
            # Again there ought to be only one.
            themenu.delete()

    return redirect('/menu/{0}/'.format(menu))


class Tree(MenuItem):
    """
    Temporary data for gathering the tree of menu items.
    """
    def __init__(self, id, name, data):
        super(Tree, self).__init__(id=id, name=name, data=data)
        self.branches = [] # A list of Tree nodes.

    def __str__(self):
        return str(super(Tree, self))


def build_tree(report, id):
    """
    Creates a Tree from the Menu/Submenu data.
    Counts the nodes as it traverses them.

    id: The menu item at which to begin the traversal.
    """
    try:
        menu = Menu.objects.get(id=id)
    except Menu.DoesNotExist:
        return []

    # Gather the next descendants.
    tree = Tree(id=menu.id, name=menu.name, data=menu.data)

    # Increment the count of nodes.
    report['count'] = report['count'] + 1

    # Traverse the children
    submenus = gather_children(parentid=id)
    for submenu in submenus:
        branch = build_tree(report, id=int(submenu.id))
        # Add each branch to the tree.
        tree.branches.append(branch)

    return tree

def build_report():
    """
    Construct a dictionary to hold the report results.
    This includes the Tree itself and a count of the nodes.
    """
    # Don't count the root node. Set count to -1 initially.
    report = { 'tree': None, 'count': -1 }
    # build_tree_from only updates the count member.
    report['tree'] = build_tree(report, id=1)
    return report

@login_required
def menu_report(request):
    """ Renders the complete menu report. """
    assert isinstance(request, HttpRequest)
    #raise Http404("Debugging: " + request.get_raw_uri() + " menu:" + menu + " child:" + child)

    # and its children
    report = build_report()

    return render_app_page(
        request=request,
        template_name='menu_report.html',
        context_instance = RequestContext(
            request=request,
            dict_={
                'title': 'Menu Report',
                'total': report['count'],
                'tree': report['tree'],
            })
        )
