from django import template
from django.utils.http import urlencode

register = template.Library()


# @register.filter
# def get_assembly_name(assemblies, assembly_id):
#     try:
#         return assemblies.get(id=assembly_id).name
#     except:
#         return "Unknown"


@register.filter
def status_count(items, status):
    return items.filter(status=status).count()


@register.filter
def div(value, arg):
    """Divide the value by the argument"""
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0


@register.simple_tag
def update_query_params(**kwargs):
    """Update query parameters in URL"""
    query_dict = {}
    for key, value in kwargs.items():
        if value:
            query_dict[key] = value
    return urlencode(query_dict)


@register.filter
def get_assembly_name(assemblies, assembly_id):
    """Get assembly name from ID"""
    try:
        assembly = assemblies.get(id=int(assembly_id))
        return assembly.name
    except:
        return "Unknown"


@register.filter
def div(value, arg):
    """Divide the value by the argument"""
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0
