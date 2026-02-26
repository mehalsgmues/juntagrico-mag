from django import template
from django.urls import reverse

register = template.Library()


@register.inclusion_tag('activityprofile/snippets/edit_link.html', takes_context=True)
def edit_link(context):
    user = context['request'].user
    area = context['area']
    edit_url = ''
    if user.has_perm('activityprofile.change_activityprofile'):
        try:
            edit_url = reverse('admin:activityprofile_activityprofile_change', args=(area.profile.id,))
        except AttributeError:
            if user.has_perm('juntagrico.change_activityarea'):
                edit_url = reverse('admin:juntagrico_activityarea_change', args=(area.id,))
    return {
        'edit_url': edit_url,
    }


@register.inclusion_tag('activityprofile/snippets/add_link.html', takes_context=True)
def add_link(context):
    user = context['request'].user
    add_url = ''
    if user.has_perm('activityprofile.add_activityprofile'):
        add_url = reverse('admin:activityprofile_activityprofile_add')
    return {
        'add_url': add_url
    }
