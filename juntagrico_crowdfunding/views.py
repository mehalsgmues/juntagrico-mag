import datetime 

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django import forms
from django.contrib.auth import logout
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.models import User

from juntagrico_crowdfunding.forms import *

from juntagrico_crowdfunding.models import Fundable
from juntagrico_crowdfunding.models import Fund
from juntagrico_crowdfunding.models import FundingProject
from juntagrico_crowdfunding.models import Funder

from juntagrico.views import get_menu_dict as juntagrico_get_menu_dict
from juntagrico.util.management import password_generator

from juntagrico_crowdfunding.mailer import *

def get_menu_dict(request):
    if request.user.is_authenticated:
        if hasattr(request.user,"member"):
            renderdict = juntagrico_get_menu_dict(request)
            renderdict.update({'is_member': True, 'menu': {'crowdfunding': 'active'},})
            return renderdict
        elif hasattr(request.user,"funder"):
            return {'is_funder': True}
    return {}

def lost_session(request):
    """
    Session lost. start over
    """
    renderdict = get_menu_dict(request)
    return render(request, "cf/session_lost.html", renderdict)


def list_funding_projects(request):
    """
    List of fundingprojects
    """

    funding_projects = FundingProject.objects.filter(active = True)
    # don't show selection if only one active funding project exists
    if funding_projects.count() == 1:
        return list_fundables(request, funding_projects[0].id)

    else:

        renderdict = get_menu_dict(request)
        renderdict.update({
            'funding_projects': funding_projects
        })

        return render(request, "cf/list_funding_projects.html", renderdict)


def list_fundables(request, funding_project_id):
    """
    List of fundables
    """

    fundables = Fundable.objects.filter(funding_project_id = funding_project_id)

    my_funds = False
    if request.user.is_authenticated: # logged in
        if hasattr(request.user, 'funder'): # is funder
            my_funds = Fund.objects.filter(funder=request.user.funder, fundable__funding_project=funding_project_id)
        
    renderdict = get_menu_dict(request)
    renderdict.update({
        'fp': FundingProject.objects.filter(id = funding_project_id)[0],
        'fundables': fundables,
        'my_funds': my_funds
    })

    return render(request, "cf/list_fundables.html", renderdict)


def view_fundable(request, fundable_id):
    """
    Details of fundable
    """

    fundable = Fundable.objects.filter(id=fundable_id)[0]

    #evaluate form
    if request.method == 'POST':
        # store order
        fundForm = FundForm(fundable.available, request.POST)
    elif request.session.get('pastorder') is not None: #when changing order
        fundForm = FundForm(fundable.available, request.session.get('pastorder') )
    else:
        fundForm = FundForm(fundable.available)

    fundForm.fields['fundable'].initial = fundable # set fundable in form
    if hasattr(request.user,"funder"):
        fundForm.fields['sponsor'].initial = request.user.funder.first_name # set fundable in form
    

    if request.method == 'POST':
        if fundForm.is_valid():
            request.session['order'] = fundForm.cleaned_data
            request.session['pastorder'] = None #clear
            return HttpResponseRedirect('/cf/confirm')

    renderdict = get_menu_dict(request)
    renderdict.update({
        'fundable': fundable,
        'public_funds': fundable.fund_set.all,
        'fundForm': fundForm
    })
    return render(request, "cf/view_fundable.html", renderdict)


def fund(request, fundable_id):
    """
    Confirm funding
    """

    fundable = Fundable.objects.filter(id=fundable_id)[0]    

    renderdict = get_menu_dict(request)
    renderdict .update({
        'fundable': fundable
    })
    return render(request, "cf/fund.html", renderdict)


