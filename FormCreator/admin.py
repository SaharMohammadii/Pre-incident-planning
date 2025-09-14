from django.contrib import admin
from .models import (
    FormTemplate, SectionTemplate, ItemTemplate,
    FormResponse, SectionResponse, ItemResponse
)

class ItemTemplateInline(admin.TabularInline):
    model = ItemTemplate
    extra = 0

class SectionTemplateInline(admin.StackedInline):
    model = SectionTemplate
    extra = 0
    show_change_link = True

@admin.register(FormTemplate)
class FormTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "version", "is_active", "created_at")
    list_filter = ("type", "is_active")
    search_fields = ("name",)
    inlines = [SectionTemplateInline]

@admin.register(SectionTemplate)
class SectionTemplateAdmin(admin.ModelAdmin):
    list_display = ("title", "form", "parent", "order")
    inlines = [ItemTemplateInline]

@admin.register(ItemTemplate)
class ItemTemplateAdmin(admin.ModelAdmin):
    list_display = ("body", "section", "order", "required")

@admin.register(FormResponse)
class FormResponseAdmin(admin.ModelAdmin):
    list_display = ("id", "template", "owner_name", "created_at")

@admin.register(SectionResponse)
class SectionResponseAdmin(admin.ModelAdmin):
    list_display = ("id", "form_response", "title_snapshot", "order", "parent")

@admin.register(ItemResponse)
class ItemResponseAdmin(admin.ModelAdmin):
    list_display = ("id", "section_response", "body_snapshot", "answer", "order")
