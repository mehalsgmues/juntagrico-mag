
from juntagrico.util import addons
from juntagrico.admin import RecuringJob
from mehalsgmues.admin import JobAccessInfoInline

addons.config.register_model_inline(RecuringJob, JobAccessInfoInline)
