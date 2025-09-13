# Шаблонный фильтр для медиафайлов (users/templatetags/my_tags.py)

from django import template

register = template.Library()


@register.filter()
def media_filter(path):
    if path:
        return f"/media/{path}"
    return "#"
