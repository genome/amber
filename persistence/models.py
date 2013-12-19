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


class Fileset(models.Model):
    pass

class File(models.Model):
    path = models.CharField(max_length=256)
    fileset = models.ForeignKey(Fileset, related_name='files')
    size = models.IntegerField()
    md5 = models.CharField(max_length=32)

    class Meta(object):
        unique_together = ('path', 'fileset')
