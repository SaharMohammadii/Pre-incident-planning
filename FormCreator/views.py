from rest_framework import viewsets, mixins, status
from .serializers import (
    FormTemplateSerializer,
    FormResponseCreateSerializer, 
    FormResponseReadSerializer,
    FormResponseMetaUpdateSerializer
)
from rest_framework.response import Response
from .models import FormResponse, FormTemplate, ItemResponse

from .serializers import (
    FormResponseCreateSerializer,
    FormResponseReadSerializer,
    FormResponseMetaUpdateSerializer,
    AnswerInputSerializer,
)
from rest_framework.decorators import action
from django.db import transaction




class TemplateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FormTemplate.objects.prefetch_related(
        "sections__items", "sections__children__items"
    )
    serializer_class = FormTemplateSerializer
    filterset_fields = ["type", "is_active", "name"]  
    search_fields = ["name"] 



class FormResponseViewSet(mixins.CreateModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.ListModelMixin,
                          mixins.UpdateModelMixin,
                          viewsets.GenericViewSet):
    queryset = FormResponse.objects.all().select_related("template")

    def get_serializer_class(self):
        if self.action == "create":
            return FormResponseCreateSerializer
        if self.action in ["update", "partial_update"]:
            return FormResponseMetaUpdateSerializer
        # for custom actions we’ll serialize the response with the read serializer
        return FormResponseReadSerializer

    @action(detail=True, methods=["post", "patch"], url_path="update_answers")
    def update_answers(self, request, pk=None):
        """
        Update answers for an existing FormResponse.
        Body shape:
        {
          "answers": [
            {"item_id": 123, "answer": "YES", "note": "ok"},
            {"item_id": 124, "answer": "NO"}
          ]
        }
        """
        # validate payload
        answers_payload = request.data.get("answers", [])
        ser = AnswerInputSerializer(data=answers_payload, many=True)
        ser.is_valid(raise_exception=True)

        resp: FormResponse = self.get_object()

        # build a map of existing ItemResponse by item_template_id
        existing = {
            ir.item_template_id: ir
            for ir in ItemResponse.objects.filter(
                section_response__form_response=resp
            )
        }

        with transaction.atomic():
            for payload in ser.validated_data:
                item_id = payload["item_id"]
                answer = payload.get("answer", ItemResponse.UNANSWERED)
                note = payload.get("note", "")

                ir = existing.get(item_id)
                if not ir:
                    # If the item wasn’t part of the original template/response tree,
                    # you can either skip it silently, raise a 400, or create it.
                    # Here we choose to fail fast:
                    return Response(
                        {"detail": f"ItemResponse for item_id={item_id} not found in this form response."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                ir.answer = answer
                ir.note = note
                ir.save(update_fields=["answer", "note"])

        # return the fresh read view
        return Response(FormResponseReadSerializer(resp).data, status=status.HTTP_200_OK)