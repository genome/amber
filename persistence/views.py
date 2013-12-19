from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from persistence import models

import simplejson


@csrf_exempt
def checkpoint(request, **stuff):
    data = simplejson.loads(request.body)

    try:
        result = models.Result.objects.get(tool_name=data['tool_name'],
                test_name=data['test_name'],
                lookup_hash=models.Result.calculate_lookup_hash(data['inputs']))
        return HttpResponse(simplejson.dumps({
            'objects': ['/v1/results/%d/' % result.id]
        }))
    except models.Result.DoesNotExist:
        return HttpResponse(status=404)

