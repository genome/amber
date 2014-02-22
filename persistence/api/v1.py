from tastypie.api import Api
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource, fields

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


class AllocationResource(ModelResource):
    fileset = fields.ToOneField('persistence.api.v1.FilesetResource', 'fileset')

    class Meta(BaseMeta):
        queryset = models.Allocation.objects.all()
        resource_name = 'allocations'

class FilesetResource(ModelResource):
    files = fields.ToManyField('persistence.api.v1.FileResource', 'files',
            null=True, full=True, related_name='fileset')
    allocations = fields.ToManyField(AllocationResource, 'allocations',
            null=True, full=True, related_name='fileset')

    class Meta(BaseMeta):
        queryset = models.Fileset.objects.all()
        resource_name = 'filesets'

class FileResource(ModelResource):
    fileset = fields.ToOneField('persistence.api.v1.FilesetResource', 'fileset')

    class Meta(BaseMeta):
        queryset = models.File.objects.all()
        resource_name = 'files'


class ProcessResource(ModelResource):
    created_results = fields.ToManyField('persistence.api.v1.ResultResource',
            'created_results', null=True)

    steps = fields.ToManyField('persistence.api.v1.ProcessStepResource',
            'steps', null=True)

    class Meta(BaseMeta):
        queryset = models.Process.objects.all()
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

class ProcessStepResource(ModelResource):
    process = fields.ToOneField(ProcessResource, 'process')
    result = fields.ToOneField(ResultResource, 'result')

    class Meta(BaseMeta):
        queryset = models.ProcessStep.objects.all()
        resource_name = 'process-steps'
        filtering = {"process": ["exact"]}


amber_api = Api(api_name='v1')

MODULE = sys.modules[__name__]
for name in dir(MODULE):
    cls = getattr(MODULE, name)
    if inspect.isclass(cls):
        if cls != ModelResource:
            if issubclass(cls, ModelResource):
                amber_api.register(cls())
