from rest_framework.decorators import action
from random import randint
from rest_framework import status, generics, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

import datetime
from django.core.mail import EmailMessage
from .serializers import *
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
# Create your views here.

def responsedata(status, message, data=None):
    if status:
        return {
            "status": status,
            "message": message,
            "data": data
        }
    else:
        return {
            "status": status,
            "message": message,
        }
def send_email(recipient, subject, body, msg_html=None):

    email = EmailMessage(subject=subject,body=body,to=[recipient])
    email.send()
    # message = Mail(
    #     from_email='',
    #     to_emails=recipient,
    #     subject=subject,
    #     html_content=msg_html if msg_html else body)
    # try:
    #     # sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
    #     sg = SendGridAPIClient(
    #         '')
    #     response = sg.send(message)
    #     print(response.status_code)
    #     print(response.body)
    # except Exception as e:
    #     print(str(e))
    #     print(str(e.body))


class UserClass(viewsets.ModelViewSet):
    model_class = User
    serializer_class = UserSerializer
    instance_name = "user"
    queryset = model_class.objects.all()
    token_obtain_pair = TokenObtainPairView.as_view()

    def create(self, request):

        d = request.data
        if not d.get('email'):

            return Response(responsedata(False, "Email is required"), status=status.HTTP_400_BAD_REQUEST)

        if not d.get('username'):

            return Response(responsedata(False, "User Name is required"), status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=request.data.get("email")).values().exists():
            return Response(responsedata(False, "User already present"), status=status.HTTP_409_CONFLICT)
        if request.data.get("mobile"):
            if User.objects.filter(email=request.data.get("mobile")).values().exists():
                return Response(responsedata(False, "An account with this mobile number already exists"),
                                status=status.HTTP_409_CONFLICT)

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            try:
                usr = User.objects.get(id=serializer.data.get('id'))
                usr.profile.user_type = request.data.get('user_type')
                usr.save()
                return Response(responsedata(True, f"{self.instance_name} created sucessfully", serializer.data),
                                status=status.HTTP_200_OK)
            except Exception as e:
                return Response(responsedata(True, f"{self.instance_name} creation error " + str(e)),
                                status=status.HTTP_400_BAD_REQUEST)


        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def authorize(self, request):

        if User.objects.filter(email=request.data.get('email')).exists():
            user = User.objects.get(email=request.data.get('email'))
            if user.check_password(request.data.get('password')):

                if user.is_active and user.is_superuser:
                    user.last_login = datetime.datetime.now()
                    # user.profile.password_changed=
                    user.save()
                    tokenserializer = TokenObtainPairSerializer(
                        data={"username": user.username, "id": str(user.id), "password": request.data.get('password')})
                    if tokenserializer.is_valid(raise_exception=True):
                        d = tokenserializer.validate(
                            {"id": str(user.id), "username": user.username, "password": request.data.get('password')})
                        # print(d)
                    data = dict(user=user.username,
                                id=user.id,
                                email=user.email,
                                user_type=user.profile.user_type,
                                refresh=str(d['refresh']),
                                accessToken=str(d['access']),
                                )

                    return Response(responsedata(True, 'login successfull', data),
                                    headers={"accessToken": str(d['access'])}, status=status.HTTP_200_OK)
                elif user.is_active:
                    # token = RefreshToken.for_user(user)
                    user.last_login = datetime.datetime.now()
                    user.save()
                    tokenserializer = TokenObtainPairSerializer(
                        data={"username": user.username, "id": str(user.id), "password": request.data.get('password')})
                    if tokenserializer.is_valid(raise_exception=True):
                        d = tokenserializer.validate(
                            {"id": str(user.id), "username": user.username, "password": request.data.get('password')})
                    data = dict(user=user.username,
                                id=user.id,
                                email=user.email,
                                user_type=user.profile.user_type,
                                refresh=str(d['refresh']),
                                accessToken=str(d['access']),
                                )

                    return Response(responsedata(True, 'login successfull', data),
                                    headers={"accessToken": str(d['access'])}, status=status.HTTP_200_OK)
                elif not user.is_active:
                    return Response(responsedata(True, 'Your account is temporarily deactivated,'
                                                       ' Please contact administrator'),
                                    status=status.HTTP_403_FORBIDDEN)

                else:

                    return Response(responsedata(True, 'Invalid Login Credentials'),
                                    status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(responsedata(False, "Password is incorrect"), status=status.HTTP_401_UNAUTHORIZED)

        else:

            return Response(responsedata(True, 'Invalid Login Credentials'),
                            status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['post'])
    def request_forgotpassword(self, request):
        """
        API function for requesting forgot password
        """

        # if email not found raise error
        if not request.data.get('email'):
            raise ValidationError({
                "status": False,
                "message": "email is a required field",
                "data": {}
            })

        # get user details
        # if user not valid raise error
        if not User.objects.filter(email=request.data.get('email')):
            raise ValidationError({
                "status":
                    False,
                "message":
                    "{} email does not exist".format(request.data.get('email')),
                "data": {}
            })

        if ForgotPassword.objects.filter(email=request.data.get('email')).values().exists():
            ForgotPassword.objects.filter(email=request.data.get('email')).delete()

        # create a model serializer
        otp_code = str(1234)
        request.data.update({'code': otp_code})
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                msg = 'Your Email verification OTP is ' + otp_code
                send_email(request.data.get("email"), "Code for Email Setup", msg)
                serializer.save()
                return Response(responsedata(True, "Mail sent successfully"), status=status.HTTP_200_OK)
            except Exception as e:
                return Response(responsedata(False, "Cant send mail"), status=status.HTTP_400_BAD_REQUEST)
        else:

            return Response(responsedata(False, serializer.errors), status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk):
        data = request.data
        user = User.objects.get(id=pk)
        if data.get('user_type'):
            user.profile.user_type = data.get('user_type')
            user.save()

        ser = self.serializer_class(user, data=data, partial=True)
        if ser.is_valid(raise_exception=True):
            ser.save()
            return Response(ser.data,status=status.HTTP_200_OK)
        else:
            return Response(ser.errors,status=status.HTTP_400_BAD_REQUEST)




    @action(detail=False, methods=['post'])
    def resendotp(self, request):
        """
        API function for resend otp according at validation
        """

        if request.data.get("validation_type") == "forgot password":
            validation_obj = ForgotPassword.objects.get(email=request.data.get("email"))
            # user_obj = User.objects.get(email=request.data.get("email"))

            try:
                otp_code = str(1234)
                msg = 'Your Email verification OTP is ' + otp_code
                send_email(request.data.get("email"), "Code for Email Setup", msg)

                validation_obj.code = otp_code
                validation_obj.save()
                return Response(responsedata(True, "Mail Sent successfully"), status=status.HTTP_200_OK)

            except Exception as e:

                return Response(responsedata(False, "Cant send mail"), status=status.HTTP_400_BAD_REQUEST)


class ValidateOtp(APIView):


    def post(self, request):
        if request.data.get("validation_type") == "forgot password":
            if not ForgotPassword.objects.filter(email=request.data.get("email"), is_used=True).values().exists():
                if not int(ForgotPassword.objects.get(email=request.data.get("email")).code) == int(
                        request.data.get("code")):
                    return Response(responsedata(False, "Invalid code"), status=status.HTTP_403_FORBIDDEN)

                otp_code = randint(100000, 999999)

                obj = ForgotPassword.objects.get(email=request.data.get("email"))
                obj.change_code = otp_code
                obj.save()
                d_dict = {"change_code": otp_code, 'email': request.data.get("email")}
                return Response(responsedata(True, "Valid code", d_dict), status=status.HTTP_200_OK)
            else:
                return Response(responsedata(False, "password already changed, Please login"),
                                status=status.HTTP_406_NOT_ACCEPTABLE)

class ForgotPasswordChange(APIView):
    """
    API View for performing password change
    based on forgot password request
    """


    def patch(self, request):
        if ForgotPassword.objects.filter(email=request.data.get("email"), is_used=False).values().exists():

            if not ForgotPassword.objects.get(email=request.data.get("email")).change_code == int(
                    request.data.get("code")):
                return Response(responsedata(False, "You are not authorized to change password"),
                                status=status.HTTP_401_UNAUTHORIZED)

            request.data['is_used'] = True
            request.data['code'] = request.data.get("code")

            # reset token
            reset_token = ForgotPassword.objects.get(email=request.data.get("email"))
            reset_token.is_used = True
            reset_token.save()

            # replace password from the user
            password = request.data.get('password')
            try:
                obj = User.objects.get(email=request.data['email'])
                obj.set_password(password)
                obj.save()

                return Response(responsedata(True, "Password Changed successfully", UserSerializer(obj).data),
                                status=status.HTTP_200_OK)
            except Exception as e:
                return Response(responsedata(False, "Something went wrong " + str(e))
                                , status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(responsedata(False, "password already changed, Please login"),
                            status=status.HTTP_406_NOT_ACCEPTABLE)


class Logout(APIView):
    def post(self, request):

        try:
            Refresh_token = request.data["refresh"]
            token = RefreshToken(Refresh_token)
            token.blacklist()
            access_token = request.META.get('HTTP_AUTHORIZATION').split(' ')[1]

            b = BlacklistedAccessTokens()
            b.token = access_token
            b.save()
            return Response("Successful Logout", status=status.HTTP_200_OK)
        except:
            return Response("Successful Logout", status=status.HTTP_200_OK)


class CategoryAPI(generics.ListCreateAPIView):
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer

class CategoryDetailsAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer

class ProductsAPI(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductsDetailsAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class TagsAPI(viewsets.ModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer