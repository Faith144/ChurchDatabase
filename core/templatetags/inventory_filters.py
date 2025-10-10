from django import template

register = template.Library()


@register.filter
def get_assembly_name(assemblies, assembly_id):
    """Get assembly name from ID"""
    try:
        assembly = assemblies.get(id=int(assembly_id))
        return assembly.name
    except:
        return "Unknown"
