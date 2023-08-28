import random
import string
import time

from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from referrals.models import UserProfile


@api_view(['GET'])
def entry_authorization_page(request):
    return render(request, 'login_step1.html')

@api_view(['GET'])
def entry_get_profile(request):
    return render(request, 'profile.html')


@api_view(['POST'])
def authenticate_user(request):
    # получаем номер телефона, инвайт из формы
    phone_number = request.data.get('phone_number')
    invite_code = request.data.get('invite_code')
    # передаем в request.session
    request.session['phone_number'] = phone_number
    request.session['invite_code'] = invite_code
    request.session.save()
    return render(request, 'login_step2.html')



@api_view(['POST'])
def verify_activation_code(request):
    activation_code = request.data.get('authorization_code')
    print(f'activation_code = {activation_code}')
    phone_number = request.session.get('phone_number')
    invite_code = request.session.get('invite_code')

    print(f'phone_number, invite_code в verify_activation_code = {phone_number, invite_code}')
    if activation_code:
        print(f'activation_code1 = {activation_code}')
        time.sleep(2)
        '''
        если пользователь с указанным номером сущесвует,
        возвращается кртеж с user и create = False
        если не существует, то user создается, created = True
        '''
        user, created = UserProfile.objects.get_or_create(phone_number=phone_number)

        invite_code_exist = UserProfile.objects.filter(invite_code=invite_code).exists()
        print(f'invite_code_exist is {invite_code_exist}')
        if created:
            if invite_code:
                if invite_code_exist:
                    '''
                    если введенный код принадлежит другому user:
                    записать инвайт-код новому user
                    '''
                    user.phone_number = phone_number
                    user.invite_code = invite_code
                    user.used_foreign_invite = True
                    user.save()
                    context = {
                        'message': 'created',
                        'phone_number': user.phone_number,
                        'invite_code': user.invite_code,
                        'used_foreign_invite': user.used_foreign_invite,
                        # 'referral_phone_numbers': user.referral_phone_numbers,
                    }
                    return render(request, 'profile.html', context)
                else:
                    return render(request, 'error_message.html',
                                  {'message': f'Invalid invite_code: {invite_code} or phone_number: {phone_number}'})


            else:
                '''
                если инвайт-код не вводился:
                сгенерировать и присвоить 
                '''
                user.phone_number = phone_number
                user.invite_code = ''.join(random.choice(string.ascii_uppercase + string.digits)
                                           for _ in range(6))
                user.save()
                context = {
                    'message': 'created',
                    'phone_number': user.phone_number,
                    'invite_code': user.invite_code,
                    'used_foreign_invite': user.used_foreign_invite,
                }
                return render(request, 'profile.html', context)

        else:
            context = {
                'message': 'authorized',
                'phone_number': user.phone_number,
                'invite_code': user.invite_code,
                'used_foreign_invite': user.used_foreign_invite,
            }
            return render(request, 'profile.html', context)
    else:
        return render(request, 'error_message.html',
                      {'message': f'activation_code is {activation_code}'})


@api_view(['POST'])
def get_user_profile(request):
    phone_number = request.data.get('phone_number')

    try:
        user = UserProfile.objects.get(phone_number=phone_number)
        referral_phone_numbers = []
        if not user.used_foreign_invite:
            referral_phone_numbers = [referral.phone_number for referral in
                                      UserProfile.objects.filter(invite_code=user.invite_code)
                                      if referral.phone_number != user.phone_number]

        context = {
            'phone_number': user.phone_number,
            'invite_code': user.invite_code,
            'used_foreign_invite': user.used_foreign_invite,
            'referral_phone_numbers': referral_phone_numbers,
        }
        return render(request, 'profile.html', context)
    except UserProfile.DoesNotExist:
        error_message = "User with the provided phone number was not found."
        return render(request, 'profile.html', {'message': error_message})

#           {"phone_number":"+79263602259"}    9NG1A4  I2HPSY +79994447773
