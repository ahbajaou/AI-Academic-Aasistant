from rest_framework import status, response, decorators
from .serialz import auth_db_serial, tokens_db_serial, verify_serializer
from .models import auth_db, tokens_db, verificationSystem, userFields
from django.core import mail
from django.conf import settings
from .isStrong import validate_passwd
import bcrypt, string, random
from django.views.decorators.csrf import csrf_exempt
# from ai.models import conversations
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import api_view
from rest_framework.response import Response

def is_auth_user(access_token, refresh_token=""):
    try:
        user_data = tokens_db.objects.get(access_token=access_token)
        return user_data
    except:
        raise Exception("")

def generate_tokens(email):
    access_token = ''.join(random.choices
                           (string.digits + string.ascii_uppercase + string.ascii_lowercase, k=100))
    return {'identity': email, 'access_token': access_token}

@swagger_auto_schema(
    method='post',
    operation_description="User Sign Up",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password')
        },
        required=['username', 'password']
    ),
    responses={
        200: openapi.Response(
            description="User signed up successfully",
            examples={
                "application/json": {
                    "message": "User signed up successfully"
                }
            }
        )
    }
)
@decorators.api_view(["POST"])
def signup(req):
    serial = auth_db_serial(data=req.data)
    if serial.is_valid():
        # Check if user already exists
        try:
            existing_user = auth_db.objects.get(email=serial.validated_data['email'])
            return response.Response({'email': 'User with this email already exists'},
                                   status=status.HTTP_400_BAD_REQUEST)
        except auth_db.DoesNotExist:
            pass

        password_status = validate_passwd(serial.validated_data['password'])
        if (password_status != 'Strong'):
            return response.Response({'Weak Password': password_status},
                                   status=status.HTTP_400_BAD_REQUEST)
        
        hash_pass = bcrypt.hashpw(serial.validated_data['password'].encode('ASCII'),
                                 bcrypt.gensalt())
        serial.validated_data['password'] = hash_pass.decode('ASCII')
        tokens = generate_tokens(serial.validated_data['email'])
        tokens_serial = tokens_db_serial(data=tokens)
        if tokens_serial.is_valid():
            tokens_serial.save()
        
        try:
            # Delete any existing verification records for this email
            verificationSystem.objects.filter(identity=serial.validated_data['email']).delete()
            
            code = ''.join(random.choices(string.digits + string.ascii_letters, k=8))
            verification_serial = verify_serializer(data={
                'identity': serial.validated_data['email'],
                'ActivationCode': code
            })
            if verification_serial.is_valid():
                verification_serial.save()
            else:
                return response.Response(verification_serial.errors,
                                     status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            mail.send_mail(
                'Uorianted - ACTIVATION', 
                f"Hello {serial.validated_data['email']}\nYour Activation Code is: {code}\nBest Regards,\nUorianted team.",
                settings.EMAIL_HOST_USER, 
                [serial.validated_data['email']]
            )
        except Exception as e:
            print(f"RED: Failed Cause: {e}")
            return response.Response({'Verification': 'Failed to send the verification mail'},
                                   status=status.HTTP_504_GATEWAY_TIMEOUT)
        
        serial.save()
        return response.Response(status=status.HTTP_201_CREATED)
    return response.Response(serial.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    operation_description="Account Verification",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email address'),
            'verification_code': openapi.Schema(type=openapi.TYPE_STRING, description='Verification code')
        },
        required=['email', 'verification_code']
    ),
    responses={
        200: openapi.Response(
            description="Account verified successfully",
            examples={
                "application/json": {
                    "message": "Account verified successfully"
                }
            }
        ),
        400: openapi.Response(
            description="Bad Request",
            examples={
                "application/json": {
                    "Activation Failed": "Invalid Information",
                    "email": "This Field Required",
                    "verification_code": "This Field Required"
                }
            }
        )
    }
)
@decorators.api_view(["POST"])
def verify(req):
    try:
        # Validate required fields
        email = req.data.get('email')
        code = req.data.get('verification_code')

        if not email or not code:
            return response.Response({
                'Activation Failed': 'Invalid Information',
                'email': 'This Field Required' if not email else '',
                'verification_code': 'This Field Required' if not code else ''
            }, status=status.HTTP_400_BAD_REQUEST)

        # Fetch user from verification system
        user = verificationSystem.objects.get(identity=email)

        # Check if the verification code matches
        if user.ActivationCode == code:
            activateUser = auth_db.objects.get(email=user.identity)
            activateUser.activation = True
            activateUser.save()
            user.delete()
            return response.Response({
                'Activation': 'Successful Activation',
                'Email': activateUser.email
            }, status=status.HTTP_200_OK)
        else:
            return response.Response({'verification_code': 'Invalid Code'},
                                     status=status.HTTP_400_BAD_REQUEST)
    except verificationSystem.DoesNotExist:
        return response.Response({'Activation Failed': 'Invalid Information'},
                                 status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return response.Response({'Error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(
    method='post',
    operation_description="User Sign In",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password')
        },
        required=['username', 'password']
    ),
    responses={
        200: openapi.Response(
            description="User signed in successfully",
            examples={
                "application/json": {
                    "message": "User signed in successfully",
                    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                }
            }
        )
    }
)
@decorators.api_view(["POST"])
def signin(req):
    try:
        email, password = req.data.get('email'), req.data.get('password').encode('ASCII')
        user = auth_db.objects.get(email=email)
        if user.activation == False:
            return response.Response({'email': 'Email Activation Required'},
                                     status=status.HTTP_401_UNAUTHORIZED)
        if bcrypt.checkpw(password, user.password.encode('ASCII')):
            user_tokens = tokens_db.objects.get(identity=email)
            isAvailable = False
            try:
                userFields.objects.get(identity=email)
                isAvailable = True
            except:
                pass
            return response.Response(
                {
                    'active_user': user.activation,
                    'Access-Token': user_tokens.access_token,
                    'isSelectFields': isAvailable
                }, status=status.HTTP_200_OK)
    except:
        pass
    return response.Response({'Error': 'Invalid Informations'}, status=status.HTTP_404_NOT_FOUND)

