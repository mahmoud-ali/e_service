from django import template

register = template.Library()

@register.simple_tag
def get_item_from_list(arr,index):
    return str(arr[index])

