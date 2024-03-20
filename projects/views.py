from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import Projects, Equipment, Insurance, Maintenance, Claim
from .forms import AddProjectForm, EditProjectForm, EquipmentForm, InsuranceForm, MaintenanceForm, ClaimForm
from django.db.models import Q
from django.contrib import messages

# Helper function to generate breadcrumbs
def generate_breadcrumbs(*custom_items):
    breadcrumbs = [
        {'name': 'Home', 'url': '/welcome/'},
        {'name': 'Projects List', 'url': '/project/'},
    ]
    breadcrumbs.extend(custom_items)
    return breadcrumbs

class IndexView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'projects.view_projects'
    raise_exception = True

    def get(self, request):
        project = Projects.objects.all()
        breadcrumbs = generate_breadcrumbs()
        context = {'project': project, 'breadcrumbs': breadcrumbs}
        return render(request, 'projects/index.html', context)

class AddProjectView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'projects.add_projects'
    raise_exception = True

    def get(self, request):
        form = AddProjectForm()
        breadcrumbs = generate_breadcrumbs({'name': 'Add Project'})
        context = {'form': form, 'breadcrumbs': breadcrumbs}
        return render(request, 'projects/add_project.html', context)

    def post(self, request):
        form = AddProjectForm(request.POST, request.FILES)
        if form.is_valid():
            user_string = str(request.user) if request.user.is_authenticated else 'default_by_user'
            form.instance.user = user_string
            form.save()
            return redirect('projects:index')
        else:
            breadcrumbs = generate_breadcrumbs({'name': 'Add Project'})
            context = {'form': form, 'breadcrumbs': breadcrumbs}
            return render(request, 'projects/add_project.html', context)

class EditProjectView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'projects.change_projects'
    raise_exception = True

    def get(self, request, project_id):
        project = get_object_or_404(Projects, pk=project_id)
        form = EditProjectForm(instance=project)
        breadcrumbs = generate_breadcrumbs({'name': f'Id {project_id} Edit'})
        context = {'form': form, 'project': project, 'breadcrumbs': breadcrumbs}
        return render(request, 'projects/edit_project.html', context)

    def post(self, request, project_id):
        project = get_object_or_404(Projects, pk=project_id)
        form = EditProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            user_string = str(request.user) if request.user.is_authenticated else 'default_by_user'
            form.instance.user = user_string
            form.save()
            return redirect('projects:index')
        else:
            breadcrumbs = generate_breadcrumbs({'name': f'Id {project_id} Edit'})
            context = {'form': form, 'project': project, 'breadcrumbs': breadcrumbs}
            return render(request, 'projects/edit_project.html', context)

class ProjectDetailsView(LoginRequiredMixin,PermissionRequiredMixin, View):
    permission_required = 'projects.view_projects'
    raise_exception = True

    def get(self, request, project_id):
        project = get_object_or_404(Projects, pk=project_id)
        equipment = Equipment.objects.filter(project=project_id)
        breadcrumbs = generate_breadcrumbs({'name': f'Project {project_id} Detail'})
        context = {
            'project': project,
            'equipment_data': equipment,
            'breadcrumbs': breadcrumbs,
        }
        return render(request, 'projects/detail_project.html', context)

class EquipmentAddView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'projects.add_equipment'
    raise_exception = True

    def get(self, request, project_id):
        project = get_object_or_404(Projects, pk=project_id)
        form = EquipmentForm(initial={'project': project})
        breadcrumbs = generate_breadcrumbs(
            {'name': f'Projects {project_id}', 'url': f'/project/{project_id}/detail/'},
            {'name': 'Add Equipment'},
        )
        context = {'form': form, 'breadcrumbs': breadcrumbs}
        return render(request, 'projects/add_equipment.html', context)

    def post(self, request, project_id):
        project = get_object_or_404(Projects, pk=project_id)
        form = EquipmentForm(request.POST, request.FILES)
        if form.is_valid():
            user_string = str(request.user) if request.user.is_authenticated else 'default_by_user'
            form.instance.user = user_string
            form.instance.project = project
            form.save()
            return redirect('projects:project_details', project_id=project_id)
        else:
            breadcrumbs = generate_breadcrumbs(
                {'name': f'Projects {project_id}', 'url': f'/project/{project_id}/detail/'},
                {'name': 'Add Equipment'}
                )
            context = {'form': form, 'breadcrumbs': breadcrumbs}
            return render(request, 'projects/add_equipment.html', context)

