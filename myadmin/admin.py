from django.contrib import admin
from myadmin import models


@admin.register(models.ClientRecord)
class ClientRecordAdmin(admin.ModelAdmin):
    model = models.ClientRecord
    list_display = [
        "full_name",
        "identity",
        "gender",
        "phone_number",
        "email",
        "address1",
        "address2",
        "city",
        "postcode",
        "state",
        "country",
        "agent_fullname",
        "agent_ph",
        "agent_identity",
        "remark",
    ]

@admin.register(models.Case)
class CaseAdmin(admin.ModelAdmin):
    model = models.Case
    # list_display = "__all__"
    exclude = ["client_role", "clients","court_type",]


@admin.register(models.ClientRole)
class ClientRoleAdmin(admin.ModelAdmin):
    model = models.ClientRole
    # list_display = "__all__"




@admin.register(models.CourtType)
class CourtTypeAdmin(admin.ModelAdmin):
    model = models.CourtType
    # list_display = "__all__"


@admin.register(models.CaseAttachment)
class CaseAttachmentAdmin(admin.ModelAdmin):
    model = models.CaseAttachment


@admin.register(models.Payments)
class PaymentsAdmin(admin.ModelAdmin):
    model = models.Payments



