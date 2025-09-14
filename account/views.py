from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .serializers import PhoneSerializer, OTPSerializer, UserTokenObtainPairSerializer
from django.contrib.auth import authenticate
from .utils import is_phone_number_valid, send_sms, is_valid_otp
from django.contrib.auth import get_user_model
from .models import OTP, OTPBlackList
import random
import string

User = get_user_model()



def generate_otp_code(length=6):
    
    found_unique_otp = False
    otp_code = ""
    while not found_unique_otp:
        code = "".join(random.choices(string.digits, k=length))
        check_for_black_listed = OTPBlackList.objects.filter(otp_code=code, black_listed=True)
        if not check_for_black_listed.exists():
            otp_code = code
            break
    
    return otp_code



class SendOTPView(APIView):
    serializer_class = PhoneSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            phone_number = serializer.validated_data.get('phone_number')

            # phone number regex check for iran's number            
            if is_phone_number_valid(phone_number):
                user = User.objects.filter(phone_number=phone_number)
                
                if user.exists():
                    user = user.first()

                    # check that another code hasn't been sent to user
                    check_for_active_otp_code = OTP.objects.filter(user=user, expired=False)
                    
                    if check_for_active_otp_code.exists():
                        otp_obj = check_for_active_otp_code.last()
                        
                        if not otp_obj.is_valid():

                            # generate code that hasn't been sent to another user
                            otp_code = generate_otp_code(length=6)
                            
                            print(otp_code)
                            # create OTP object
                            OTP_obj = OTP(
                                user=user,
                                code=otp_code,
                                expired=False
                            )

                            OTP_obj.save()

                            # send it to black list
                            black_list_obj = OTPBlackList(otp_code=otp_code, black_listed=True)
                            black_list_obj.save()

                            # send the code and handle the verfication in VerifyOTP
                            
                            sms_status = send_sms(phone_number, otp_code)
                            if not sms_status:
                                return Response({'msg': 'مشکلی به وجود آمده لطفا دوباره امتحان کنید'},  status=status.HTTP_204_NO_CONTENT)


                            return Response({"msg": "کد برای شما ارسال شد"}, status=status.HTTP_200_OK)
                        else:

                            return Response({"msg": 'کد برای شما ارسال شده است'}, status=status.HTTP_204_NO_CONTENT)

                    else:
                            otp_code = generate_otp_code(length=6)
                            
                            print(otp_code)
                            # create OTP object
                            OTP_obj = OTP(
                                user=user,
                                code=otp_code,
                                expired=False
                            )

                            OTP_obj.save()

                            # send it to black list
                            black_list_obj = OTPBlackList(otp_code=otp_code, black_listed=True)
                            black_list_obj.save()

                            # send the code and handle the verfication in VerifyOTP
                            
                            sms_status = send_sms(phone_number, otp_code)
                            if not sms_status:
                                return Response({'msg': 'مشکلی به وجود آمده لطفا دوباره امتحان کنید'},  status=status.HTTP_204_NO_CONTENT)


                            return Response({"msg": "کد برای شما ارسال شد"}, status=status.HTTP_200_OK)

                
                else:
                    return Response(status=status.HTTP_404_NOT_FOUND)

            else:
                return Response({"msg": "شماره را درست وارد کنید"}, status=status.HTTP_400_BAD_REQUEST)

        
        return Response(status=status.HTTP_400_BAD_REQUEST)

        


class VerifyOTPView(APIView):
    def post(self, request, format=None):
        serializer = OTPSerializer(data=request.data)

        if serializer.is_valid():
            phone_number = serializer.validated_data.get("phone_number")
            otp_code = serializer.validated_data.get("otp_code")

            phone_number_check = is_phone_number_valid(phone_number)
            otp_check = is_valid_otp(otp_code)

            if otp_check and phone_number_check:
                otp_obj = OTP.objects.filter(code=otp_code, expired=False)
                if otp_obj.exists():
                    otp_obj = otp_obj.last()
                    
                    if otp_obj.is_valid():

                        if otp_obj.user.phone_number == phone_number:
                            user = otp_obj.user
                            token_serializer = UserTokenObtainPairSerializer()
                            token = token_serializer.get_token(user)

                            # expire the whole object for the user
                            otp_obj.expired = True
                            otp_obj.save()

                            # set the generated code free for further usage
                            blacklist = OTPBlackList.objects.get(otp_code=otp_code, black_listed=True)
                            blacklist.black_listed = False
                            blacklist.save()


                            if user.is_active:
                                authenticate(phone_number=phone_number)
                                
                                return Response({
                                    'refresh': str(token),
                                    'access': str(token.access_token),
                                }, status=status.HTTP_200_OK)
                            
                            return Response({'msg': 'user is not active'}, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
                            

                        else:
                            return Response(status=status.HTTP_401_UNAUTHORIZED)

                    else:
                        # expire the whole object for the user
                        otp_obj.expired = True
                        otp_obj.save()

                        # set the generated code free for further usage
                        blacklist = OTPBlackList.objects.get(otp_code=otp_code, black_listed=True)
                        blacklist.black_listed = False
                        blacklist.save()

                        return Response({'msg': 'کد منقضی شده است'}, status=status.HTTP_204_NO_CONTENT)
                
                else:
                    return Response({'msg': "کد وارده شده اشتباه است"}, status=status.HTTP_404_NOT_FOUND)
            
            else:
                return Response({'msg': "کد یا شماره تلفن اشتباه وارد شده است"}, status=status.HTTP_400_BAD_REQUEST)
                
        
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


















