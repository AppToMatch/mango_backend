from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from rest_framework.views import APIView,status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from app.models import *
from app.serializers import *
from .serializers import *
from django.contrib.auth.models import AnonymousUser, User
from rest_framework import generics,viewsets,status
from rest_framework.pagination import PageNumberPagination,LimitOffsetPagination
from django.contrib.auth import login, authenticate,logout
from .permissions import Check_API_KEY_Auth
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from paystackapi.paystack import Paystack
from paystackapi.transaction import Transaction
from paystackapi.verification import Verification
from app.email_sender import sendmail
paystack_secret_key = "sk_test_e6c40e9e83237dbb32096831467c6e6193a970cb"
paystack = Paystack(secret_key=paystack_secret_key)




def getuser(request,):
    try:
        user = User.objects.get(pk=request.user.pk)
    except Exception:
        user = []
    return user


def getpartner(request):
    try:
        partner = Partner.objects.get(admin=getuser(request))
        return partner
    except Exception:
        return []

def getsender(request,**filters):
    try:
        sender = Sender.objects.get(user=User.objects.get(pk = int(request.user.pk)),**filters)
    except Exception:
        sender = []
    return sender

def getprofile(request,**filters):
    try:
        profile = Profile.objects.get(user=User.objects.get(pk = int(request.user.pk)),**filters)
    except Exception:
        profile = []
    return profile


def accepttc(request):
    profile = getprofile(request)
    if profile:
        profile.tc_accepted = True
        profile.save()
        return {'status':'success',}
    else:
        return {'status':'No profile',}



def getkeys(obj):
    try:
        obj = dict(obj[0])
        return list(obj.keys())
    except Exception:
        return []


def getfilters(request,*args,**kwargs):
    if request.method == 'POST':
        generalfilters = dict(request.POST)
    else:
        generalfilters = dict(request.GET)
    exclude_contain_words = []
    filters = {}
    try:
        model_fields = kwargs['model_fields']
    except KeyError:
        model_fields = []
    try:
        exclude_list = kwargs['exclude']
    except KeyError:
        exclude_list = []

    try:
        contain_words_list = kwargs['contain_words']
    except KeyError:
        contain_words_list =[]
    for filter in generalfilters:
        if filter =='format':
            exclude_contain_words.append(filter)
        elif filter in exclude_list:
            exclude_contain_words.append(filter)
        elif not generalfilters[filter][0]:
            exclude_contain_words.append(filter)
        elif filter not in model_fields:
            for word in model_fields:
                    if filter.find(word) != -1:                
                        exclude_contain_words.append(filter)
        else:
            for word in contain_words_list:
                if (word and filter not in exclude_contain_words):
                    if filter.find(word) != -1:                
                        exclude_contain_words.append(filter)
        if filter in exclude_contain_words:
            pass
        else:
            # exist = (filter in args) or (filter in kwargs['model_fields'])
            filter = str(filter)
            filters[filter] = generalfilters[filter][0]
    return filters

class checkapipermission(APIView,):
    permission_classes = (Check_API_KEY_Auth,)
    def get(self, request, format=None):
        content = {
        'status': 'request was permitted'
        }
        return Response(content)

class UserList(viewsets.ModelViewSet,):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserListPaginated(viewsets.ModelViewSet,PageNumberPagination):
    pagination_class = LimitOffsetPagination
    page_size = 10
    page_size_query_param = 'page_size'
    queryset = User.objects.all()
    serializer_class = UserSerializer



class tokenAuth(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request, format=None):
        return Response({'detail': "I suppose you are authenticated"})


