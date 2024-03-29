"""
Definition of models.
"""

from django.db import models

# Create your models here.

class Menu(models.Model):
    #id = models.AutoField() # Implicitly added for all modelled objects
    name = models.CharField(max_length=50)
    data = models.TextField(blank=True)

    def __unicode__(self):
        return u'{ "id": %d, "name": "%s"" }' % (self.id, self.name)

class Submenu(models.Model):
    child = models.OneToOneField(Menu, related_name='children')
    child.primary_key = True
    parent = models.ForeignKey(Menu)
    ordinal = models.PositiveSmallIntegerField(default=0)

    def __unicode__(self):
        return u'{ "parent_id": %d, "child_id": %d, "ordinal": %d }' % (self.parent.id, self.child.id, self.ordinal)

