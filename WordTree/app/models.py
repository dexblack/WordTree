"""
Definition of models.
"""

from django.db import models

# Create your models here.

class Menu(models.Model):
    #id = models.AutoField() # Implicitly added for all modelled objects
    name = models.CharField(max_length=50)
    tag = models.CharField(max_length=25)
    tag.db_index = True
    data = models.TextField(blank=True)

    def __unicode__(self):
        return u'{ id: %d, name: "%s", tag: "%s" }' % (self.id, self.name, self.tag)

class Submenu(models.Model):
    child = models.ForeignKey(Menu, related_name='children', on_delete=models.DO_NOTHING)
    child.primary_key = True
    parent = models.OneToOneField(Menu)
    ordinal = models.IntegerField(default=0)
    ordinal.db_index = True

    def __unicode__(self):
        return u'{ ordinal: %d, child_id: %d, parent_id: %d }' % (self.ordinal, self.child.id, self.parent.id)
