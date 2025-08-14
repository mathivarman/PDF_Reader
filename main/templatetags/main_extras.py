from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
import re

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
    
    # Remove "Processing Notes:" prefix if present, but keep everything else
    if "Processing Notes:" in processing_notes:
        processing_notes = processing_notes.replace("Processing Notes:", "").strip()
    
    if "Simple Summary:" in processing_notes:
        parts = processing_notes.split("Simple Summary:")
        if len(parts) > 1:
            summary = parts[1].strip()
            
            # Clean up the summary and ensure proper HTML formatting
            summary = summary.strip()
            
            # Remove any extra whitespace around HTML tags but preserve line breaks
            summary = re.sub(r'[ \t]+', ' ', summary)
            
            # Ensure proper line breaks for readability
            summary = summary.replace('\n', '<br>')
            
            # Mark as safe HTML content so Django renders the HTML properly
            return mark_safe(summary)
    
    return ""
