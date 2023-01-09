import json

from django.utils.safestring import mark_safe
from django.template import Library

# Template tag for safe JavaScript variables
# https://stackoverflow.com/questions/298772/django-template-variables-and-javascript
register = Library()

@register.filter(is_safe=True)
def js(obj):
    return mark_safe(json.dumps(obj))
