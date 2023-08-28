import random
import string
import time

from django.shortcuts import render
from rest_framework.decorators import api_view

from referrals.models import UserProfile


@api_view(['GET'])
def entry_authorization_page(request):
    """стартовая страница авторизации"""
    return render(request, 'login_step1.html')


@api_view(['GET'])
def entry_get_profile(request):
    """стартовая страница профиля"""
    return render(request, 'profile.html')


@api_view(['POST'])
def authenticate_user(request):
    """получаем номер телефона и инвайт из формы"""
    phone_number = request.data.get('phone_number')
    invite_code = request.data.get('invite_code')
    """передаем номер телефона и инвайт в request.session"""
    request.session['phone_number'] = phone_number
    request.session['invite_code'] = invite_code
    request.session.save()
    return render(request, 'login_step2.html')


@api_view(['POST'])
def verify_activation_code(request):
    activation_code = request.data.get('authorization_code')
    """получаем номер телефона и инвайт из текущей сессии"""
    phone_number = request.session.get('phone_number')
    invite_code = request.session.get('invite_code')

    if activation_code:
        time.sleep(2)
        '''
        если пользователь с указанным номером сущесвует,
        возвращается кортеж с user, create = False
        если не существует, то user создается, created = True
        '''
        user, created = UserProfile.objects.get_or_create(phone_number=phone_number)

        invite_code_exist = UserProfile.objects.filter(invite_code=invite_code).exists()
        if created:
            if invite_code:
                if invite_code_exist:
                    '''
                    если введенный код принадлежит другому user:
                    сохранить инвайт-код новому user
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
                    """
                    после удачного создания пользователя
                    вернуть профиль
                    """
                    return render(request, 'profile.html', context)
                else:
                    return render(request, 'error_message.html',
                                  {'message': f'Invalid invite_code: {invite_code}'})
            else:
                '''
                если инвайт-код не вводился:
                сгенерировать и присвоить user
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
            """
            Если пользователь с указанным номером существует:
            вернуть профиль 
            """
            context = {
                'message': 'authorized',
                'phone_number': user.phone_number,
                'invite_code': user.invite_code,
                'used_foreign_invite': user.used_foreign_invite,
            }
            return render(request, 'profile.html', context)
    else:
        """если код """
        return render(request, 'error_message.html',
                      {'message': f'Invalid activation_code: {activation_code}'})


@api_view(['POST'])
def get_user_profile(request):
    """
    Получение профиля пользователя по указанному номеру телефона.
    :param request: содержит номер телефона пользователья
    :return: профиль пользователя по указанному номеру телефона
    """
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
