from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import SignUpForm, LoginForm
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated 

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()          
            login(request, user)        
            return redirect('home')  #поменять   
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    form = LoginForm(data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            email = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(email=email, password=password) 
            if user is not None:
                login(request, user)     
                return redirect('home')  #поменять  
    return render(request, 'login.html', {'form': form})


class HelloView(APIView):                       #для обкатки postman
    permission_classes = (IsAuthenticated,)             

    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)