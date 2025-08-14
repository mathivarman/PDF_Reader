from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def split(value, arg):
    """
    Split a string by the given argument and return a list.
    """
    return value.split(arg)

@register.filter
def extract_simple_summary(processing_notes):
    """
    Extract the simple summary from processing notes.
    """
    if not processing_notes:
        return ""
    
    if "Simple Summary:" in processing_notes:
        parts = processing_notes.split("Simple Summary:")
        if len(parts) > 1:
            summary = parts[1].strip()
            # Remove any leading/trailing whitespace and newlines
            summary = summary.strip()
            return summary
    
    return ""