def signup(request):

    initial = {}
    if hasattr(request.user, 'member'): # copy from juntagrico member if available
        member = request.user.member
        initial = {
            'first_name': member.first_name,
            'last_name': member.last_name,
            'addr_street': member.addr_street,
            'addr_zipcode': member.addr_zipcode,
            'addr_location': member.addr_location,
            'phone': member.phone,
            'email': member.email
        }

    if request.method == 'POST':
        funderform = RegisterFunderForm(request.POST, initial=initial)
    elif request.session.get('pastfunder') is not None: #when changing funder
        funderform = RegisterFunderForm(instance=request.session.get('pastfunder'))
    else:
        funderform = RegisterFunderForm(initial=initial)

    renderdict = get_menu_dict(request)
    renderdict.update({
        'funderform': funderform
    })
    return render(request, "cf/signup.html", renderdict)


def confirm(request):
    """
    Confirm Fund
    """

    funder = False

    # 1. form evaluation
    if request.method == 'POST':
        print("parsing POST")
        # create funder from form
        funderform = RegisterFunderForm(request.POST)
        #TODO: Wenn E-mail schon existiert, darauf hinweisen, dass Benutzer sich einloggen soll.
        if funderform.is_valid():
            print("creating funder")
            funder = Funder(**funderform.cleaned_data)
            request.session['funder'] = funder

    # get funder (existing or about to be created)
    if request.user.is_authenticated and hasattr(request.user, 'funder'):
        # existing funder
        funder = request.user.funder
    elif request.session.get('funder') is not None:
        # new funder
        funder = request.session['funder']
            

    # if no user is logged in: show form to login or register
    if not funder:
        return signup(request)

    # process order
    order = request.session.get('order')
    if order is None:
        return lost_session(request) # session expired
    else:
        order.update( { 'contribution': order.get('quantity')*order.get('fundable').price })

    # save confirmed order
    if request.POST.get('confirm') == '1':
        print("creating fund")
        password = None
        if request.user.is_authenticated:
            funder.user = request.user
        else:
            password = password_generator()
            funder.user = User.objects.create_user(username=funder.email, password=password)

        fund = Fund(
            funder=funder,
            contribution=order.get('contribution'),
            fundable=order.get('fundable'),
            sponsor=order.get('sponsor'),
            message=order.get('message')
        )
        funding_project_id = order.get('fundable').funding_project.id
        
        #send confirmation email
        send_fund_confirmation_mail(fund, password)

        funder.user.save()
        funder.save()
        fund.funder = funder
        fund.save()

        # clear session and show thanks message
        request.session['funder'] = None
        request.session['pastfunder'] = None
        request.session['order'] = None
        request.session['pastorder'] = None
        return HttpResponseRedirect('/cf/thanks/'+str(funding_project_id))

    # show summary to confirm
    renderdict = get_menu_dict(request)
    renderdict .update({
        'order': order,
        'funder': funder
    })
    return render(request, "cf/confirm.html", renderdict)


def edit_order(request):
    """
    go back to order page
    """    

    if not request.session.get('order'):
        return lost_session(request) # session expired

    # delete order from session and pass its content to the order form
    request.session['pastorder'] = request.session.get('order')
    request.session['order'] = None
    return HttpResponseRedirect('/cf/view/'+str(request.session['pastorder'].get('fundable').id)+'/')


def edit_funder(request):
    """
    change funder but keep order
    """

    # logout in case funder is logged in
    if request.user.is_authenticated and hasattr(request.user,"funder"):
        order = request.session.get('order') # keep order
        logout(request)
        request.session['order'] = order
    else:
        # clear funder
        request.session['pastfunder'] = request.session.get('funder')
        request.session['funder'] = None

    return HttpResponseRedirect('/cf/confirm/')


def thanks(request, funding_project_id=None):
    """
    Thank you page
    """

    renderdict = get_menu_dict(request)
    if funding_project_id:
        renderdict.update({ 'funding_project': FundingProject.objects.get(id=funding_project_id) })
    return render(request, "cf/thanks.html", renderdict)


@login_required
def contribution(request):
    """
    List of personal contributions
    """

    contributions = False
    if hasattr(request.user, 'funder'): # is funder
        contributions = Fund.objects.filter(funder=request.user.funder)
        
    renderdict = get_menu_dict(request)
    renderdict.update({
        'contributions': contributions
    })

    return render(request, "cf/contribution.html", renderdict)
