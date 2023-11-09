from oauth2_provider.models import AccessToken
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import logout
from rest_framework import status
from oauth2_provider.decorators import protected_resource
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

@api_view(('GET',))
@protected_resource(scopes=['read'])
def hello_endpoint(request, *args, **kwargs):
        authorization_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not authorization_header.lower().startswith("bearer "):
          return Response(
            {"detail": "Invalid or missing Bearer token in Authorization header", "code": 0},
            status=status.HTTP_401_UNAUTHORIZED
        )
        access_token = authorization_header.split(" ")[1]
        print(f"token : {access_token}")
        try:
           temp = AccessToken.objects.get(token=str(access_token))
           user = User.objects.get(username=temp.user)
           return Response(
            {"username": f'{str(user.username)}', "email" : f'{str(user.email)}', "code": 1},
            status=status.HTTP_200_OK
          )
        except AccessToken.DoesNotExist:
          return Response(
            {"detail": "Access token not found or is invalid", "code": 2},
            status=status.HTTP_401_UNAUTHORIZED
        )


@csrf_exempt
@api_view(('POST',))
def oauth_logout(request):
    authorization_header = request.META.get("HTTP_AUTHORIZATION", "")
    if not authorization_header.lower().startswith("bearer "):
          return Response(
            {"detail": "Invalid or missing Bearer token in Authorization header", "code": 0},
            status=status.HTTP_401_UNAUTHORIZED
        )
    access_token = authorization_header.split(" ")[1]
    print(f"token : {access_token}")
    try:
     token_object = AccessToken.objects.get(token=str(access_token))
    except AccessToken.DoesNotExist:
           print("error token dosent exist ")
   
    user = token_object.user
    access_token = AccessToken.objects.filter(user=user)
    
    if access_token:
        for token in access_token:
            token.revoke()
    logout(request)

    return Response({'message': 'Logged out successfully'}, status=200)

