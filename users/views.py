from django.shortcuts import render,get_object_or_404,redirect
from .models import EmployeeProfile
from django.contrib import auth
from django.contrib.auth.decorators import login_required
#тут нужно добавить откуда-то руку для взятия jwt токенов - 2-х
# Create your views here.



def employee_list(request):
    employee = EmployeeProfile.objects.all().order_by('-name')
    return render(request,'users/users_list.html',{'employee': employee})


#по идее поле для руки с показом инфы с бд для каждого юзера
# нужно jwt, но не знаю где
#так же нужно добавить синхру для юзеров на fast и slow jwt
@login_required
def jwt_sync(jwt_jwt_fast_token,jwt_slow_token,request):
    def jwt_fast_sync(jwt_fast_token,request):
        pass

    def jwt_slow_sync(jwt_slow_token,request):
        pass
