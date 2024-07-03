from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def has_certification(gown, certification_name):
    return gown.certificates.filter(name=certification_name).exists()

@register.filter
def get_emission_value(emissions_dict, args):
    gown_id, attribute = args.split('.')
    gown_id = int(gown_id)
    emission = emissions_dict.get(gown_id)
    return getattr(emission, attribute, None)