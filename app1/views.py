from django.shortcuts import render,redirect
import io
from rest_framework.parsers import JSONParser
from . models import Array
from . serializers import ArraySerializer
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django.http import HttpResponse,JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
# Create your views here.
def index(request):
    return render(request, 'app1/index.html')
@csrf_exempt
def array_api(request):
    # if request.method == 'GET':
    #     jsondata = request.body
    #     stream = io.BytesIO(jsondata)
    #     pydata = JSONParser().parse(stream)
    #     group_name = pydata.get('group_name',None)

    #     if group_name is not None:
    #         array = Array.objects.filter(group_name=group_name)
    #         serializer = ArraySerializer(array,many=True)
    #         jsondata = JSONRenderer().render(serializer.data)
    #         return HttpResponse(jsondata,content_type='application/json')
    #     jsondata = JSONRenderer().render('some error')
    #     return HttpResponse(jsondata,content_type='application/json')
    
    if request.method == "PUT":
        jsondata = request.body
        stream = io.BytesIO(jsondata)
        pydata = JSONParser().parse(stream)
        group_name = pydata.get('group_name')
        index = int(pydata['index'])
        playerInput = pydata.get('playerInput',None)
        print('in api view------------')
        print(group_name)
        print(playerInput)
        print(index)
        instance = Array.objects.get(pk=group_name)
        array = instance.data
        array[index] = playerInput
        instance.data = array
        instance.save()
        return JsonResponse("Success",safe=False)

@csrf_exempt 
def get_array(request):
    if request.method == "POST":
        jsondata = request.body
        stream = io.BytesIO(jsondata)
        pydata = JSONParser().parse(stream)
        group_name = pydata.get('group_name',None)
        if group_name is not None:
            array = Array.objects.get(pk=group_name)
            serializer = ArraySerializer(array)
            # response = JSONRenderer().render(serializer.data)
            # return HttpResponse(response,content_type='application/json')
            return JsonResponse(serializer.data,safe=False)