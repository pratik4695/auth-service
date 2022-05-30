from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from core.document.file_validator import FileValidator
from utils import generate_file_path

class DocumentType(models.Model):
    name = models.CharField(
        _("Document Type"),
        max_length=64,
        null=False,
        unique=True,
        help_text=_("Document name like Aadhar, Permanent Account Number, etc.."),
    )
    code = models.CharField(
        _("Document Code"),
        max_length=25,
        validators=[
            RegexValidator(
                regex=r"^[a-zA-Z_][a-zA-Z_]+$",
                message=_("Code can only contain the letters a-z, A-Z and underscore"),
            ),
        ],
        help_text=_("Short name for document. PAN for Permanent Account Number, etc.."),
    )
    creation_date = models.DateTimeField(_("Creation Date"), auto_now_add=True)

    IDENTIFIERS = (
        ('not_specified', _("Not Specified")),
    )

    identifier = models.CharField(
        _("Document Identifier"),
        default='not_specified',
        max_length=100,
        choices=IDENTIFIERS,
    )

    is_document_mandatory = models.BooleanField(
        _("Is Mandatory"), default=False, db_index=True
    )
    is_expire_needed = models.BooleanField(
        _("Is Expire Needed"), default=False, db_index=True
    )
    is_mandatory_for_registration = models.BooleanField(
        _("Is Mandatory for Registration"), default=False, db_index=True
    )

    sequence = models.PositiveIntegerField(_('Sequence'), default = 0)
    
    instruction_heading = models.CharField(_("Instruction Heading"), 
        max_length=255, null=True, blank=True
    )
    instructions = models.JSONField(blank=True, null=True)

    no_of_pages = models.PositiveIntegerField(_('No of Pages'), default = 1)

    regex = models.TextField(_("Regex"), default='.*')

    error_message = models.CharField(_("error message"), default='error', max_length=150)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Document Type")
        verbose_name_plural = _("Document Types")



class DocumentPage(models.Model):
    page_number = models.PositiveIntegerField(_("Page Number"))

    file = models.FileField(
        upload_to=generate_file_path, validators=[FileValidator()], max_length=256)

    uploaded_at = models.DateTimeField(_('Date Uploaded'), auto_now_add = True)

    def __str__(self):
        return self.file

    class Meta:
        abstract = True
        app_label = "documentpage"
        verbose_name = _("DocumentPage")
        verbose_name_plural = _("DocumentPages")


class Document(models.Model):
    file = models.FileField(
        upload_to=generate_file_path, validators=[FileValidator()], max_length=256
    )
    document_type = models.ForeignKey(
        DocumentType,
        on_delete=models.PROTECT,
        help_text=_("Document Type"),
    )

    number = models.CharField(
        _("Document Number"),
        max_length=100,
        default="----",
        help_text=_("Input the number from the file uploaded.."),
    )

    VERIFICATION_PENDING = "verification_pending"
    ACTIVE = "active"
    INACTIVE = "inactive"
    REJECTED = "rejected"
    EXPIRED = "Expired"
    DOCUMENT_STATUSES = (
        (VERIFICATION_PENDING, _("Verification pending")),
        (ACTIVE, _("Active")),
        (INACTIVE, _("Inactive")),
        (REJECTED, _("Rejected")),
        (EXPIRED, _("Expired")),
    )

    status = models.CharField(
        _("Status"),
        max_length=25,
        choices=DOCUMENT_STATUSES,
        default=VERIFICATION_PENDING,
        help_text=_("Current status of document. Active/inactive, etc.."),
    )

    expiry_date = models.DateField(
        _("Expiry Date"), blank=True, null=True, help_text=_("Expiry date of document")
    )
    date_uploaded = models.DateTimeField(_("Date uploaded"), auto_now_add=True)

    def __str__(self):
        return self.file

    class Meta:
        abstract = True
        app_label = "document"
        verbose_name = _("Document")
        verbose_name_plural = _("Documents")