# @decorators.api_view(['GET'])
# def profile_data(req):
#     try:
#         user_data = is_auth_user(req.headers.get('Access-Token'), req.headers.get('Refresh-Token'))
#     except Exception as error:
#         return response.Response({'Authentication': 'Permission Needed'},
#                                  status=status.HTTP_404_NOT_FOUND)
#     infos = auth_db.objects.get(email=user_data.identity)
#     return response.Response({'Email': infos.email,'Activation': infos.activation},
#                              status=status.HTTP_200_OK)

# @decorators.api_view(['POST'])
# def storeUserFileds(req):
#     try:
#         user_data = is_auth_user(req.headers.get('Access-Token'), req.headers.get('Refresh-Token'))
#     except Exception as error:
#         return response.Response({'Authentication': 'Permission Needed'},
#                                  status=status.HTTP_404_NOT_FOUND)
#     data = req.data.get('fields')
#     if data is None or len(data) == 0:
#         return response.Response({'fields': 'Required Field', 'Empty fields': 'This field cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)
#     try:
#         getUserFields = userFields.objects.create(identity=user_data.identity)
#     except:
#         getUserFields = userFields.objects.get(identity=user_data.identity)
#     allowedFields = ['football', 'ai', 'crypto', 'it', 'politic', 'cybersec']
#     fields = {}
#     for field in data:
#         if field in allowedFields:
#             fields[field] = True
#         else:
#             return response.Response({'allowed fields': allowedFields}, status=status.HTTP_400_BAD_REQUEST)
#     print(fields)
#     try:
#         getUserFields.fields = fields
#         getUserFields.save()
#     except Exception as e:
#         print("Eroor: ", e)
#         return response.Response({'Sorry': 'Something Wierd Happen'}, status=status.HTTP_504_GATEWAY_TIMEOUT)
#     return response.Response({'fields': 'added succeful'}, status=status.HTTP_200_OK)

# @decorators.api_view(['GET'])
# def getUserFields(req):
#     try:
#         user_data = is_auth_user(req.headers.get('Access-Token'), req.headers.get('Refresh-Token'))
#     except Exception as error:
#         return response.Response({'Authentication': 'Permission Needed'},
#                                  status=status.HTTP_404_NOT_FOUND)
#     try:
#         theFields = userFields.objects.get(identity=user_data.identity)
#         print("Your Fileds", theFields.fields)
#         return response.Response(theFields.fields, status=status.HTTP_200_OK)
#     except:
#         return response.Response({'fields': 'Fields Not Found'}, status=status.HTTP_400_BAD_REQUEST)