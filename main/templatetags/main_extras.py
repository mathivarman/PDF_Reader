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

@register.simple_tag
def render_simple_summary(processing_notes):
    """
    Render the simple summary from processing notes as HTML.
    """
    if not processing_notes:
        return ""
    
    if "Simple Summary:" in processing_notes:
        parts = processing_notes.split("Simple Summary:")
        if len(parts) > 1:
            summary = parts[1].strip()
            # Clean up the summary and ensure proper HTML formatting
            summary = summary.strip()
            # Ensure the HTML is properly formatted
            import re
            # Remove any extra whitespace around HTML tags but preserve line breaks
            summary = re.sub(r'[ \t]+', ' ', summary)
            # Mark as safe HTML content
            from django.utils.safestring import mark_safe
            return mark_safe(summary)
    
    return ""
    
    if "Simple Summary:" in processing_notes:
        parts = processing_notes.split("Simple Summary:")
        if len(parts) > 1:
            summary = parts[1].strip()
            # Clean up the summary and ensure proper HTML formatting
            summary = summary.strip()
            # Ensure the HTML is properly formatted
            import re
            # Remove any extra whitespace around HTML tags but preserve line breaks
            summary = re.sub(r'[ \t]+', ' ', summary)
            # Mark as safe HTML content
            from django.utils.safestring import mark_safe
            return mark_safe(summary)
    
    return ""
