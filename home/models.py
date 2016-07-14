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

class Region(models.Model):
    name = models.CharField(max_length=30)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']

class RegionDexNum(models.Model):
    region = models.ForeignKey(Region)
    number = models.IntegerField()
    def __str__(self):
        return str(self.region) + ": " + str(self.number)

class Type(models.Model):
    name = models.CharField(max_length=30)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']

class EggGroup(models.Model):
    name = models.CharField(max_length=30)
    desc = models.CharField(max_length=200, default="Nothing written")
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']

class Generation(models.Model):
    gen = models.IntegerField()
    def __str__(self):
        return str(self.gen)

class Ability(models.Model):
    name       = models.CharField(max_length=30)
    number     = models.IntegerField(null=True)
    effect     = models.CharField(max_length=200, default="Nothing written")
    generation = models.ForeignKey(Generation, null=True)

    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']

class LevelingRate(models.Model):
    name = models.CharField(max_length=30)
    def __str__(self):
        return self.name

class BodyStyle(models.Model):
    style = models.CharField(max_length=40)
    def __str__(self):
        return self.style
    class Meta:
        ordering = ['style']

class Pokemon(models.Model):
    # basic info
    name                 = models.CharField(max_length=30)
    category             = models.CharField(max_length=30)
    natDexNum            = models.IntegerField()
    regDexNums           = models.ManyToManyField(RegionDexNum)
    poketypes            = models.ManyToManyField(Type)
    abilities            = models.ManyToManyField(Ability)
    catchRate            = models.FloatField()

    # breeding
    eggGroup             = models.ManyToManyField(EggGroup)
    genderRatio          = models.CharField(max_length=10) # if genderless then "genderless"
    heightUSFeet         = models.IntegerField()
    heightUSInches       = models.IntegerField()
    heightMetric         = models.FloatField()
    weightUS             = models.FloatField()
    weightMetric         = models.FloatField()
    hatchTimeLow         = models.IntegerField()
    hatchTimeHigh        = models.IntegerField()
    bodyStyle            = models.ForeignKey(BodyStyle)
    baseFriendship       = models.IntegerField()

    # training
    baseExpYieldUpToGen4 = models.IntegerField()
    baseExpYieldGen5Plus = models.IntegerField()
    levelingRate         = models.ForeignKey(LevelingRate)

    # effort values
    evHP                 = models.IntegerField()
    evAttack             = models.IntegerField()
    evDefense            = models.IntegerField()
    evSpecialAttack      = models.IntegerField()
    evSpecialDefense     = models.IntegerField()
    evSpeed              = models.IntegerField()


    def __str__(self):
        return str(self.natDexNum) + ": " + self.name
    class Meta:
        ordering = ['natDexNum']