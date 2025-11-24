from django.shortcuts import render

def index(request):
    return render(request, 'core/index.html')

def highschool_search(request):
    return render(request, 'core/highschool_search.html')