class LoginView(APIView):
    permission_classes = ()
    serializer_class = UserSerializer
    def get(self,request):
        return Response(status=status.HTTP_202_ACCEPTED)

    def post(self, request,):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request,email=email, password=password)
        try:
            user = User.objects.get(email=email)
            if check_password(password,user.password):
                login(request,user)
                serialized_data = UserSerializer(user)
                return Response(serialized_data.data,status=status.HTTP_202_ACCEPTED)
            else:
                return Response({"error": "Wrong credentials"}, status=status.HTTP_400_BAD_REQUEST)

        except ObjectDoesNotExist:

            return Response({"error": "User does not exist"}, status=status.HTTP_400_BAD_REQUEST)


class RequestChangePasswordView(APIView):

    queryset = Security.objects.all()
    serializer_class = SecuritySerializer
    authentication_classes = ()
    permission_classes = ()

    def get(self,request):
        email =request.GET.get('email')
        try:
            user= User.objects.get(email=email)
            try:
                security = Security.objects.get(user=user)
                security_serializer_class = SecuritySerializer(security)
                db_token = str(round(9999999 * random()))[0:6]
                print(db_token)
                security.last_token= make_password(db_token)
                security.save()
                data = {'status':'success'}
                
            except ObjectDoesNotExist:
                security = Security.objects.create(user=user)
                security.refresh_from_db()
                db_token = str(round(9999999 * random()))[0:6]
                print(db_token)
                security.last_token= make_password(db_token)
                security.save()
                security_serializer_class = SecuritySerializer(security)
                data = {'status':'success'}
            # message = '<p><b>Use ' + db_token + ' as your verification code</b></p>'
            # subject = 'Password Change Request'
            # sendmail([user.email],message,message,subject)
            return Response(data,status=status.HTTP_202_ACCEPTED)
        except ObjectDoesNotExist:
            return Response({'user':False},status=status.HTTP_404_NOT_FOUND)


    def post(self, request):
        verification_code = request.data.get('last_token')
        email = request.GET.get('email')
        # '154914'
        try:
            user= User.objects.get(email=email)
            try:
                security = Security.objects.get(user=user)
                if check_password(verification_code,security.last_token):
                    user.set_password(request.data.get('secret_answer'))
                    user.save()
                    data = {'success':True}
                else:
                    data= {'invalid_verification_code':True}
                return Response(data,status=status.HTTP_202_ACCEPTED)

            except ObjectDoesNotExist:
                return Response({'invalid_request':True},status=status.HTTP_404_NOT_FOUND)


        except ObjectDoesNotExist:
            return Response({'user':False},status=status.HTTP_404_NOT_FOUND)


class CheckAccountNumber(APIView):

    def post(self,request):
        account_number = request.POST.copy().get('account_number')
        account_bank = request.POST.copy().get('account_bank')
        verification_response = Verification.verify_account(account_number=account_number,bank_code=account_bank)
        sender = getsender(request)

        if verification_response['status']:
            if sender.is_admin:
                partner = getpartner(request)
                if verification_response['data']['account_name'] == partner.name:
                    account_accepted= True

                else:
                    name_count =0
                    for name in str(sender.first_name + ' ' + sender.last_name).split(' '):
                        if name in str(verification_response['data']['account_name']).split(' '):
                            account_accepted = True
                            name_count += 1
                    if name_count > 1:
                        account_accepted = True
                    else:
                        account_accepted = False
                        reason = 'Account name does not match business or your name'
            else:
                name_count =0
                for name in str(sender.first_name + ' ' + sender.last_name).split(' '):
                    if name in str(verification_response['data']['account_name']).split(' '):
                        account_accepted = True
                        name_count += 1
                if name_count > 1:
                    account_accepted = True
                else:
                    account_accepted = False
                    reason = 'Account name does not match your name'   
            data = {
            'full_name':verification_response['data']['account_name'],'account_accepted':account_accepted,'reason':reason,
                            }
            return Response(data,status=status.HTTP_200_OK)
        else:
            data = {
            'error':'Wrong account details',
                            }
            return Response(data,status=status.HTTP_404_NOT_FOUND)



