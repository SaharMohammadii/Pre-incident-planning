from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from account.permissions import HasGroupPermission
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from .models import FireStation, Inspection, Location
from .serializers import (FireStationSerializer, 
                          StaffAddSerializer,  
                          AccountUserSerializer, 
                          CreateUserAsStaff,
                          ModifyStaffStatusSerializer,
                          InspectionSerializer,
                          CreateInspectionSerializer,
                          InspectionManagementStatusSerializer,
                          InspectionReportSerializer,
                          LocationSerializer)

from account.utils import is_phone_number_valid
from .constants import WARNINGS, SAFETY_LEVELS
from django.contrib.auth.models import Group


User = get_user_model()



class FireStationManagementView(APIView):
    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
         'PATCH': ['manager'],
         'POST': ['manager'],
         'GET': ['manager'],
     }
    
    # get fire station data
    def get(self, request, format=None):
        user = request.user
        fire_station = FireStation.objects.filter(manager__id=user.id)
        if fire_station.exists():
            fire_station = fire_station.first()
            
            return Response(FireStationSerializer(fire_station).data, status=status.HTTP_200_OK)
        
        else:
            return Response({"msg": "No Station Found"}, status=status.HTTP_404_NOT_FOUND)

        
    # add staff to fire station 
    def post(self, request, format=None):

        serializer = StaffAddSerializer(data=request.data)

        if serializer.is_valid():
            staff_id = serializer.validated_data.get('user_id')
            
            staff_obj = User.objects.filter(id=staff_id)
            if staff_obj.exists():
                staff_obj = staff_obj.first()


                user = request.user

                fire_station = FireStation.objects.filter(manager__id=user.id)
                if fire_station.exists():
                    fire_station = fire_station.first()
                    
                    if staff_obj not in fire_station.staffs.all() and staff_obj.user_role == "staff":
                        fire_station.staffs.add(staff_obj)
                        fire_station.save()

                        return Response({'msg': f"کاربر {staff_obj} با موفقیت به آتش نشانی اضافه شد."})

                    else:
                        return Response({'msg': 'کاربر در آتش نشانی هست.'}, status=status.HTTP_204_NO_CONTENT)

                else:
                    return Response({'msg': 'این آتش نشانی موجود نیست'}, status=status.HTTP_404_NOT_FOUND)

            else:
                return Response({'msg': 'کاربر یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)



    # modify fire station
    def patch(self, request, format=None):
        user = request.user            
        fire_station = FireStation.objects.filter(manager__id=user.id)
        if fire_station.exists():
            fire_station = fire_station.first()

            serializer = FireStationSerializer(fire_station, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            

        else:
            return Response({'msg': 'این آتش نشانی موجود نیست'}, status=status.HTTP_404_NOT_FOUND)
        




class AccountUserByManagementView(APIView):
    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
         'PATCH': ['manager'],
         'POST': ['manager'],
         'GET': ['manager'],
     }
    
    # get staff info
    def get(self, request, pk=None):
        user = request.user
        if pk is not None:
            fire_station = FireStation.objects.filter(manager__id=user.id, id=pk)
            if fire_station.exists():
                fire_station = fire_station.first()

                return Response(AccountUserSerializer(fire_station.staffs.all(), many=True).data, status=status.HTTP_200_OK)

            
            else:
                return Response({'msg': 'no fire station found'}, status=status.HTTP_404_NOT_FOUND)

        else:
            return Response({'msg': 'fire station is not found'}, status=status.HTTP_404_NOT_FOUND)

    # create user 
    def post(self, request, format=None):
        serializer = CreateUserAsStaff(data=request.data)

        if serializer.is_valid():
            first_name = serializer.validated_data.get('first_name')
            last_name = serializer.validated_data.get('last_name')
            personnel_code = serializer.validated_data.get('personnel_code')
            phone_number = serializer.validated_data.get('phone_number')

            if is_phone_number_valid(phone_number):
                user_obj = User(first_name=first_name, last_name=last_name, personnel_code=personnel_code, phone_number=phone_number)
                user_obj.save()
                
                group = Group.objects.get(name='staff')
                user_obj.groups.add(group)


                return Response(AccountUserSerializer(user_obj).data, status=status.HTTP_201_CREATED)

            else:
                return Response({'msg': 'phone number is not valid'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'msg': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    

    # modify staff status
    def patch(self, request, format=None):
        serializer = ModifyStaffStatusSerializer(data=request.data)

        if serializer.is_valid():
            _status = serializer.validated_data.get('status')
            staff_id = serializer.validated_data.get('staff_id')

            # check if the manager is belong to this fire station
            user = request.user
            fire_station = FireStation.objects.filter(manager__id=user.id)

            if fire_station.exists():
                fire_station = fire_station.first()

                # check that if the user exists
                staff_obj = User.objects.filter(id=staff_id)
                if staff_obj.exists():
                    staff_obj = staff_obj.first()

                    # check that user is a memeber of this fire station
                    if staff_obj in fire_station.staffs.all():
                        
                        # status can only be on of `free` or `on_mission`
                        if _status == 'on_mission' or _status == 'free':
                            staff_obj.staff_status = _status
                            staff_obj.save()

                            return Response({'msg': f'staff status updated to {_status}'}, status=status.HTTP_200_OK)
                        
                        else:
                            return Response({'msg': f"status should be on of `on_mission` or `free` "})

                    else:
                        return Response({'msg': 'the staff is not in the fire station'}, status=status.HTTP_401_UNAUTHORIZED)

                else:
                    return Response({'msg': 'user does not exist'}, status=status.HTTP_404_NOT_FOUND)

            else:
                return Response({'msg': 'fire station not found'}, status=status.HTTP_404_NOT_FOUND)
        
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)





class InspectionManagementView(APIView):
    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
         'PATCH': ['manager', ],
         'POST': ['manager', ],
         'GET': ['manager', ],
         'DELETE': ['manager', ]
     }
    
    # get all inspections of the fire station
    def get(self, request, pk=None, format=None):
        user = request.user
        
        if pk is not None:
            inspection = Inspection.objects.filter(fire_station__manager__id=user.id, id=pk)
            if inspection.exists():
                inspection = inspection.first()
                return Response(InspectionSerializer(inspection).data, status=status.HTTP_200_OK)
            else:
                return Response({'msg': 'inspectio not found'}, status=status.HTTP_404_NOT_FOUND)

        inspections = Inspection.objects.filter(fire_station__manager__id=user.id)
        
        if inspections.exists():
            return Response(InspectionSerializer(inspections, many=True).data, status=status.HTTP_200_OK)

        return Response({'msg': 'No Inspection Found'}, status=status.HTTP_404_NOT_FOUND)

    # create inspection by manager
    def post(self, request, format=None):
        serializer = CreateInspectionSerializer(data=request.data)

        if serializer.is_valid():
            building = serializer.validated_data.get('building')
            head_staff = serializer.validated_data.get('head_staff')
            staff = serializer.validated_data.get('staff')

            user = request.user
            fire_station = FireStation.objects.filter(manager__id=user.id)
            if fire_station.exists():
                fire_station = fire_station.first()
                
                inspection = Inspection(
                    building=building,
                    head_staff=head_staff,
                    fire_station=fire_station,

                )
                inspection.save()

                inspection.staff.set(staff)
                inspection.save()

                return Response(InspectionSerializer(inspection).data, status=status.HTTP_201_CREATED)

            else:
                return Response({'msg': 'No Fire Station Found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


    
    # modify the inspection status
    def patch(self, request, pk=None):
        
        serializer = InspectionManagementStatusSerializer(data=request.data)
        if serializer.is_valid() and pk is not None:
            _status = serializer.validated_data.get('status')

            user = request.user

            inspection = Inspection.objects.filter(id=pk, fire_station__manager__id=user.id)
            if inspection.exists():
                inspection = inspection.first()

                if inspection.ready_to_review:
                    inspection.approved_by_manager = _status

                    if _status == True:
                        inspection.status = 'done'
                    
                    elif _status == False:
                        inspection.status = 'pending'

                    inspection.save()

                    return Response(InspectionSerializer(inspection).data, status=status.HTTP_200_OK)

                else:
                    return Response({'msg': 'the inspection is under review'}, status=status.HTTP_204_NO_CONTENT)    

            else:
                return Response({'msg': "No Inspection Found"}, status=status.HTTP_404_NOT_FOUND)

    
    # delete inspection (optional)
    def delete(self, request, format=None):
        # required otp code that is sent to manager's phone number
        pass



class InspectionStaffView(APIView):
    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
         'PATCH': ['staff'],
         'GET': ['staff'],
     }
    
    def get(self, request, pk=None, format=None):
        user = request.user
        if pk is not None:
            inspection = Inspection.objects.filter(staff=user, id=pk)
            if inspection.exists():
                inspection = inspection.first()
                return Response(InspectionSerializer(inspection).data, status=status.HTTP_200_OK)
            else:
                return Response({'msg': 'inspection not found'}, status=status.HTTP_404_NOT_FOUND)

        inspections = Inspection.objects.filter(staff=user)

        if inspections.exists():
            return Response(InspectionSerializer(inspections, many=True).data, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, format=None):
        serializer = InspectionReportSerializer(data=request.data)

        user = request.user
        user_obj = User.objects.get(id=user.id)

        if serializer.is_valid():
            type_of_report = serializer.validated_data.get('type_of_report')
            value = serializer.validated_data.get('value')
            inspection = serializer.validated_data.get('inspection')

            if user_obj == inspection.head_staff or user_obj in inspection.staff.all():
                
                if type_of_report == 'warning':
                    inspection.warning_report = value

                elif type_of_report == 'safety':
                    inspection.owner_report = value

                elif type_of_report == 'ready':             
                    inspection.ready_to_review = True


                inspection.save()
                return Response(InspectionSerializer(inspection).data, status=status.HTTP_200_OK)
            
            else:
                return Response({'msg': 'you cannot change this inspection'}, status=status.HTTP_401_UNAUTHORIZED)
        
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
            




class LocationView(APIView):
    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
         'POST': ['manager', 'staff'],
     }
    
    def post(self, request, format=None):
        serializer = LocationSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                location = Location(**serializer.validated_data)
                location.save()

                return Response(LocationSerializer(location).data, status=status.HTTP_201_CREATED)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)





class ConstantsView(APIView):
    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
         'GET': ['manager', 'staff'],
     }
    
    def get(self, request, format=None):
        param = request.GET.get('type')

        if param == 'warning':
            data = {
                '1': WARNINGS[0][0],
                '2': WARNINGS[1][0],
                '3': WARNINGS[2][0],
            }


            return Response(data, status=status.HTTP_200_OK)

        elif param == 'safety':
            data = {
                '1': SAFETY_LEVELS[0][0],
                '2': SAFETY_LEVELS[1][0],
                '3': SAFETY_LEVELS[2][0],
                '4': SAFETY_LEVELS[3][0],
            }


            return Response(data, status=status.HTTP_200_OK)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)
