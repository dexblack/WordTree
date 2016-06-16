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
from app.forms import AddMenu, EditMenu, ChangeParent
import app.api_impl as api

# Get an instance of a logger
logger = logging.getLogger(__name__)

THIS_APP_NAME = 'Editor Prototype'
THIS_APP_VERSION = [0,9,4]

def render_app_page(**kwargs):
    try:
        kwargs["context_instance"]['title'] = THIS_APP_NAME
        kwargs["context_instance"]["this_app_name"] = THIS_APP_NAME
        kwargs["context_instance"]["this_app_ver"] = '.'.join([str(x) for x in THIS_APP_VERSION])
        kwargs["context_instance"]["year"] = datetime.now().year

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



def rootmenu(request):
    return redirect("/menu/1/")

@login_required
def menu(request, menu):
    """ Renders the given menu with links for the children. """
    assert isinstance(request, HttpRequest)
    logger.info("menu('{0}', menu={1})".format(request.get_raw_uri(), menu))
    chosenmenu = None
    try:
        # Retrieve the last menu id in the URL fragment.
        menupath = menu.split("/")[0:-1] if menu else ['1']
        depth = len(menupath)
        menuid = menupath[-1]
        chosenid = int(menuid)
        # Retrieve the corresponding Menu object.
        chosenmenu = Menu.objects.get(id=chosenid)

    except ValueError:
        raise Http404("No menu found at: " + request.get_raw_uri() + "menu: " + menu)

    except Menu.DoesNotExist:
        if chosenid == 1:
            # Initialise the root menu given that it doesn't exist yet
            try:
                rootmenu = Menu(name='RU App', data='')
                rootmenu.save()
                chosenmenu = rootmenu

            except IntegrityError:
                raise Http404("Database initialisation error")
        else:
            raise Http404("Invalid menu: '" + menu + "'")

    # and its children
    children = api.gather_children(parentid=chosenmenu.id)

    # Package the results in the appropriate structures
    return render_app_page(
        request=request,
        template_name='menu.html',
        context_instance = RequestContext(
            request=request,
            dict_={
                'menu' : chosenmenu.name,
                'parent' : '/'.join(menupath[0:-1]),
                'depth' : depth,
                'children' : children,
                'last' : api.initialise_ordinals(children),
                'order' : range(len(children))
            })
        )


@login_required
@permission_required(['app.add_menu', 'app.add_submenu'])
def menu_add(request, menu):
    # if this is a POST request we need to process the form data
    logger.info("menu_add('{0}', menu={1})".format(request.get_raw_uri(), menu))
    if request.method == 'POST':
        # create a form instance and populate it with data from the request
        form = AddMenu(request.POST)
        if form.is_valid():
            # discard the new id response here and redirect
            api.menu_add(parentid=form.cleaned_data['parent'], new_name=form.cleaned_data['name'])
            return redirect('/menu/{0}/'.format(form.cleaned_data['next']))
    else:
        # Retrieve the matching parent menu id being added to.
        menupath = menu.split("/")[0:-1] if menu else ['1']

        form = AddMenu({
            'parent': menupath[-1],
            'next': '/'.join(menupath)
        })

    return render_app_page(
        request=request,
        template_name='menu_add.html',
        context={'form':form}
        )

#def menu_edit_root(request):
#    return menu_edit(request, menu=None, child=None)

@login_required
@permission_required(['app.change_menu', 'app.change_submenu'])
def menu_edit(request, menu):
    logger.info("menu_edit('{0}', menu={1})".format(request.get_raw_uri(), menu))

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
            # Retrieve the matching menu id being edited.
            menupath = menu.split("/")[0:-1]
            menuid = int(menupath[-1])
            if menuid == 1:
                # Do nothing. Do not edit the root node.
                return redirect('/menu/1/')

            chosenmenu = Menu.objects.get(id=menuid)

        except ValueError:
            raise Http404("No menu matching: " + request.get_raw_uri() + "menu: " + menu)

        except Menu.DoesNotExist:
            raise Http404("Invalid menu: '" + menu)

        # Initialise the form with this menu's details
        form = EditMenu({
            'id':menupath[-1],
            'name':chosenmenu.name,
            'next': '/'.join(menupath[0:-1])
        })

    return render_app_page(
        request=request,
        template_name='menu_edit.html',
        context={'form':form}
        )