class AddHelp(APIView):

    queryset = Help.objects.all()
    serializer_class = HelpSerializer

    def get(self,request):
        user = getuser(request)
        helps = Help.objects.filter(user=user)
        serializer_class = HelpSerializer(helps,many=True)
        data = {'status':'success','helps':serializer_class.data,}
        return Response(data,status=status.HTTP_202_ACCEPTED)


    def post(self,request):
        user = getuser(request)
        serializer_class = HelpSerializer(data=request.data)
        if serializer_class.is_valid():
            serializer_class.save()
            help_request = serializer_class.instance
            help_request.user = user
            help_request.save()
            # profile.help= help
            # profile.save()
            help_serializer_class = HelpSerializer(help_request)
            data = {'status':'success','help':help_serializer_class.data}
        else:
            data = {'status':'failed',}
            
        return Response(data,status=status.HTTP_202_ACCEPTED)



    def put(self,request):
        user = getuser(request)
        help_request = Help.objects.get(id=request.GET.get('id'))
        serializer_class = HelpSerializer(instance =help_request, data=request.data)
        if serializer_class.is_valid():
            serializer_class.save()
            # help = serializer_class.instance
            # help.save()
            # profile.help= help
            # profile.save()
            help_serializer_class = HelpSerializer(help_request)
            data = {'status':'success','help':help_serializer_class.data}
        else:
            data = {'status':'failed',}
            
        return Response(data,status=status.HTTP_202_ACCEPTED)

class ProfileView(APIView):

    queryset = Profile.objects.all()
    serializer_class = ProfilesSerializer

    def get(self,request):
        user = getuser(request)
        try:
            profile = Profile.objects.get(user=user)
            profile_serializer_class = ProfilesSerializer(profile)
            data = {'status':'success','profile':profile_serializer_class.data}
        except ObjectDoesNotExist:
            data = {'profile':''}
        return Response(data,status=status.HTTP_202_ACCEPTED)


    def post(self,request):
        user = getuser(request)
        try:
            profile = Profile.objects.get(user=user)
            serializer_class = ProfilesSerializer(profile,instance=profile,data=request.data)
        except ObjectDoesNotExist:
            serializer_class = ProfilesSerializer(data=request.data)
        if serializer_class.is_valid():
            serializer_class.save()
            profile = serializer_class.instance
            profile.user= getuser(request)
            profile.save()
            profile_serializer_class = ProfilesSerializer(profile)
            data = {'status':'success','profile':profile_serializer_class.data}
        else:

            data = {'status':'failed','description':'Invalid data',}
            
        return Response(data,status=status.HTTP_202_ACCEPTED)


class VerifyPhone(APIView):

    queryset = Security.objects.all()
    serializer_class = SecuritySerializer
    authentication_classes = ()
    permission_classes = ()

    def get(self,request):
        phone_number =request.GET.get('phone_number')
        try:
            security = Security.objects.get(phone_number=phone_number)
            security_serializer_class = SecuritySerializer(security)
            db_token = str(round(9999999 * random()))[0:6]
            print(db_token)
            security.last_token= make_password(db_token)
            security.save()
            data = {'status':'success','security':security_serializer_class.data}
            
        except ObjectDoesNotExist:
            security = Security.objects.create(phone_number=phone_number)
            security.refresh_from_db()
            db_token = str(round(9999999 * random()))[0:6]
            print(db_token)
            security.last_token= make_password(db_token)
            security.save()
            security_serializer_class = SecuritySerializer(security)
            data = {'status':'success','security':security_serializer_class.data}
            
        return Response(data,status=status.HTTP_202_ACCEPTED)


    def post(self,request):
        try:
            security = Security.objects.get(phone_number=request.data['phone_number'])
            digits = request.data['last_token']
            if check_password(digits, security.last_token):
                security.last_token = ''
                security.save()
                print('Password matched')
            else:
                print('Worng password')
            data = {'status':'success',}

        except ObjectDoesNotExist:

            data = {'status':'failed','description':'Invalid data',}
            
        return Response(data,status=status.HTTP_202_ACCEPTED)