class EquipmentEditView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'projects.change_equipment'
    raise_exception = True

    def get(self, request, project_id, id):
        equipment = get_object_or_404(Equipment, pk=id)
        form = EquipmentForm(instance=equipment)
        breadcrumbs = generate_breadcrumbs(
            {'name': f'Projects {project_id}', 'url': f'/project/{project_id}/detail/'},
            {'name': f'Edit Equipment {equipment.id}'}
            )
        context = {'form': form, 'breadcrumbs': breadcrumbs}
        return render(request, 'projects/edit_equipment.html', context)

    def post(self, request, project_id, id):
        equipment = get_object_or_404(Equipment, pk=id)
        form = EquipmentForm(request.POST, request.FILES, instance=equipment)
        if form.is_valid():
            user_string = str(request.user) if request.user.is_authenticated else 'default_by_user'
            form.instance.user = user_string
            form.save()
            return redirect('projects:project_details', project_id=project_id)
        else:
            breadcrumbs = generate_breadcrumbs(
                {'name': f'Projects {project_id}', 'url': f'/project/{project_id}/detail/'},
                {'name': f'Edit Equipment {equipment.id}'}
                )
            context = {'form': form, 'breadcrumbs': breadcrumbs}
            return render(request, 'projects/edit_equipment.html', context)

class EquipmentDetailsView(LoginRequiredMixin,PermissionRequiredMixin, View):
    permission_required = 'projects.view_equipment'
    raise_exception = True

    def get(self, request, project_id, id):
        equipment = Equipment.objects.filter(Q(project=project_id) & Q(id=id))
        insurance = Insurance.objects.filter(Q(project=project_id) & Q(equipment=id))
        maintenance_data = sorted(Maintenance.objects.filter(Q(project=project_id) & Q(equipment=id)), key=lambda x: x.id, reverse=True)
        w_claim = Claim.objects.filter(Q(project=project_id) & Q(claim_type='Warranty') & Q(equipment=id))
        i_claim = Claim.objects.filter(Q(project=project_id) & Q(claim_type='Insurance') & Q(equipment=id))
        today = timezone.now().date()
        breadcrumbs = generate_breadcrumbs(
            {'name': f'Projects {project_id}', 'url': f'/project/{project_id}/detail/'},
            {'name': f'Equipment Detail'}
            )
        context = {
            'equipment_data': equipment,
            'insurance_data':insurance,
            'maintenance_data':maintenance_data,
            'w_claim':w_claim,
            'i_claim':i_claim,
            'today': today,
            'breadcrumbs': breadcrumbs,
        }
        return render(request, 'projects/equipment_detail.html', context)

class InsuranceAddView(LoginRequiredMixin,PermissionRequiredMixin, View):
    permission_required = 'projects.add_insurance'
    raise_exception = True

    def get(self, request, id, project_id):
        project = get_object_or_404(Projects, pk=project_id)
        equipment = get_object_or_404(Equipment, pk=id)
        breadcrumbs = generate_breadcrumbs(
            {'name': f'Projects {project_id}', 'url': f'/project/{project_id}/detail/'},
            {'name': f'Equipment {equipment.name}','url': f'/project/{project_id}/equipment-detail/{equipment.id}'},
            {'name': 'Add Insurance'}
            )
        existing_insurance = Insurance.objects.filter(project=project, equipment=equipment).first()
        if existing_insurance:
            error_message = "The selected equipment is already under insurance policy for this project."
            return render(request, 'projects/add_insurance.html', {'error_message': error_message, 'breadcrumbs':breadcrumbs})
        form = InsuranceForm()
        context = {'form': form, 'breadcrumbs': breadcrumbs}
        return render(request, 'projects/add_insurance.html', context)

    def post(self, request, id, project_id):
        project = get_object_or_404(Projects, pk=project_id)
        equipment = get_object_or_404(Equipment, pk=id)
        form = InsuranceForm(request.POST)
        if form.is_valid():
            insurance = form.save(commit=False)
            user_string = str(request.user) if request.user.is_authenticated else 'default_by_user'
            form.instance.user = user_string
            insurance.project = project
            insurance.equipment = equipment
            insurance.save()
            return redirect('projects:equipment_detail', project_id=project, id=equipment.id)
        else:
            breadcrumbs = generate_breadcrumbs(
                {'name': f'Projects {project_id}', 'url': f'/project/{project_id}/detail/'},
                {'name': f'Equipment {equipment.name}','url': f'/project/{project_id}/equipment-detail/{equipment.id}'},
                {'name': 'Add Insurance'}
                )
            context = {'form': form, 'breadcrumbs': breadcrumbs}
            return render(request, 'projects/add_insurance.html', context)

