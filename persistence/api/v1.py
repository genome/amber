from django.db import IntegrityError
from tastypie.api import Api
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource, fields, ALL

from persistence import models

import inspect
import simplejson
import sys


class BaseMeta(object):
    authentication = Authentication()
    authorization = Authorization()


class SampleResource(ModelResource):
    library = fields.ToOneField('persistence.api.v1.LibraryResource', 'library')
    individuals = fields.ToManyField('persistence.api.v1.IndividualResource',
            'individuals', null=True)

    class Meta(BaseMeta):
        queryset = models.Sample.objects.all()
        resource_name = 'samples'

class LibraryResource(ModelResource):
    samples = fields.ToManyField('persistence.api.v1.SampleResource',
            'samples', null=True)

    class Meta(BaseMeta):
        queryset = models.Library.objects.all()
        resource_name = 'libraries'

class TaxonResource(ModelResource):
    individuals = fields.ToManyField('persistence.api.v1.IndividualResource',
            'individuals', null=True)

    class Meta(BaseMeta):
        queryset = models.Taxon.objects.all()
        resource_name = 'taxons'

class IndividualResource(ModelResource):
    taxon = fields.ToOneField('persistence.api.v1.TaxonResource', 'taxon')
    samples = fields.ToManyField('persistence.api.v1.SampleResource',
            'samples', null=True)

    class Meta(BaseMeta):
        queryset = models.Individual.objects.all()
        resource_name = 'individuals'


class FilesetResource(ModelResource):
    files = fields.ToManyField('persistence.api.v1.FileResource', 'files',
            null=True, full=True, related_name='fileset')

    class Meta(BaseMeta):
        queryset = models.Fileset.objects.all()
        resource_name = 'filesets'

    def obj_create(self, bundle, **kwargs):
        try:
            return ModelResource.obj_create(self, bundle, **kwargs)
        except IntegrityError:
            # This has the negative side-effect of always making the server
            # respond with (201) regardless of whether or not the object was
            # just created.  It would be better if it could return (200) if the
            # object already existed.
            allocation_id = simplejson.loads(bundle.request.body)['allocation_id']
            fileset = models.Fileset.objects.get(allocation_id=allocation_id)
            bundle.obj = fileset
            return bundle

class FileResource(ModelResource):
    fileset = fields.ToOneField('persistence.api.v1.FilesetResource', 'fileset')

    class Meta(BaseMeta):
        queryset = models.File.objects.all()
        resource_name = 'files'

class ProcessResource(ModelResource):
    class Meta(BaseMeta):
        queryset = models.Process.objects.all()
        filtering = {
                "username": ['exact', 'in'],
                "status": ['exact', 'in'],
                "date_started": ALL,
                "date_ended": ALL,
                "source_path": ['exact', 'in'],
        }
        resource_name = 'processes'

class ToolResource(ModelResource):
    class Meta(BaseMeta):
        queryset = models.Tool.objects.all()
        resource_name = 'tools'

class ResultResource(ModelResource):
    creating_process = fields.ToOneField(ProcessResource, 'creating_process')
    tool = fields.ToOneField(ToolResource, 'tool')

    class Meta(BaseMeta):
        queryset = models.Result.objects.all()
        resource_name = 'results'
        excludes = ['lookup_hash']

    def dehydrate(self, bundle):
        bundle.data['inputs'] = bundle.obj.inputs
        bundle.data['outputs'] = bundle.obj.outputs
        return bundle

    def obj_create(self, bundle, **kwargs):
        try:
            return ModelResource.obj_create(self, bundle, **kwargs)
        except IntegrityError:
            # This has the negative side-effect of always making the server
            # respond with (201) regardless of whether or not the object was
            # just created.  It would be better if it could return (200) if the
            # object already existed.
            data = simplejson.loads(bundle.request.body)
            tool = models.Tool.objects.get(
                    source_path=data['tool']['source_path'],
                    version=data['tool']['version'])
            result = models.Result.objects.get(tool=tool,
                    test_name=data['test_name'],
                    lookup_hash=models.Result.calculate_lookup_hash(data['inputs']))
            bundle.obj = result
            return bundle

class ProcessStepResource(ModelResource):
    process = fields.ToOneField(ProcessResource, 'process')
    result = fields.ToOneField(ResultResource, 'result')

    class Meta(BaseMeta):
        queryset = models.ProcessStep.objects.all()
        resource_name = 'process-steps'
        filtering = {
                "process": ["exact"],
        }


amber_api = Api(api_name='v1')

MODULE = sys.modules[__name__]
for name in dir(MODULE):
    cls = getattr(MODULE, name)
    if inspect.isclass(cls):
        if cls != ModelResource:
            if issubclass(cls, ModelResource):
                amber_api.register(cls())