class UserView(APIView):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = ()
    permission_classes = ()
    def get(self,request):
        user = getuser(request)
        try:
            user = UserSerializer(user)
            data = {'status':'success','user':user.data}
        except ObjectDoesNotExist:
            data = {'user':''}
        return Response(data,status=status.HTTP_202_ACCEPTED)


    def post(self,request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            serialized_data = UserSerializer(user)
            login(request,user)
        return Response(serialized_data.data,status=status.HTTP_202_ACCEPTED)


# class CreateUser(APIView):

#     queryset = User.objects.all()
#     serializer_class = UsersSerializer
#     authentication_classes = ()
#     permission_classes = ()


#     def get(self,request):
#         user = getuser(request)
#         try:
#             user = UsersSerializer(user)
#             data = {'status':'success','user':user.data}
#         except ObjectDoesNotExist:
#             data = {'user':''}
#         return Response(data,status=status.HTTP_202_ACCEPTED)


#     def post(self,request):
#         first_name = request.data['first_name']
#         last_name = request.data['last_name']
#         phone_number =request.GET.get('phone_number')
#         try:
#             security = Security.objects.get(phone_number=phone_number)
#             user = User.objects.create(first_name=first_name,last_name=last_name)
#             try:
#                 profile = Profile.objects.get(user=user)
#             except ObjectDoesNotExist:
#                 profile = Profile.objects.create(user=user)
#             try:
#                 wallet = Wallet.objects.get(user=user)
#             except ObjectDoesNotExist:
#                 wallet = Wallet.objects.create(user=user)
#             profile.security = security
#             profile.wallet=wallet
#             profile.save()
#             user_serializer_class = UsersSerializer(user)
#             login(request, user)
#             data = {'status':'success','user':user_serializer_class.data}
#         except ObjectDoesNotExist:
#             data = {'status':'failed','description':'Verify phone number',}
            
#         return Response(data,status=status.HTTP_202_ACCEPTED)




class SecurityView(APIView):
    queryset = Security.objects.all()
    serializer_class = SecuritySerializer

    def get(self,request):
        user = getuser(request)
        try:
            security = Security.objects.get(user=user)
        except ObjectDoesNotExist:
            security = Security.objects.create(user=user)
        serializer_class = SecuritySerializer(security)
        return Response(serializer_class.data)


    def post(self,request):
        user = getuser(request)
        try:
            security = Security.objects.get(user=user)
            serializer_class = SecuritySerializer(instance=security, data=request.data)
        except ObjectDoesNotExist:
            serializer_class = SecuritySerializer(data=request.data)
        if serializer_class.is_valid():
            serializer_class.save()
            security = serializer_class.instance
        serializer_class = SecuritySerializer(security)
        data = {'status':'success','security':serializer_class.data}
        return Response(data,status=status.HTTP_202_ACCEPTED)


class UserTwoFactorEnableView(APIView):
    queryset = User.objects.all()
    serializer_class = UserTwoFactorSerializer

    def get(self,request):
        user = getuser(request)
        try:
            security = Security.objects.get(user=user)
        except ObjectDoesNotExist:
            security = Security.objects.create(user=user)
        serializer_class = SecuritySerializer(security)
        return Response(serializer_class.data)


    def post(self,request):
        user = getuser(request)
        try:
            security = Security.objects.get(user=user)
        except ObjectDoesNotExist:
            security = Security.objects.create(user=user)
        user.set_password(request.data['password'])
        user.save()
        security.two_factor_auth_enabled = True
        security.save()
        login(request,user)
        serializer_class = SecuritySerializer(security)
        data = {'status':'success','security':serializer_class.data}
        return Response(data,status=status.HTTP_202_ACCEPTED)

class UserTwoFactorDisableView(APIView):
    queryset = User.objects.all()
    serializer_class = UserTwoFactorSerializer


    def get(self,request):
        user = getuser(request)
        try:
            security = Security.objects.get(user=user)
        except ObjectDoesNotExist:
            security = Security.objects.create(user=user)
        serializer_class = SecuritySerializer(security)
        return Response(serializer_class.data)


    def post(self,request):
        user = getuser(request)
        try:
            security = Security.objects.get(user=user)
        except ObjectDoesNotExist:
            security = Security.objects.create(user=user)
        if check_password(request.data['password'], user.password):
            user.password=''
            user.save()
            security.two_factor_auth_enabled = False
            security.save()
            serializer_class = SecuritySerializer(security)
            login(request,user)

            data = {'status':'success','security':serializer_class.data}
        else:
            serializer_class = SecuritySerializer(security)
            security.save()
            if security.login_attempt_count == 3:
                logout(request)
            else:
                security.login_attempt_count +=1
                login(request,user)
            data = {'status':'failed','incorrect':True,'security':serializer_class.data}    
        return Response(data,status=status.HTTP_202_ACCEPTED)



class PictureView(APIView):
    queryset = Picture.objects.all()
    serializer_class = PicturesSerializer

    def get(self,request):
        user = getuser(request)
        filters = getfilters(request,exclude=[''],contain_words=['',])
        picture = Picture.objects.filter(user=user,**filters)
        serializer_class = PicturesSerializer(picture,many = True)
        return Response({'pictures':serializer_class.data},status=status.HTTP_202_ACCEPTED)


    def post(self,request):
        user = getuser(request)
        serializer_class = PicturesSerializer(data=request.data)
        if serializer_class.is_valid():
            serializer_class.save()
            picture = serializer_class.instance
            picture.user=user
            try:
                picture.save()
                serializer_class = PicturesSerializer(picture)
                data = {'status':'success','picture':serializer_class.data}   
                res_status= status.HTTP_202_ACCEPTED         
            except Exception:
                picture.delete()
                data = {'status':'failed','err':'duplicate entry'}            
                res_status= status.HTTP_400_BAD_REQUEST
        return Response(data,status = res_status)


    def delete(self,request):
        user = getuser(request)
        filters = getfilters(request,exclude=[''],contain_words=['',])
        try:
            picture = Picture.objects.get(**filters)
            picture.delete()
            data = {'status':'success'}
            res_status=status.HTTP_202_ACCEPTED

        except ObjectDoesNotExist:
            data = {'status':'failed'}
            res_status =status.HTTP_404_NOT_FOUND
        return Response(data,status=resstatus)




class ProfileView(APIView):
    queryset = Profile.objects.all()
    serializer_class = ProfilesSerializer

    def get(self,request):
        user = getuser(request)
        try:
            profile = Profile.objects.get(user=user)
        except ObjectDoesNotExist:
            profile = Profile.objects.create(user=user)
        serializer_class = ProfilesSerializer(profile)
        return Response(serializer_class.data)


    def post(self,request):
        user = getuser(request)
        try:
            profile = Profile.objects.get(user=user)
            serializer_class = ProfilesSerializer(instance=profile, data=request.data)
        except ObjectDoesNotExist:
            serializer_class = ProfilesSerializer(data=request.data)
        if serializer_class.is_valid():
            serializer_class.save()
            profile = serializer_class.instance
        serializer_class = ProfilesSerializer(profile)
        data = {'status':'success','profile':serializer_class.data}
        return Response(data,status=status.HTTP_202_ACCEPTED)





class SwipeView(APIView):
    queryset = Profile.objects.all()
    serializer_class = ProfilesSerializer

    def get(self,request):
        user = getuser(request)
        all_mangoes = list(Profile.objects.all())
        current_profile= list(filter(lambda x:x.user == user,all_mangoes))[0]
        mangoes = list(filter(lambda x:x.interested_in == current_profile.interested_in and x.id != current_profile.id ,all_mangoes))
        page = request.GET.get('page')
        paginator = Paginator(mangoes, 1)
        try:
            mangoes = paginator.page(page)
        except PageNotAnInteger:
            mangoes = paginator.page(1)
        except EmptyPage:
            mangoes = paginator.page(paginator.num_pages)
        print(mangoes.object_list)
        serializer_class = ProfilesSerializer(mangoes.object_list,many=True)
        data = {'status':'success',
        'mangoes':serializer_class.data,
        'has_next':mangoes.has_next()}
        return Response(data,status=status.HTTP_202_ACCEPTED)


class FilterSwipe(APIView):
    queryset = Profile.objects.all()
    serializer_class = ProfilesSerializer

    def get(self,request):
        user = getuser(request)
        filters = getfilters(request,exclude=[''],contain_words=['',])
        print(filters)
        profiles = Profile.objects.filter(**filters)

        serializer_class = ProfilesSerializer(profiles,many=True)
        data = {'status':'success','profiles':serializer_class.data}

        return Response(data,status=status.HTTP_202_ACCEPTED)



class LikeUnlikeMango(APIView):
    queryset = Profile.objects.all()
    serializer_class = ProfilesSerializer

    def get(self,request):
        user = getuser(request)
        try:
            profile = Profile.objects.get(user=user)
        except ObjectDoesNotExist:
            profile = Profile.objects.create(user=user)
        likedmangoes = Profile.objects.filter(user__in=profile.liked_mangoes.all())
        serializer_class = ProfilesSerializer(likedmangoes,many=True)
        return Response(serializer_class.data)


    def post(self,request):
        action = request.data.get('action')
        mangoe_id= request.data.get('mangoe_id')
        user = getuser(request)
        try:
            profile = Profile.objects.get(user=user)
        except ObjectDoesNotExist:
            profile = Profile.objects.create(user=user)
        try:
            mangoe = User.objects.get(id=mangoe_id)
        except ObjectDoesNotExist:
            return Response({'action':action,'success':False,},status=status.HTTP_404_NOT_FOUND)
        if action == 'like':
            profile.liked_mangoes.add(mangoe)
        elif action == 'unlike':
            profile.liked_mangoes.remove(mangoe)
        return Response({'action':action,'success':True},status=status.HTTP_202_ACCEPTED)



class ChatView(APIView):
    queryset = Chat.objects.all()
    serializer_class = ChatsSerializer

    def get(self,request):
        user = getuser(request)
        filters = getfilters(request,exclude=[''],contain_words=['',])
        chat = Chat.objects.filter(user=user,**filters)
        serializer_class = ChatsSerializer(chat,many=True)
        return Response(serializer_class.data,status=status.HTTP_202_ACCEPTED)


    def post(self,request):
        user = getuser(request)

        serializer_class = ChatsSerializer(data=request.data)
        if serializer_class.is_valid():
            serializer_class.save()
            chat = serializer_class.instance
        serializer_class = ChatsSerializer(chat)
        data = {'status':'success','chat':serializer_class.data}
        return Response(data,status=status.HTTP_202_ACCEPTED)


class ReplyView(APIView):
    queryset = Reply.objects.all()
    serializer_class = RepliesSerializer

    def get(self,request):
        user = getuser(request)
        filters = getfilters(request,exclude=[''],contain_words=['',])
        reply = Reply.objects.filter(**filters)
        serializer_class = RepliesSerializer(reply,many=True)
        return Response(serializer_class.data,status=status.HTTP_202_ACCEPTED)


    def post(self,request):
        user = getuser(request)

        serializer_class = RepliesSerializer(data=request.data)
        if serializer_class.is_valid():
            serializer_class.save()
            reply = serializer_class.instance
        serializer_class = RepliesSerializer(reply)
        data = {'status':'success','reply':serializer_class.data}
        return Response(data,status=status.HTTP_202_ACCEPTED)