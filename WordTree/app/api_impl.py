"""
API implementation.
"""

from django.http import JsonResponse
from django.db import transaction

import logging
from app.models import Menu, Submenu

logger = logging.getLogger(__name__)

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
    def __init__(self, parentid, id, name, data):
        self.parentid = parentid
        super(ChildMenu, self).__init__(id=id, name=name, data=data)

    def __str__(self):
        return "{'parent':{0}, 'id':{1}, 'name':{2}, 'data':{3} }".format(self.parent, str(super(ChildMenu, self)))

def gather_children(parentid):
    '''
    Returns a list of ChildMenu objects which are
    the direct first level descendants of Menu 'parentid'.
    '''
    # parentid must be > 0.
    if parentid < 1:
        return []
    # parentid must correspond to an existing menu item.
    parentmenu = Menu.objects.get(id=parentid)

    children = []
    submenus = Submenu.objects.filter(parent=parentid).order_by('child_id')
    for submenu in submenus:
        menu = Menu.objects.get(id=submenu.child.id)
        childmenu = ChildMenu(parentid=int(parentmenu.id), id=int(menu.id), name=menu.name, data=menu.data)
        children.append(childmenu)

    return children

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

def initialise_ordinals(parentid):
    logger.info("api_impl.initialise_ordinals(parentid={0}')".format(parentid))
    # Get children.
    # Iterate over children setting ordinal value
