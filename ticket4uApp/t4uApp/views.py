from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status

from .models import Concerts
from .serializers import *


@api_view(['GET', 'POST'])
def concert_list(request):
    if request.method == 'GET':
        data = Concerts.objects.all()
        serializer = ConcertsSerializer(data, context={'request': request}, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = ConcertsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
