from django import template
from django.urls import reverse

register = template.Library()


@register.inclusion_tag('activityprofile/snippets/edit_link.html', takes_context=True)
def edit_link(context):
    user = context['request'].user
    area = context['area']
    add_url = ''
    edit_url = ''
    if user.is_superuser or \
            user.has_perm('activityprofile.change_activityprofile') and \
            not user.has_perm('juntagrico.is_area_admin') or \
            area.coordinator == user.member:
        try:
            edit_url = reverse('admin:activityprofile_activityprofile_change', args=(area.profile.id,))
        except AttributeError:
            edit_url = reverse('admin:juntagrico_activityarea_change', args=(area.id,))
            add_url = reverse('admin:activityprofile_activityprofile_add')
    return {
        'edit_url': edit_url,
        'add_url': add_url
    }
