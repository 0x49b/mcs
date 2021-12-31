from django.core.exceptions import ValidationError


def validate_file(value):
    value = str(value)
    if value.endswith(".zip"):
        return value
    else:
        raise ValidationError("Only Zip Files can be uploaded")
