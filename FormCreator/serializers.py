from rest_framework import serializers
from .models import (
    FormTemplate, SectionTemplate, ItemTemplate,
    FormResponse, SectionResponse, ItemResponse
)
from django.contrib.auth import get_user_model
User = get_user_model()


class ItemTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemTemplate
        fields = ["id", "order", "body", "extra_description", "required"]

class SectionTemplateSerializer(serializers.ModelSerializer):
    items = ItemTemplateSerializer(many=True, read_only=True)
    children = serializers.SerializerMethodField()

    class Meta:
        model = SectionTemplate
        fields = ["id", "order", "title", "parent", "items", "children"]

    def get_children(self, obj):
        qs = obj.children.all().order_by("order", "id")
        return SectionTemplateSerializer(qs, many=True).data

class FormTemplateSerializer(serializers.ModelSerializer):
    sections = serializers.SerializerMethodField()

    class Meta:
        model = FormTemplate
        fields = ["id", "name", "type", "version", "is_active", "created_at", "sections"]

    def get_sections(self, obj):
        roots = obj.sections.filter(parent__isnull=True).order_by("order", "id")
        return SectionTemplateSerializer(roots, many=True).data



class AnswerInputSerializer(serializers.Serializer):
    item_id = serializers.IntegerField()
    answer = serializers.ChoiceField(choices=ItemResponse.ANSWER_CHOICES, default=ItemResponse.UNANSWERED)
    note = serializers.CharField(allow_blank=True, required=False)

class FormResponseCreateSerializer(serializers.ModelSerializer):
    answers = AnswerInputSerializer(many=True, required=False)

    class Meta:
        model = FormResponse
        fields = [
            "id", "template",
            "owner_name", "renewal_code", "infrastructure", "address",
            "phone_number", "area", "forward_number", "visited_date",
            "description", "answers"
        ]

    def validate(self, attrs):
        template = attrs.get("template")
        if not template:
            raise serializers.ValidationError({"template": "Template is required."})
        return attrs

    def create(self, validated_data):
        from django.db import transaction

        answers = {a["item_id"]: a for a in validated_data.pop("answers", [])}
        template = validated_data["template"]

        with transaction.atomic():
            resp = FormResponse.objects.create(**validated_data)

            section_map = {}

            def build_sections(parent_st: SectionTemplate | None, parent_sr: SectionResponse | None):
                qs = template.sections.filter(parent=parent_st).order_by("order", "id")
                for st in qs:
                    sr = SectionResponse.objects.create(
                        form_response=resp,
                        section_template=st,
                        title_snapshot=st.title,
                        order=st.order,
                        parent=parent_sr
                    )
                    section_map[st.id] = sr

                    for it in st.items.all().order_by("order", "id"):
                        payload = answers.get(it.id)
                        ans = payload["answer"] if payload else ItemResponse.UNANSWERED
                        note = payload.get("note", "") if payload else ""
                        ItemResponse.objects.create(
                            section_response=sr,
                            item_template=it,
                            body_snapshot=it.body,
                            extra_description_snapshot=it.extra_description,
                            answer=ans,
                            note=note,
                            order=it.order,
                        )

                    # recurse for children
                    build_sections(st, sr)

            build_sections(parent_st=None, parent_sr=None)

        return resp


class ItemResponseReadSerializer(serializers.ModelSerializer):
    item_id = serializers.IntegerField(source="item_template.id", read_only=True)

    class Meta:
        model = ItemResponse
        fields = [
            "id", "item_id", "order",
            "body_snapshot", "extra_description_snapshot",
            "answer", "note"
        ]

class SectionResponseReadSerializer(serializers.ModelSerializer):
    items = ItemResponseReadSerializer(many=True, read_only=True)
    children = serializers.SerializerMethodField()

    class Meta:
        model = SectionResponse
        fields = ["id", "order", "title_snapshot", "parent", "items", "children"]

    def get_children(self, obj):
        qs = obj.children.all().order_by("order", "id")
        return SectionResponseReadSerializer(qs, many=True).data


class SlimFormTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormTemplate
        fields = ["id", "name", "type", "version", "is_active", "created_at"]



class FormResponseReadSerializer(serializers.ModelSerializer):
    template = SlimFormTemplateSerializer(read_only=True)
    sections = serializers.SerializerMethodField()

    class Meta:
        model = FormResponse
        fields = [
            "id", "template",
            "owner_name", "renewal_code", "infrastructure", "address",
            "phone_number", "area", "forward_number", "visited_date",
            "description", "created_at", "sections"
        ]

    def get_sections(self, obj):
        roots = obj.section_responses.filter(parent__isnull=True).order_by("order", "id")
        return SectionResponseReadSerializer(roots, many=True).data




class FormResponseMetaUpdateSerializer(serializers.ModelSerializer):
    template = serializers.PrimaryKeyRelatedField(read_only=True)
    staff_visited = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), required=False
    )

    class Meta:
        model = FormResponse
        fields = [
            "template",
            "owner_name", "renewal_code", "infrastructure", "address",
            "phone_number", "area",
            "forward_number", "visited_date", "description", "staff_visited",
        ]

