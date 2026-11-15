from django.contrib.auth.decorators import permission_required


mapjob_change_required = permission_required('mapjob.change_mapjob')
