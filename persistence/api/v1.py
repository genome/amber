from django.contrib.auth.models import User
from tastypie.api import Api
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource, fields

from persistence import models

import inspect
import sys


class BaseMeta(object):
    authentication = Authentication()
    authorization = Authorization()


class UserResource(ModelResource):
    class Meta(BaseMeta):
        queryset = User.objects.all()
        resource_name = 'users'
        excludes = ['email', 'password', 'is_superuser']


class SampleResource(ModelResource):
    library = fields.ToOneField('persistence.api.v1.LibraryResource', 'library')
    individuals = fields.ToManyField('persistence.api.v1.IndividualResource', 'individuals', null=True)

    class Meta(BaseMeta):
        queryset = models.Sample.objects.all()
        resource_name = 'samples'

class LibraryResource(ModelResource):
    samples = fields.ToManyField('persistence.api.v1.SampleResource', 'samples', null=True)

    class Meta(BaseMeta):
        queryset = models.Library.objects.all()
        resource_name = 'libraries'

class TaxonResource(ModelResource):
    individuals = fields.ToManyField('persistence.api.v1.IndividualResource', 'individuals', null=True)

    class Meta(BaseMeta):
        queryset = models.Taxon.objects.all()
        resource_name = 'taxons'

class IndividualResource(ModelResource):
    taxon = fields.ToOneField('persistence.api.v1.TaxonResource', 'taxon')
    samples = fields.ToManyField('persistence.api.v1.SampleResource', 'samples', null=True)

    class Meta(BaseMeta):
        queryset = models.Individual.objects.all()
        resource_name = 'individuals'


amber_api = Api(api_name='v1')

MODULE = sys.modules[__name__]
for name in dir(MODULE):
    cls = getattr(MODULE, name)
    if inspect.isclass(cls):
        if cls != ModelResource:
            if issubclass(cls, ModelResource):
                amber_api.register(cls())
