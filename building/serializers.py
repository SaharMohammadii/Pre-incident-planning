from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import (ImageHandler, Widget, 
                     Equipment, Floor, Building, Route, ImageUploader)
# from management.serializers import LocationSerializer
from management.models import Location
from FormCreator.models import FormResponse

class ImageUploaderSerializer(ModelSerializer):
    class Meta:
        model = ImageUploader
        fields = ['id', 'image', 'description']


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["lat", "lang", "alt"]


class ImageHandlerSerializer(ModelSerializer):
    class Meta:
        model = ImageHandler
        fields = '__all__'


class WidgetSerializer(ModelSerializer):
    location = LocationSerializer()

    class Meta:
        model = Widget
        fields = '__all__'


class EquipmentSerializer(ModelSerializer):
    widget = WidgetSerializer()

    class Meta:
        model = Equipment
        fields = '__all__'


class RouteSerializer(ModelSerializer):
    location = LocationSerializer()

    class Meta:
        model = Route
        fields = '__all__'


class FloorSerializer(ModelSerializer):
    widget = WidgetSerializer(many=True)
    images = ImageHandlerSerializer(many=True)
    equipments = EquipmentSerializer(many=True)
    shape = LocationSerializer(many=True)
    routes = RouteSerializer(many=True)

    class Meta:
        model = Floor
        fields = '__all__'


