from django.db import models

import json_field


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

class Allocation(models.Model):
    allocation_id = models.CharField(max_length=256, unique=True)
    fileset = models.ForeignKey(Fileset, related_name='allocations')


class Process(models.Model):
    allocation_id = models.CharField(max_length=256, unique=True)

class Result(models.Model):
    creating_process = models.ForeignKey(Process)

    tool_name = models.CharField(max_length=256)
    lookup_hash = models.CharField(max_length=32)
    test_name = models.CharField(max_length=256)

    inputs = json_field.JSONField()
    outputs = json_field.JSONField()

    class Meta(object):
        unique_together = ('tool_name', 'lookup_hash', 'test_name')

class ProcessStep(models.Model):
    process = models.ForeignKey(Process)
    result = models.ForeignKey(Result)
    label = models.CharField(max_length=256)

    class Meta(object):
        unique_together = ('process', 'result')
