from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from persistence import models

import simplejson


@csrf_exempt
def register_fileset(request, **stuff):
    data = simplejson.loads(request.body)

    try:
        tool = models.Fileset(source_path=data['source_path'],
                version=data['version'])
        tool.save()
    except IntegrityError:
        tool = models.Tool.objects.get(
                source_path=data['source_path'],
                version=data['version'])
    return HttpResponse(simplejson.dumps({
        'objects': ['/v1/tools/%d/' % tool.id]
    }))

@csrf_exempt
def register_tool(request, **stuff):
    data = simplejson.loads(request.body)

    try:
        tool = models.Tool(source_path=data['source_path'],
                version=data['version'])
        tool.save()
    except IntegrityError:
        tool = models.Tool.objects.get(
                source_path=data['source_path'],
                version=data['version'])
    return HttpResponse(simplejson.dumps({
        'objects': ['/v1/tools/%d/' % tool.id]
    }))

@csrf_exempt
def checkpoint(request, **stuff):
    data = simplejson.loads(request.body)

    try:
        tool = models.Tool.objects.get(
                source_path=data['source_path'],
                version=data['version'])
        result = models.Result.objects.get(tool=tool,
                test_name=data['test_name'],
                lookup_hash=models.Result.calculate_lookup_hash(data['inputs']))
        return HttpResponse(simplejson.dumps({
            'objects': ['/v1/results/%d/' % result.id]
        }))
    except models.Result.DoesNotExist:
        return HttpResponse(status=404)