class InsuranceEditView(LoginRequiredMixin,PermissionRequiredMixin, View):
    permission_required = 'projects.change_insurance'
    raise_exception = True

    def get(self, request, project_id, id):
        insurance = get_object_or_404(Insurance, pk=id)
        form = InsuranceForm(instance=insurance)
        breadcrumbs = generate_breadcrumbs(
            {'name': f'Projects {project_id}', 'url': f'/project/{project_id}/detail/'},
            {'name': f'Equipment {insurance.equipment}','url': f'/project/{project_id}/equipment-detail/{insurance.equipment.id}'},
            {'name': 'Edit Insurance'}
            )
        context = {'form': form, 'breadcrumbs': breadcrumbs}
        return render(request, 'projects/edit_insurance.html', context)

    def post(self, request, project_id, id):
        project = get_object_or_404(Projects, pk=project_id)
        insurance = get_object_or_404(Insurance, pk=id)
        form = InsuranceForm(request.POST, request.FILES, instance=insurance)
        if form.is_valid():
            user_string = str(request.user) if request.user.is_authenticated else 'default_by_user'
            form.instance.user = user_string
            form.project = project
            form.insurance = insurance
            form.save()
            return redirect('projects:equipment_detail', project_id=project, id=insurance.equipment.id)
        else:
            breadcrumbs = generate_breadcrumbs(
                {'name': f'Projects {project_id}', 'url': f'/project/{project_id}/detail/'},
                {'name': f'Equipment {insurance.equipment}','url': f'/project/{project_id}/equipment-detail/{insurance.equipment.id}'},
                {'name': 'Edit Insurance'}
                )
            context = {'form': form, 'breadcrumbs': breadcrumbs}
            return render(request, 'projects/edit_insurance.html', context)

class AddMaintenanceView(LoginRequiredMixin,PermissionRequiredMixin, View):
    permission_required = 'projects.add_maintenance'
    raise_exception = True

    def get(self, request, project_id, equipment_id):
        project = get_object_or_404(Projects, pk=project_id)
        equipment = get_object_or_404(Equipment, pk=equipment_id)
        form = MaintenanceForm(initial={'project': project})
        breadcrumbs = generate_breadcrumbs(
            {'name': f'Projects {project_id}', 'url': f'/project/{project_id}/detail/'},
            {'name': f'Equipment {equipment.name}','url': f'/project/{project_id}/equipment-detail/{equipment.id}'},
            {'name': 'Maintenance'}
            )
        context = {'form': form, 'breadcrumbs': breadcrumbs}
        return render(request, 'projects/add_maintenance.html', context)

    def post(self, request, project_id, equipment_id):
        project = get_object_or_404(Projects, pk=project_id)
        equipment = get_object_or_404(Equipment, pk=equipment_id)
        form = MaintenanceForm(request.POST, request.FILES)
        if form.is_valid():
            user_string = str(request.user) if request.user.is_authenticated else 'default_by_user'
            form.instance.user = user_string
            form.instance.project = project
            form.instance.equipment = equipment
            form.save()
            return redirect('projects:equipment_detail', project_id=project, id=equipment.id)
        else:
            breadcrumbs = generate_breadcrumbs(
                {'name': f'Projects {project_id}', 'url': f'/project/{project_id}/detail/'},
                {'name': f'Equipment {equipment.name}','url': f'/project/{project_id}/equipment-detail/{equipment.id}'},
                {'name': 'Maintenance'}
                )
            context = {'form': form, 'breadcrumbs': breadcrumbs}
            return render(request, 'projects/add_maintenance.html', context)

class MaintenanceDetailsView(LoginRequiredMixin,PermissionRequiredMixin, View):
    permission_required = 'projects.view_maintenance'
    raise_exception = True

    def get(self, request, project_id, equipment_id,maintenance_id):
            
            maintenance = Maintenance.objects.get(project=project_id, equipment=equipment_id, id=maintenance_id)
            request_user_str = str(request.user)
            # Check if maintenance is already approved
            if maintenance.approval:
                can_approve = False
            elif request_user_str == maintenance.user:
                # If the logged-in user is the same as the maintenance user, they cannot approve
                can_approve = False
            else:
                # Otherwise, the user can approve
                can_approve = True
        
            breadcrumbs = generate_breadcrumbs(
                {'name': f'Projects {project_id}', 'url': f'/project/{project_id}/detail/'},
                {'name': f'Equipment Detail', 'url': f'/project/{project_id}/equipment-detail/{equipment_id}'},
                {'name': f'Maintenance Detail'},
                )
            context = {
                'maintenance':maintenance,
                'breadcrumbs': breadcrumbs,
                'can_approve': can_approve,
            }
            return render(request, 'projects/maintenance_details.html', context)
    
