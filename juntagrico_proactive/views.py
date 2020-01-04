from datetime import date

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404

from juntagrico.views import get_menu_dict as juntagrico_get_menu_dict

from juntagrico_proactive.forms import AssignmentRequestForm, AssignmentResponseForm
from juntagrico_proactive.mailer import MemberNotification, AdminNotification
from juntagrico_proactive.models import AssignmentRequest


def get_menu_dict(request):
    if request.user.is_authenticated and hasattr(request.user, "member"):
        renderdict = juntagrico_get_menu_dict(request)
        renderdict.update({'menu': {'request_assignment': 'active'}, })
        return renderdict
    return {}


@login_required
def request_assignment(request, sent=False):
    """
    Request an assignment
    """

    member = request.user.member
    assignment_request_form = AssignmentRequestForm(request.POST or None)
    if request.method == 'POST' and assignment_request_form.is_valid():
        # Create request
        assignment_request = assignment_request_form.instance
        assignment_request.member = member
        assignment_request.save()
        AdminNotification.request_created(assignment_request)
        return redirect('proactive-assignment-requested')

    assignment_requests = AssignmentRequest.objects.filter(member=member)

    renderdict = get_menu_dict(request)
    renderdict.update({
        'assignment_requests': assignment_requests,
        'form': assignment_request_form,
        'sent': sent
    })
    return render(request, "proactive/request_assignment.html", renderdict)


@login_required
def delete_request_assignment(request, request_id):
    """
    Request an assignment
    """

    assignment_request = get_object_or_404(AssignmentRequest, id=request_id)
    if assignment_request.member == request.user.member\
            and not assignment_request.assignment:
        assignment_request.delete()
    return redirect('proactive-request-assignment')


@login_required
def edit_request_assignment(request, request_id):
    """
    Request an assignment
    """

    member = request.user.member
    assignment_request = get_object_or_404(AssignmentRequest, id=request_id, member=member)
    assignment_request_form = AssignmentRequestForm(request.POST or None, instance=assignment_request)
    if request.method == 'POST' and assignment_request_form.is_valid():
        # edit request
        assignment_request = assignment_request_form.instance
        assignment_request.status = AssignmentRequest.REQUESTED
        assignment_request.save()
        AdminNotification.request_changed(assignment_request)
        return redirect('proactive-assignment-requested')

    renderdict = get_menu_dict(request)
    renderdict.update({
        'form': assignment_request_form,
    })
    return render(request, "proactive/edit_assignment_request.html", renderdict)


@permission_required('juntagrico_proactive.can_confirm_assignments')
def list_assignment_requests(request):
    """
    List assignment requests
    """

    assignment_requests = AssignmentRequest.objects.all()
    renderdict = get_menu_dict(request)
    renderdict.update({
        'assignment_requests': assignment_requests,
    })
    return render(request, "proactive/list_assignment_requests.html", renderdict)


@permission_required('juntagrico_proactive.can_confirm_assignments')
def respond_assignment_request(request, request_id):
    """
    Confirm or reject an assignment request
    """

    assignment_request = get_object_or_404(AssignmentRequest, id=request_id)
    assignment_response_form = AssignmentResponseForm(request.POST or None, instance=assignment_request)
    if request.method == 'POST' and assignment_response_form.is_valid():
        assignment_request = assignment_response_form.instance
        assignment_request.response_date = date.today()
        if 'confirm' in request.POST:
            assignment_request.status = AssignmentRequest.CONFIRMED
        elif 'reject' in request.POST:
            assignment_request.status = AssignmentRequest.REJECTED
        AdminNotification.request_handled_by_other_approver(assignment_request, request.user.member)
        assignment_request.approver = request.user.member
        assignment_request.save()
        MemberNotification.request_handled(assignment_request)
        return redirect('proactive-list-assignment-requests')

    renderdict = get_menu_dict(request)
    renderdict.update({
        'assignment_request': assignment_request,
        'form': assignment_response_form,
    })
    return render(request, "proactive/respond_assignment_request.html", renderdict)


@permission_required('juntagrico_proactive.can_confirm_assignments')
def confirm_assignment_request(request, request_id):
    """
    Confirm an assignment request directly
    """
    assignment_request = get_object_or_404(AssignmentRequest, id=request_id)
    if not assignment_request.is_confirmed():
        assignment_request.response_date = date.today()
        assignment_request.response = ''
        assignment_request.status = AssignmentRequest.CONFIRMED
        AdminNotification.request_handled_by_other_approver(assignment_request, request.user.member)
        # overwrite approver in any case to actual approver
        assignment_request.approver = request.user.member
        assignment_request.save()
        MemberNotification.request_handled(assignment_request)
    return redirect('proactive-list-assignment-requests')
