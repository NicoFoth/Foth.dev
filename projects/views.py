from django.shortcuts import get_object_or_404, render

from .models import Project


def show_projects(request):
    projects = Project.objects.order_by('id')
    return render(request, 'projects/projects.html', {'projects': projects})


def show_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(request, 'projects/project.html', {'project': project})