class MaintenanceEditView(LoginRequiredMixin,PermissionRequiredMixin, View):
    permission_required = 'projects.change_maintenance'
    raise_exception = True
    def post(self, request, project_id, equipment_id, maintenance_id):
        maintenance = get_object_or_404(Maintenance, id=maintenance_id)
        maintenance.approval = True
        maintenance.save()

        # Redirect to equipment detail view
        return redirect('projects:equipment_detail', project_id=project_id, id=equipment_id)

 
    


class AddClaimView(LoginRequiredMixin,PermissionRequiredMixin, View):
    permission_required = 'projects.add_claim'
    raise_exception = True
    def get(self, request, equipment_id, project_id, insurance_id):
        project = get_object_or_404(Projects, pk=project_id)
        equipment = get_object_or_404(Equipment, pk=equipment_id)
        insurance = get_object_or_404(Insurance, pk=insurance_id)
        type = "Insurance"
        form = ClaimForm()
        breadcrumbs = generate_breadcrumbs(
            {'name': f'Projects {project_id}', 'url': f'/project/{project_id}/detail/'},
            {'name': f'Equipment {equipment}','url': f'/project/{project_id}/equipment-detail/{equipment.id}'},
            {'name': 'Insurance Claim'}
            )
        context = {'form': form, 'breadcrumbs': breadcrumbs , 'type':type}
        return render(request, 'projects/add_claim.html', context)

    def post(self, request, equipment_id, project_id, insurance_id):
        project = get_object_or_404(Projects, pk=project_id)
        equipment = get_object_or_404(Equipment, pk=equipment_id)
        insurance = get_object_or_404(Insurance, pk=insurance_id)
        form = ClaimForm(request.POST)
        if form.is_valid():
            claim = form.save(commit=False)
            user_string = str(request.user) if request.user.is_authenticated else 'default_by_user'
            form.instance.user = user_string
            claim.project = project
            claim.equipment = equipment
            claim.insurance = insurance 
            claim.claim_type = "Insurance"
            claim.save()
            return redirect('projects:equipment_detail', project_id=project, id=equipment.id)
        else:
            breadcrumbs = generate_breadcrumbs(
                {'name': f'Projects {project_id}', 'url': f'/project/{project_id}/detail/'},
                {'name': f'Equipment {equipment}','url': f'/project/{project_id}/equipment-detail/{equipment.id}'},
                {'name': 'Insurance Claim'}
                )
            context = {'form': form, 'breadcrumbs': breadcrumbs}
            return render(request, 'projects/add_claim.html', context)
    
class AddWClaimView(LoginRequiredMixin, PermissionRequiredMixin,View):
    permission_required = 'projects.add_claim'
    raise_exception = True
    def get(self, request, project_id, equipment_id):
        project = get_object_or_404(Projects, pk=project_id)
        equipment = get_object_or_404(Equipment, pk=equipment_id)
        type = "Warranty"
        form = ClaimForm()
        breadcrumbs = generate_breadcrumbs(
            {'name': f'Projects {project_id}', 'url': f'/project/{project}/detail/'},
            {'name': f'{equipment} Detail', 'url': f'/project/{project}/equipment-detail/{equipment.id}'},
            {'name': 'W-G Claim'}
        )
        context = {'form': form, 'breadcrumbs': breadcrumbs,'type':type}
        return render(request, 'projects/add_claim.html', context)

    def post(self, request, project_id, equipment_id):
        project = get_object_or_404(Projects, pk=project_id)
        equipment = get_object_or_404(Equipment, pk=equipment_id)
        form = ClaimForm(request.POST)
        if form.is_valid():
            claim = form.save(commit=False)
            user_string = str(request.user) if request.user.is_authenticated else 'default_by_user'
            form.instance.user = user_string
            claim.project = project
            claim.equipment = equipment
            claim.claim_type = "Warranty" 
            claim.save()
            messages.success(request, 'Claim added successfully!')
            return redirect('projects:equipment_detail', project_id=project_id, id=equipment_id)
        else:
            messages.error(request, 'Please correct the errors below.')
            breadcrumbs = generate_breadcrumbs(
                {'name': f'Projects {project_id}', 'url': f'/project/{project_id}/detail/'},
                {'name': 'W Claim'}
            )
            context = {'form': form, 'breadcrumbs': breadcrumbs}
            return render(request, 'projects/add_claim.html', context)