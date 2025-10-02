from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Committee, CommitteeMembership, Member
from .forms import CommitteeForm, CommitteeMembershipForm
from django.db.models import Q

def committee_list(request):
    committees = Committee.objects.all().prefetch_related('memberships__member')
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        committees = committees.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(committees, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query or '',
    }
    return render(request, 'committees/committee_list.html', context)

def committee_detail(request, pk):
    committee = get_object_or_404(Committee, pk=pk)
    memberships = committee.memberships.all().select_related('member')
    non_members = Member.objects.exclude(
        id__in=committee.memberships.values_list('member__id', flat=True)
    )
    
    context = {
        'committee': committee,
        'memberships': memberships,
        'non_members': non_members,
    }
    return render(request, 'committees/committee_detail.html', context)

@login_required
def committee_create(request):
    if request.method == 'POST':
        form = CommitteeForm(request.POST)
        if form.is_valid():
            committee = form.save()
            messages.success(request, f"Committee '{committee.name}' was created successfully!")

            # add committee leader as member if specified
            leader = form.cleaned_data.get('leader')
            if leader:
                CommitteeMembership.objects.create(
                    committee=committee,
                    member=leader,
                    role='Leader'
                )
                
            return redirect('committee-detail', pk=committee.pk)
    else:
        form = CommitteeForm()
    
    return render(request, 'committees/committee_form.html', {'form': form})

@login_required
def committee_update(request, pk):
    committee = get_object_or_404(Committee, pk=pk)
    
    if request.method == 'POST':
        form = CommitteeForm(request.POST, instance=committee)
        if form.is_valid():
            committee = form.save()
            messages.success(request, f"Committee '{committee.name}' was updated successfully!")
            return redirect('committee-detail', pk=committee.pk)
    else:
        form = CommitteeForm(instance=committee)
    
    return render(request, 'committees/committee_form.html', {'form': form})

@login_required
def committee_delete(request, pk):
    committee = get_object_or_404(Committee, pk=pk)
    
    if request.method == 'POST':
        committee_name = committee.name
        committee.delete()
        messages.success(request, f"Committee '{committee_name}' was deleted successfully!")
        return redirect('committee-list')
    
    return render(request, 'committees/committee_confirm_delete.html', {'committee': committee})

# API views for managing committee members
@login_required
@require_http_methods(["POST"])
def add_committee_member(request, committee_id):
    try:
        committee = Committee.objects.get(id=committee_id)
        member_id = request.POST.get('member_id')
        role = request.POST.get('role', '')
        
        if not member_id:
            return JsonResponse({
                'success': False,
                'message': 'Member ID is required'
            }, status=400)
        
        member = Member.objects.get(id=member_id)
        
        # Check if member is already in committee
        if CommitteeMembership.objects.filter(committee=committee, member=member).exists():
            return JsonResponse({
                'success': False,
                'message': f'{member.get_full_name()} is already in this committee'
            }, status=400)
        
        # Create membership
        CommitteeMembership.objects.create(
            committee=committee,
            member=member,
            role=role
        )
        
        return JsonResponse({
            'success': True,
            'message': f'{member.get_full_name()} added to committee'
        })
    except (Committee.DoesNotExist, Member.DoesNotExist):
        return JsonResponse({
            'success': False,
            'message': 'Committee or Member not found'
        }, status=404)

@login_required
@require_http_methods(["POST"])
def remove_committee_member(request, committee_id, membership_id):
    try:
        membership = CommitteeMembership.objects.get(id=membership_id, committee_id=committee_id)
        member_name = membership.member.get_full_name()
        membership.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'{member_name} removed from committee'
        })
    except CommitteeMembership.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Membership not found'
        }, status=404)

@login_required
@require_http_methods(["POST"])
def update_member_role(request, committee_id, membership_id):
    try:
        membership = CommitteeMembership.objects.get(id=membership_id, committee_id=committee_id)
        role = request.POST.get('role', '')
        
        membership.role = role
        membership.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Role updated for {membership.member.get_full_name()}'
        })
    except CommitteeMembership.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Membership not found'
        }, status=404)

@login_required
@require_http_methods(["POST"])
def set_committee_leader(request, committee_id):
    try:
        committee = Committee.objects.get(id=committee_id)
        member_id = request.POST.get('member_id')
        
        if not member_id:
            return JsonResponse({
                'success': False,
                'message': 'Member ID is required'
            }, status=400)
        
        member = Member.objects.get(id=member_id)
        
        # Check if member is part of the committee
        if not CommitteeMembership.objects.filter(committee=committee, member=member).exists():
            return JsonResponse({
                'success': False,
                'message': 'Member must be part of committee to be leader'
            }, status=400)
        
        committee.leader = member
        committee.save()
        
        return JsonResponse({
            'success': True,
            'message': f'{member.get_full_name()} set as committee leader'
        })
    except (Committee.DoesNotExist, Member.DoesNotExist):
        return JsonResponse({
            'success': False,
            'message': 'Committee or Member not found'
        }, status=404)