from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from account.permissions import HasGroupPermission
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .models import (ImageUploader, Building)
from .models import FIRE_RISKS, INCIDENT_RISKS, EQUIPMENT_STATUS, BUILDING_TYPE
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import BuildingSerializer, ImageUploaderSerializer, ConstatnsSerializer
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D



class BuildingView(APIView):
    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
         'POST': ['manager', 'staff'],
         'PATCH': ['manager', 'staff'],
     }

    def post(self, request, format=None):
        serializer = BuildingSerializer(data=request.data)

        if serializer.is_valid():
            building = serializer.save()
            building.save()

            return Response(BuildingSerializer(building).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def patch(self, request, pk=None, format=None):
        try:
            building = Building.objects.get(pk=pk)
        except Building.DoesNotExist:
            return Response({'msg': 'building not found'}, status=status.HTTP_404_NOT_FOUND)

        # `partial` -> it doesn't need all the fields to be mentioned
        serializer = BuildingSerializer(building, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()  # calls your `update()` method in the serializer
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    



class BuildingViewPublic(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly, HasGroupPermission]
    required_groups = {
         'GET': ['manager', 'staff', 'normal_user']
     }
    
    def get(self, request, pk=None, format=None):

        if pk is not None:
            building = Building.objects.filter(id=pk)
            if building.exists():
                building = building.first()
                return Response(BuildingSerializer(building, context={'request': request}).data, status=status.HTTP_200_OK) 
            
            return Response({'msg': 'building not found'}, status=status.HTTP_404_NOT_FOUND)

        buildings = Building.objects.all()

        return Response(BuildingSerializer(buildings, many=True, context={'request': request}).data, status=status.HTTP_200_OK)




class ImageUploaderView(APIView):
    permission_classes = [IsAuthenticated, HasGroupPermission]
    parser_classes = [MultiPartParser, FormParser]  # important for handling image uploads

    required_groups = {
         'POST': ['manager', 'staff'],
         'GET': ['manager', 'staff', 'normal_user'],
     }
    
    def get(self, request):
        images = ImageUploader.objects.all()
        serializer = ImageUploaderSerializer(images, many=True)
        return Response(serializer.data)

    
    def post(self, request):
        serializer = ImageUploaderSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    




class ConstantsView(APIView):
    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
         'GET': ['manager', 'staff']
     }
    
    def get(self, request, format=None):
        # serializer = ConstatnsSerializer(data=request.data)
        
        type_of_request = request.GET.get('type_of_constant')

        
        if type_of_request == "fire":
            return Response(dict(FIRE_RISKS), status=status.HTTP_200_OK)
        
        elif type_of_request == 'incident':
            return Response(dict(INCIDENT_RISKS), status=status.HTTP_200_OK)


        elif type_of_request == "equipment":
            return Response(dict(EQUIPMENT_STATUS), status=status.HTTP_200_OK)


        elif type_of_request == "building":
            return Response(dict(BUILDING_TYPE), status=status.HTTP_200_OK)

        

        return Response(status=status.HTTP_400_BAD_REQUEST)
    

class BuildingSearchByLocationView(APIView):
    def get(self, request):
        try:
            lat = float(request.query_params.get('lat'))
            lng = float(request.query_params.get('lng'))
            radius = float(request.query_params.get('radius', 2))  # km
        except (TypeError, ValueError):
            return Response({"error": "Invalid lat, lng, or radius"}, status=400)

        user_point = Point(lng, lat)  # (lng, lat)

        buildings = Building.objects.filter(
            location__point__distance_lte=(user_point, D(km=radius))
        )

        serializer = BuildingSerializer(buildings, many=True)
        return Response(serializer.data)
