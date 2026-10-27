from django.shortcuts import get_object_or_404, render

from .models import Project


def index(request):
    projects = Project.objects.order_by('id')
    return render(request, 'projects/index.html', {'projects': projects})


def detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(request, 'projects/detail.html', {'project': project})