@login_required
@permission_required(['app.delete_menu', 'app.delete_submenu'])
def menu_delete(request, menu):
    """ Removes the given menu and all its children """
    assert isinstance(request, HttpRequest)
    logger.info("menu_delete('{0}', menu={1})".format(request.get_raw_uri(), menu))
    try:
        # Retrieve the last menu id in the URL fragment.
        menupath = menu.split("/")[0:-1] if menu else ['1']
        menuid = int(menupath[-1])
        if menuid == 1:
            # Do nothing. Do not delete the root node.
            return redirect('/menu/1/')
        # Only descendants of the root node can be deleted.
        assert(len(menupath) > 1)
        parentid = int(menupath[-2])
        # Retrieve the corresponding Menu object.
        # This also ensures we're deleting an existing item.
        chosenmenu = Menu.objects.get(id=menuid)
        chosensubmenu = Submenu.objects.get(child_id=chosenmenu.id)

    except ValueError:
        raise Http404("No menu matching: " + request.get_raw_uri() + "menu: " + menu)

    except Menu.DoesNotExist:
        raise Http404("Invalid menu: '" + menu)

    # and delete all its descendants
    descendants = api.gather_all_descendants(chosenid=menuid, postorder=True)
    descendants.append(api.ChildMenu(id=menuid, name=chosenmenu.name, data=chosenmenu.data, parentid=parentid))

    with transaction.atomic():
        for descendant in descendants:
            # First find the parent Menu
            parentmenu = Menu.objects.get(id=descendant.parentid)
            # Select the matching Submenu record.
            submenu = Submenu.objects.get(child_id=descendant.id)
            # There should only be one.
            logger.info('Deleting Submenu: parent:{0} id:{1}'.format(parentmenu.id, submenu.child.id))
            submenu.delete()
            # Select the matching Menu record for that child.
            themenu = Menu.objects.get(id=descendant.id)
            logger.info('Deleting Menu: {0} {1}'.format(themenu.id, themenu.name))
            # Again there ought to be only one.
            themenu.delete()

        # Adjust ordinals of the parent's children.
        api.initialise_ordinals_of(parentid, startat=chosensubmenu.ordinal)

    return redirect('/menu/{0}/'.format('/'.join(menupath[0:-1])))


@login_required
@permission_required(['app.change_menu', 'app.change_submenu'])
def move_next(request, menu):
    """
    Swap given menu item with next one in the parent menu's children.
    If at end, do nothing.
    Redisplay parent menu.
    """
    menupath = menu.split("/")[0:-1]
    if len(menupath) > 1:
        # get the ordering right
        children = api.gather_children(int(menupath[-2]))
        last = api.initialise_ordinals(children)
        # iterate over the list and find a match for menupath[-1].
        next = 0
        with transaction.atomic():
            for child in children:
                if child.id == int(menupath[-1]):
                    submenu = Submenu.objects.get(child=child.id)
                    # if it is already the last one do nothing.
                    if submenu.ordinal == last:
                        break
                    else:
                        next = submenu.ordinal + 1
                        submenu.ordinal = next
                        submenu.save()
                elif next > 0:
                    # the previous iteration matched the item to be moved down,
                    # so change this next item's ordinal accordingly.
                    submenu = Submenu.objects.get(child=child.id)
                    submenu.ordinal = next - 1
                    submenu.save()
                    break

            return redirect('/menu/{0}/'.format('/'.join(menupath[0:-1])))
    else:
        # cannot reposition the root menu.
        return redirect(menu)

