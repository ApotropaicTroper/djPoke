from __future__ import unicode_literals

from django.db import models

# Note about model fields
# =======================
# If you want to allow blank values in a date field (e.g., DateField, TimeField, 
# DateTimeField) or numeric field (e.g., IntegerField, DecimalField, FloatField), you'll 
# need to use both null=True and blank=True.

# Adding null=True is more complicated than adding blank=True, because null=True changes
# the semantics of the database -- that is, it changes the CREATE TABLE statement to 
# remove the NOT NULL from the publication_date field. To complete this change, we'll 
# need to update the database.

# For a number of reasons, Django does not attempt to automate changes to database 
# schemas, so it's your own responsibility to execute the python manage.py migrate 
# command whenever you make such a change to a model.

# Bringing this back to the admin site, now the "Add book" edit form should allow 
# for empty publication date values.

class Publisher(models.Model):
    name           = models.CharField(max_length=30)
    address        = models.CharField(max_length=50)
    city           = models.CharField(max_length=60)
    state_province = models.CharField(max_length=30)
    country        = models.CharField(max_length=30)
    website        = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name'] # specify a default natural ordering of objects in this model

class Author(models.Model):
    first_name = models.CharField(max_length=30)
    last_name  = models.CharField(max_length=40)
    email      = models.EmailField(blank=True)

    def __str__(self):
        return u'%s %s' % (self.first_name, self.last_name)

class Book(models.Model):
    title            = models.CharField(max_length=100)
    authors          = models.ManyToManyField(Author)
    publisher        = models.ForeignKey(Publisher)
    publication_date = models.DateField()

    def __str__(self):
        return self.title