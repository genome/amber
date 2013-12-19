from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

import hashlib
import json_field
import simplejson


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
    creating_process = models.ForeignKey(Process,
            related_name='created_results')

    tool_name = models.CharField(max_length=256)
    lookup_hash = models.CharField(max_length=32)
    test_name = models.CharField(max_length=256)

    inputs = json_field.JSONField()
    outputs = json_field.JSONField()

    class Meta(object):
        unique_together = ('tool_name', 'lookup_hash', 'test_name')

    @staticmethod
    def calculate_lookup_hash(inputs):
        m = hashlib.md5()
        m.update(simplejson.dumps(inputs, sort_keys=True))
        return m.hexdigest()


@receiver(pre_save, sender=Result)
def _update_lookup_hash(sender, instance, **kwargs):
    instance.lookup_hash = Result.calculate_lookup_hash(instance.inputs)


class ProcessStep(models.Model):
    process = models.ForeignKey(Process, related_name='steps')
    result = models.ForeignKey(Result, related_name='steps')
    label = models.CharField(max_length=256)

    class Meta(object):
        unique_together = ('process', 'result')