@login_required
@permission_required(['app.change_menu', 'app.change_submenu'])
def move_prev(request, menu):
    """
    Swap given menu item with previous one in the parent menu's children.
    If at beginning, do nothing.
    Redisplay parent menu.
    """
    menupath = menu.split("/")[0:-1] if menu else ['1']
    if len(menupath) > 1:
        # gather the children of this menu's parent.
        children = api.gather_children(int(menupath[-2]))
        # check the ordinal values and then initialise them if 0.
        last = api.initialise_ordinals(children)
        # iterate over the list and find a match for menupath[-1].
        prev = 0
        with transaction.atomic():
            # traverse the child list backwards
            # to preserve the move_next algorithm's pattern
            # and to make it simpler to understand.
            for child in reversed(children):
                if child.id == int(menupath[-1]):
                    submenu = Submenu.objects.get(child=child.id)
                    # if it is already the first one do nothing.
                    if submenu.ordinal == 1:
                        break
                    else:
                        prev = submenu.ordinal - 1
                        submenu.ordinal = prev
                        submenu.save()
                elif prev > 0:
                    # the previous iteration matched the item to be moved up,
                    # so change this next item's ordinal accordingly.
                    submenu = Submenu.objects.get(child=child.id)
                    submenu.ordinal = prev + 1
                    submenu.save()
                    break

            return redirect('/menu/{0}/'.format('/'.join(menupath[0:-1])))
    else:
        # cannot reposition the root menu.
        return redirect(menu)

@login_required
@permission_required(['app.change_submenu'])
def change_parent(request, menu):
    """
    Display the edit parent form that allows altering the parent id directly.
    """
    logger.info("menu_change_parent('{0}', menu={1})".format(request.get_raw_uri(), menu))

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request
        form = ChangeParent(request.POST)
        if form.is_valid():
            menuid = form.cleaned_data['id']
            parentid = form.cleaned_data['parentid']
            with transaction.atomic():
                submenu = Submenu.objects.get(child=int(menuid))
                parent = Menu.objects.get(id=int(parentid))
                # adjust ordinal to put this new item at the end.
                ordinal = len(api.gather_children(parentid=parentid)) + 1
                submenu.parent = parent
                submenu.ordinal = ordinal
                submenu.save()
            # redirect to new parent menu.
            try:
                ancestors = api.gather_ancestors(menuid=parent.id)
            except Submenu.DoesNotExist:
                return Http404('Missing menu item')
            parents = []
            for ancestor in ancestors:
                parents.append(str(ancestor.id))
            target_fragment = '/menu/{0}/'.format('/'.join(parents))
            return redirect(target_fragment)
    else:
        try:
            # Retrieve the matching menu id being edited.
            menupath = menu.split("/")[0:-1]
            menuid = int(menupath[-1])
            if menuid == 1:
                # Do nothing. Do not edit the root node.
                return redirect('/menu/1/')

            chosenmenu = Menu.objects.get(id=menuid)

        except ValueError:
            raise Http404("No menu matching: " + request.get_raw_uri() + "menu: " + menu)

        except Menu.DoesNotExist:
            raise Http404("Invalid menu: '" + menu)

        # Initialise the form with this menu's details
        form = ChangeParent({
            'id':menupath[-1],
            'name':chosenmenu.name,
            'parentid':menupath[-2]
        })

    return render_app_page(
        request=request,
        template_name='menu_change_parent.html',
        context={'form':form}
        )

@login_required
def menu_report(request):
    """ Renders the complete menu report. """
    assert isinstance(request, HttpRequest)
    #raise Http404("Debugging: " + request.get_raw_uri() + " menu:" + menu + " child:" + child)

    # and its children
    report = api.build_report()

    return render_app_page(
        request=request,
        template_name='menu_report.html',
        context_instance = RequestContext(
            request=request,
            dict_={
                'title': 'Menu Report',
                'report': report,
            })
        )
