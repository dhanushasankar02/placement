from django.shortcuts import render, redirect

def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    return render(request, 'home/index.html')

def about(request):
    return render(request, 'home/about.html')

def contact(request):
    return render(request, 'home/contact.html')

def faq(request):
    return render(request, 'home/faq.html')
