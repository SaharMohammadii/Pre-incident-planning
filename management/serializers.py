from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import FireStation, Inspection, Location
from account.serializers import AccountUserSerializer, User
from building.models import Building
from building.serializers import BuildingSerializer


class LocationSerializer(ModelSerializer):
    class Meta:
        model = Location
        fields = ['lat', 'lang', 'alt']



class FireStationSerializer(ModelSerializer):
    manager = AccountUserSerializer(read_only=True)
    staffs = AccountUserSerializer(read_only=True, many=True)
    location = LocationSerializer(required=False, allow_null=True)


    class Meta:
        model = FireStation
        fields = ['name', 'address', 'manager', 'location', 'staffs']
        extra_kwargs = {
            'staffs': {'required': False},
            'location': {'required': False},
        }

    def update(self, instance, validated_data):
        location_data = validated_data.pop('location', None)

        # update or create location
        if location_data:
            if instance.location:
                for attr, value in location_data.items():
                    setattr(instance.location, attr, value)
                instance.location.save()
            else:
                instance.location = Location.objects.create(**location_data)

        # update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class StaffAddSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)


class CreateUserAsStaff(serializers.Serializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    personnel_code = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)


class FireStationModification(serializers.Serializer):
    address = serializers.CharField()
    location = serializers.IntegerField()



class ModifyStaffStatusSerializer(serializers.Serializer):
    status = serializers.CharField(required=True)
    staff_id = serializers.IntegerField(required=True)



class InspectionSerializer(ModelSerializer):
    head_staff = AccountUserSerializer(read_only=True)
    staff = AccountUserSerializer(many=True, read_only=True)
    fire_station = FireStationSerializer()
    building = BuildingSerializer()

    class Meta:
        model = Inspection
        fields = '__all__'


class CreateInspectionSerializer(ModelSerializer):
    building = serializers.PrimaryKeyRelatedField(queryset=Building.objects.all())
    head_staff = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    staff = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)

    class Meta:
        model = Inspection
        fields = ['building', 'head_staff', 'staff']



class InspectionManagementStatusSerializer(serializers.Serializer):
    status = serializers.BooleanField()
    

class InspectionReportSerializer(serializers.Serializer):
    type_of_report = serializers.CharField()
    value = serializers.CharField()
    inspection = serializers.PrimaryKeyRelatedField(queryset=Inspection.objects.all(), required=True)