class BuildingSerializer(ModelSerializer):
    images = ImageHandlerSerializer(many=True)
    floors = FloorSerializer(many=True)
    location = LocationSerializer()
    routes = RouteSerializer(many=True)

    safety_form = serializers.PrimaryKeyRelatedField(queryset=FormResponse.objects.all())
    safety_form_for_eco = serializers.PrimaryKeyRelatedField(queryset=FormResponse.objects.all())

    class Meta:
        model = Building
        fields = '__all__'

    def create(self, validated_data):
        images_data = validated_data.pop("images", [])
        floors_data = validated_data.pop("floors", [])
        routes_data = validated_data.pop("routes", [])
        location_data = validated_data.pop("location", None)

        # --- Location (FK) ---
        if location_data:
            location_obj = Location.objects.filter(
                lat=location_data.get("lat"),
                lang=location_data.get("lang"),
                alt=location_data.get("alt", None)
            ).first()
            if not location_obj:
                location_obj = Location.objects.create(
                    lat=location_data.get("lat"),
                    lang=location_data.get("lang"),
                    alt=location_data.get("alt", None)
                )
            validated_data["location"] = location_obj

        # --- Create Building ---
        building = Building.objects.create(**validated_data)

        # --- Building images (M2M) ---
        for image_data in images_data:
            image_instance = ImageHandler.objects.create(**image_data)
            building.images.add(image_instance)

        # --- Floors (nested) ---
        for floor_data in floors_data:
            shape_data = floor_data.pop("shape", [])
            # IMPORTANT: your JSON uses "widget" (singular)
            widgets_data = floor_data.pop("widget", [])
            floor_images_data = floor_data.pop("images", [])
            equipments_data = floor_data.pop("equipments", [])
            routes_data_floor = floor_data.pop("routes", [])

            # create Floor (non-M2M fields)
            floor = Floor.objects.create(
                order_of_floor=floor_data.get("order_of_floor", 0),
                width=floor_data.get("width", 0.0),
                height=floor_data.get("height", 0.0),
            )

            # Floor.shape (M2M -> Location)
            for loc in shape_data:
                location_obj = Location.objects.filter(
                    lat=loc.get("lat"),
                    lang=loc.get("lang"),
                    alt=loc.get("alt", None)
                ).first()
                if not location_obj:
                    location_obj = Location.objects.create(
                        lat=loc.get("lat"),
                        lang=loc.get("lang"),
                        alt=loc.get("alt", None)
                    )
                floor.shape.add(location_obj)

            # Floor.widget (M2M)
            for widget_data in widgets_data:
                location_widget_data = widget_data.pop("location", None)
                if location_widget_data:
                    loc_obj, _ = Location.objects.get_or_create(
                        lat=location_widget_data.get("lat"),
                        lang=location_widget_data.get("lang"),
                        alt=location_widget_data.get("alt", None)
                    )
                    widget_data["location"] = loc_obj
                widget = Widget.objects.create(**widget_data)
                floor.widget.add(widget)

            # Floor.images (M2M)
            for image_data in floor_images_data:
                img_instance = ImageHandler.objects.create(**image_data)
                floor.images.add(img_instance)

            # Floor.equipments (M2M)  <-- FIXED: attach the created equipment to the floor
            for equipment_data in equipments_data:
                widget_data = equipment_data.pop("widget", None)
                if widget_data:
                    loc_w_data = widget_data.pop("location", None)
                    if loc_w_data:
                        loc_obj, _ = Location.objects.get_or_create(
                            lat=loc_w_data.get("lat"),
                            lang=loc_w_data.get("lang"),
                            alt=loc_w_data.get("alt", None)
                        )
                        widget_data["location"] = loc_obj
                    widget_instance = Widget.objects.create(**widget_data)
                    equipment_data["widget"] = widget_instance

                equipment_instance = Equipment.objects.create(**equipment_data)
                floor.equipments.add(equipment_instance)  # <-- crucial

            # Floor.routes (M2M)  <-- FIXED: create and attach to floor (and optionally building)
            for route_data in routes_data_floor:
                location_route_data = route_data.pop("location", None)
                if location_route_data:
                    loc_obj, _ = Location.objects.get_or_create(
                        lat=location_route_data.get("lat"),
                        lang=location_route_data.get("lang"),
                        alt=location_route_data.get("alt", None)
                    )
                    route_data["location"] = loc_obj
                route_instance = Route.objects.create(**route_data)
                floor.routes.add(route_instance)
                building.routes.add(route_instance)  # optional but often useful

            floor.save()
            building.floors.add(floor)

        # Building.routes (top level M2M)  <-- FIXED: attach to building M2M
        for route_data in routes_data:
            location_route_data = route_data.pop("location", None)
            if location_route_data:
                loc_obj, _ = Location.objects.get_or_create(
                    lat=location_route_data.get("lat"),
                    lang=location_route_data.get("lang"),
                    alt=location_route_data.get("alt", None)
                )
                route_data["location"] = loc_obj
            route_instance = Route.objects.create(**route_data)
            building.routes.add(route_instance)

        building.save()
        return building

    def update(self, instance, validated_data):
        images_data = validated_data.pop("images", None)
        floors_data = validated_data.pop("floors", None)
        routes_data = validated_data.pop("routes", None)
        location_data = validated_data.pop("location", None)

        # --- Location update/create ---
        if location_data:
            if instance.location:
                for attr, value in location_data.items():
                    setattr(instance.location, attr, value)
                instance.location.save()
            else:
                loc_obj, _ = Location.objects.get_or_create(
                    lat=location_data.get("lat"),
                    lang=location_data.get("lang"),
                    alt=location_data.get("alt", None)
                )
                instance.location = loc_obj

        # --- Update other simple fields ---
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # --- Images (replace) ---
        if images_data is not None:
            instance.images.clear()
            for image_data in images_data:
                img_instance = ImageHandler.objects.create(**image_data)
                instance.images.add(img_instance)

        # --- Floors (replace) ---
        if floors_data is not None:
            instance.floors.clear()

            for floor_data in floors_data:
                shape_data = floor_data.pop("shape", [])

                # IMPORTANT: JSON uses "widget" (singular)
                widgets_data = floor_data.pop("widget", [])
                floor_images_data = floor_data.pop("images", [])
                equipments_data = floor_data.pop("equipments", [])
                routes_data_floor = floor_data.pop("routes", [])

                floor = Floor.objects.create(
                    order_of_floor=floor_data.get("order_of_floor", 0),
                    width=floor_data.get("width", 0.0),
                    height=floor_data.get("height", 0.0),
                )

                # shape
                for loc in shape_data:
                    loc_obj = Location.objects.filter(
                        lat=loc.get("lat"),
                        lang=loc.get("lang"),
                        alt=loc.get("alt", None)
                    ).first()
                    if not loc_obj:
                        loc_obj = Location.objects.create(
                            lat=loc.get("lat"),
                            lang=loc.get("lang"),
                            alt=loc.get("alt", None)
                        )
                    floor.shape.add(loc_obj)

                # widgets
                for widget_data in widgets_data:
                    location_widget_data = widget_data.pop("location", None)
                    if location_widget_data:
                        loc_obj, _ = Location.objects.get_or_create(
                            lat=location_widget_data.get("lat"),
                            lang=location_widget_data.get("lang"),
                            alt=location_widget_data.get("alt", None)
                        )
                        widget_data["location"] = loc_obj
                    widget = Widget.objects.create(**widget_data)
                    floor.widget.add(widget)

                # images
                for image_data in floor_images_data:
                    img_instance = ImageHandler.objects.create(**image_data)
                    floor.images.add(img_instance)

                # equipments  <-- FIXED: attach to floor M2M
                for equipment_data in equipments_data:
                    widget_data = equipment_data.pop("widget", None)
                    if widget_data:
                        loc_w_data = widget_data.pop("location", None)
                        if loc_w_data:
                            loc_obj = Location.objects.filter(
                                lat=loc_w_data.get("lat"),
                                lang=loc_w_data.get("lang"),
                                alt=loc_w_data.get("alt", None)
                            ).first()
                            if not loc_obj:
                                loc_obj = Location.objects.create(
                                    lat=loc_w_data.get("lat"),
                                    lang=loc_w_data.get("lang"),
                                    alt=loc_w_data.get("alt", None)
                                )
                            widget_data["location"] = loc_obj
                        widget_instance = Widget.objects.create(**widget_data)
                        equipment_data["widget"] = widget_instance

                    equipment_instance = Equipment.objects.create(**equipment_data)
                    floor.equipments.add(equipment_instance)

                # routes  <-- FIXED: clear/add via M2M
                floor.routes.clear()
                for route_data in routes_data_floor:
                    location_route_data = route_data.pop("location", None)
                    if location_route_data:
                        loc_obj = Location.objects.filter(
                            lat=location_route_data.get("lat"),
                            lang=location_route_data.get("lang"),
                            alt=location_route_data.get("alt", None)
                        ).first()
                        if not loc_obj:
                            loc_obj = Location.objects.create(
                                lat=location_route_data.get("lat"),
                                lang=location_route_data.get("lang"),
                                alt=location_route_data.get("alt", None)
                            )
                        route_data["location"] = loc_obj

                    route_instance = Route.objects.create(**route_data)
                    floor.routes.add(route_instance)
                    instance.routes.add(route_instance)  # optional

                floor.save()
                instance.floors.add(floor)

        # --- Building routes (replace)  <-- FIXED: use the M2M directly ---
        if routes_data is not None:
            instance.routes.clear()
            for route_data in routes_data:
                location_route_data = route_data.pop("location", None)
                if location_route_data:
                    loc_obj = Location.objects.filter(
                        lat=location_route_data.get("lat"),
                        lang=location_route_data.get("lang"),
                        alt=location_route_data.get("alt", None)
                    ).first()
                    if not loc_obj:
                        loc_obj = Location.objects.create(
                            lat=location_route_data.get("lat"),
                            lang=location_route_data.get("lang"),
                            alt=location_route_data.get("alt", None)
                        )
                    route_data["location"] = loc_obj

                route_instance = Route.objects.create(**route_data)
                instance.routes.add(route_instance)

        return instance



class ConstatnsSerializer(serializers.Serializer):

    type_of_constant = serializers.CharField()




