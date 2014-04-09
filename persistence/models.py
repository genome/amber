from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

import hashlib
import json_field
import simplejson


class Library(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=256)

class Sample(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=256)
    library = models.ForeignKey(Library, related_name='samples')

class Taxon(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=256)

class Individual(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=256)
    taxon = models.ForeignKey(Taxon, related_name='individuals')
    samples = models.ManyToManyField(Sample, related_name='individuals')

class Fileset(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    allocation_id = models.CharField(max_length=256, unique=True)

class File(models.Model):
    path = models.CharField(max_length=256)
    fileset = models.ForeignKey(Fileset, related_name='files')
    size = models.IntegerField()
    md5 = models.CharField(max_length=32)

    class Meta(object):
        unique_together = ('path', 'fileset')

class Process(models.Model):
    allocation_id = models.CharField(max_length=256, unique=True)
    username = models.CharField(max_length=256)
    date_started = models.DateTimeField(auto_now_add=True)
    date_ended = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=64)
    source_path = models.CharField(max_length=512)

    # workflow_name is used to lookup the workflow in another database
    workflow_name = models.CharField(max_length=512, unique=True)

class Tool(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    source_path = models.CharField(max_length=512)
    version = models.CharField(max_length=32)
    class Meta(object):
        unique_together = ('source_path', 'version')

class Result(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    creating_process = models.ForeignKey(Process,
            related_name='created_results')

    tool = models.ForeignKey(Tool, related_name='results')
    lookup_hash = models.CharField(max_length=32)
    test_name = models.CharField(max_length=256)

    inputs = json_field.JSONField()
    outputs = json_field.JSONField()

    class Meta(object):
        unique_together = ('tool', 'lookup_hash', 'test_name')

    @staticmethod
    def calculate_lookup_hash(inputs):
        m = hashlib.md5()
        m.update(simplejson.dumps(inputs, sort_keys=True))
        return m.hexdigest()

@receiver(pre_save, sender=Result)
def _update_lookup_hash(sender, instance, **kwargs):
    instance.lookup_hash = Result.calculate_lookup_hash(instance.inputs)

class ProcessStep(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    process = models.ForeignKey(Process, related_name='steps')
    result = models.ForeignKey(Result, related_name='steps')
    label = models.CharField(max_length=256)

    class Meta(object):
        unique_together = ('process', 'result', 'label')
