import string
import random
from datetime import date, datetime
from django.conf import settings


MEDIA_UPLOAD_STRUCTURE = getattr(settings, "MEDIA_UPLOAD_STRUCTURE", "")

def get_unique_friendly_id(self, prefix=None, upper_case=False, length=6):
    """
    Returns a unique friendly id.
    """

    chars = string.digits + string.ascii_uppercase
    size = len(chars)
    year = 2015
    friendly_id = None
    reference_date = datetime(year, 1, 1)
    now = datetime.now()
    delta = now - reference_date
    days_since = delta.days
    day = self.encode_day(days_since, size, chars)
    for size in [3, 4]:
        for i in range(length):
            code = ''.join(random.sample(chars, size))
            friendly_id = day + code

    if prefix:
        friendly_id = prefix + '-' + friendly_id
    
    if upper_case:
        friendly_id = friendly_id.upper()

    return friendly_id


def generate_file_path(instance, filename):
    """
    Returns the file path as per the defined directory structure.
    """

    doc_code = instance.document_type.code.replace(" ", "_") if hasattr(instance, "document_type") else ""
    module_name = instance._meta.app_label + "s"
    instance_label = instance._meta.object_name.lower().replace("document", "")
    if hasattr(instance, instance_label+"_id"):
        instance_handle = instance_label + "_" + str(getattr(instance, instance_label+"_id"))
    else:
        instance_handle = instance_label + "_" + str(instance.id)

    file_name = str(date.today()) + "/" + get_unique_friendly_id() + "/" + filename.upper()

    return MEDIA_UPLOAD_STRUCTURE.format(
        module_name=module_name,
        instance_handle=instance_handle,
        doc_code=doc_code,
        file_name=file_name
    ).replace("//", "/")
