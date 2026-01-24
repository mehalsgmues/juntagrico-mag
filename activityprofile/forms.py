from djrichtextfield.widgets import RichTextWidget
from juntagrico.forms import AreaDescriptionForm


class AreaProfileDescriptionForm(AreaDescriptionForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].widget = RichTextWidget(field_settings='activityprofile')
