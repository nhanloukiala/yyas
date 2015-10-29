from django import template

register = template.Library()


@register.simple_tag()
def multiply(qty, unit_price, *args, **kwargs):
    # you would need to do any localization of the result here
    return "{0:.2f}".format(round(qty * unit_price, 2))
