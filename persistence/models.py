from django.db import models


class Library(models.Model):
    name = models.CharField(max_length=256)

class Sample(models.Model):
    name = models.CharField(max_length=256)
    library = models.ForeignKey(Library, related_name='samples')

class Taxon(models.Model):
    name = models.CharField(max_length=256)

class Individual(models.Model):
    name = models.CharField(max_length=256)
    taxon = models.ForeignKey(Taxon, related_name='individuals')
    samples = models.ManyToManyField(Sample, related_name='individuals')
