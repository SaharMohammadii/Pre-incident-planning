from django.db import models
from django.conf import settings



class FormTemplate(models.Model):
    STANDARD = "STANDARD"
    ECO = "ECO"
    TYPE_CHOICES = [(STANDARD, "Standard"), (ECO, "Eco")]

    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=STANDARD)
    version = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("name", "version")
        ordering = ["-created_at", "-version"]

    def __str__(self):
        return f"{self.name} v{self.version} ({self.type})"


class SectionTemplate(models.Model):
    form = models.ForeignKey(FormTemplate, on_delete=models.CASCADE, related_name="sections")
    parent = models.ForeignKey('self', null=True, blank=True,
                               on_delete=models.CASCADE, related_name="children")
    order = models.PositiveIntegerField(default=1)
    title = models.CharField(max_length=255)

    class Meta:
        ordering = ["parent__id", "order", "id"]

    def __str__(self):
        return self.title


class ItemTemplate(models.Model):
    section = models.ForeignKey(SectionTemplate, on_delete=models.CASCADE, related_name="items")
    order = models.PositiveIntegerField(default=1)
    body = models.CharField(max_length=255)
    extra_description = models.TextField(blank=True)
    required = models.BooleanField(default=False)

    class Meta:
        ordering = ["section_id", "order", "id"]

    def __str__(self):
        return self.body



class FormResponse(models.Model):
    template = models.ForeignKey(FormTemplate, on_delete=models.PROTECT, related_name="responses")

    # shared meta
    owner_name = models.CharField(max_length=255, blank=True, null=True)
    renewal_code = models.CharField(max_length=255, blank=True, null=True)
    infrastructure = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    area = models.FloatField(blank=True, null=True)

    # eco-only meta (optional to fill)
    forward_number = models.CharField(max_length=255, blank=True, null=True)
    visited_date = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    staff_visited = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"Response #{self.id} → {self.template}"


class SectionResponse(models.Model):
    form_response = models.ForeignKey(FormResponse, on_delete=models.CASCADE, related_name="section_responses")
    section_template = models.ForeignKey(SectionTemplate, on_delete=models.PROTECT)
    title_snapshot = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=1)
    parent = models.ForeignKey('self', null=True, blank=True,
                               on_delete=models.CASCADE, related_name="children")

    class Meta:
        ordering = ["parent__id", "order", "id"]


class ItemResponse(models.Model):
    YES = "YES"
    NO = "NO"
    NA = "NA"
    UNANSWERED = "UNANSWERED"
    ANSWER_CHOICES = [(YES, "Yes"), (NO, "No"), (NA, "N/A"), (UNANSWERED, "Unanswered")]

    section_response = models.ForeignKey(SectionResponse, on_delete=models.CASCADE, related_name="items")
    item_template = models.ForeignKey(ItemTemplate, on_delete=models.PROTECT)

    body_snapshot = models.CharField(max_length=255)
    extra_description_snapshot = models.TextField(blank=True)

    answer = models.CharField(max_length=12, choices=ANSWER_CHOICES, default=UNANSWERED)
    note = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["section_response_id", "order", "id"]
