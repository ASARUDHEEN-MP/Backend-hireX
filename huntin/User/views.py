from rest_framework.views import APIView
from rest_framework import status,viewsets
from Recruiter.serializers import postcreationserializer,RecruiterDetailsSerializer
from Recruiter.models import JobPost,Applicants
from .serializers import CustomUserSerializer,UserImageSerializer,UserDetailsSerializer,Applicantserializer,JobPostSerializer,IsFollowingSerializer,IgnoreJobPostSerializer
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from .models import CustomUser,UserImage,Userdetails,UserFollowsCompany,IgnoreJobPost
from .tocken import get_tokens
from rest_framework.decorators import api_view, permission_classes
from .otp import send_mail
import datetime
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication  # type: ignore
from rest_framework_simplejwt.tokens import OutstandingToken, BlacklistedToken
import random
import string
from django.urls import reverse
from django.utils.crypto import get_random_string
import cloudinary.uploader
from django.http import JsonResponse
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions, status
from django.shortcuts import get_object_or_404
from Recruiter.models import RecruiterDetails
from rest_framework import generics
from rest_framework import filters
from rest_framework.decorators import action
from django.db.models import Q
from django.contrib.auth import get_user_model
from rest_framework.generics import ListAPIView




class RegisterView(APIView):
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            Userdetails.objects.create(user=user)
            # Generate OTP and save the user object
            otp = user.generate_otp()
            user.otp = otp
            user.save()
            
            subject = 'Your OTP for Registration with HireX'
            message = f'Your OTP is: {otp}'
            from_email = 'hirexjobs66@gmail.com'
            recipient_list = [user.email]

            # Send the OTP to the user's email
            send_mail(subject, message, from_email, recipient_list)

            return Response({'message': 'User registered successfully.'}, status=status.HTTP_201_CREATED)
       
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        


class VerifyOTPView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp_code = request.data.get('otp')
        try:
            
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        print(type(otp_code))
        print(otp_code)
        if not user.is_otp_valid(otp_code):
            raise AuthenticationFailed({'invalid': 'Invalid OTP'})
        

        # Mark the email as verified and save the user object
        user.mark_email_verified()
        user.is_active = True  # Activate the user account
        user.is_employee = True 
        user.save()  # Save the changes to the database

        return Response({'message': 'Email verified successfully. Account activated.'}, status=status.HTTP_200_OK)


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({'message': 'User not found.'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.check_password(password):
            raise AuthenticationFailed({'invalid': 'Invalid password'})
        
     

        user.last_login = timezone.now()
        user.save()

        # Serialize user data
        serialized_data = CustomUserSerializer(user).data
        
        # Get JWT token
        token = get_tokens(user)
        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        
        # Create response
        response.data =({
            'userInfo': serialized_data,
            'token': token,
            'message': 'Successfully logged in',
            'status': status.HTTP_200_OK
        })

        # Set JWT token as an HTTP-only cookie
        
        return response
    

    def get(self, request):
        user_id = request.user
        print(user_id)
        # user = Account.objects.get(id=user_id)
        return Response({'user_id': user_id})
    

class Logoutview(APIView):
    def post(self,request):
        response = Response()
        response.delete_cookie('jwt')

        response.data = {
            'message':'sucess'
        }

        return response
    


class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({'message': 'User with this email does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate a random password
        
        new_password = ''.join(random.choices(string.digits, k=5))
        user.set_password(new_password)
        user.save()
        subject = ' newpassword from HireX'
        message = f'Your newpassword for Login you can change password from profile: {new_password}'
        from_email = 'hirexjobs66@gmail.com'
        recipient_list = [user.email]

        # Send password reset email
        send_mail(subject, message, from_email, recipient_list)

        return Response({'message': 'Password reset successful. Check your email for the new password.'}, status=status.HTTP_200_OK)
    

class ImageUploadView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request, format=None):
        if request.FILES.get('image'):
            uploaded_image = cloudinary.uploader.upload(request.FILES['image'])

            # Construct the full Cloudinary URL
            image_url = uploaded_image['url']
            url_string=image_url
            print(url_string)
            # Check if a UserImage instance exists for the user
            user_image = UserImage.objects.filter(user=request.user).first()

            if user_image:
                # Update the image URL if an instance exists
                user_image.image = image_url
                user_image.image_url=url_string
                user_image.save()
            else:
                # Create a new instance if an instance doesn't exist
                user_image = UserImage.objects.create(user=request.user, image=image_url,image_url=url_string)

            return JsonResponse({'image_url': image_url})
        return JsonResponse({'error': 'Invalid request.'}, status=status.HTTP_400_BAD_REQUEST)
    

# usserdetails edir api
class userdetailsview(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_pk = self.kwargs['pk']
        try:
            user = CustomUser.objects.get(id=user_pk)
            print(user.id)
            try:
                image_url = UserImage.objects.get(user=user) 
                user_serializer = CustomUserSerializer(user)
                Userdetail=Userdetails.objects.get(user=user)
                imagerserializer = UserImageSerializer(image_url)
                Userdetailserializer=UserDetailsSerializer(Userdetail)
                image='True'
            except UserImage.DoesNotExist:
                # If image details are not found, use a placeholder image URL
                imagerserializer = {'image': 'path-to-placeholder-image.jpg'}
                image='false'
            if image=='True':
                imagerserializer=imagerserializer.data
            else:
                imagerserializer=imagerserializer

            response_data = {
                "user": user_serializer.data,
                "image_url": imagerserializer,
                "userdetails":Userdetailserializer.data,
                
            
                 # Use the dictionary directly
            }
            return Response(response_data)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found."}, status=404)
        except user.DoesNotExist:
            return Response({"error": "user details not found for this user."}, status=404)
        
   
    def patch(self, request, *args, **kwargs):
            user_pk = self.kwargs['pk']
            try:
                user = CustomUser.objects.get(id=user_pk)
                userdetail = Userdetails.objects.get(user=user)
            except CustomUser.DoesNotExist:
                return Response({"error": "User not found."}, status=404)
            except Userdetails.DoesNotExist:
                return Response({"error": "User details not found for this user."}, status=404)

            # Update user data
            user_serializer = CustomUserSerializer(user, data=request.data['user'], partial=True)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

            # Update user details
            userdetail_serializer = UserDetailsSerializer(userdetail, data=request.data['user_details'], partial=True)
            print(userdetail_serializer)
            userdetail_serializer.is_valid(raise_exception=True)
            userdetail_serializer.save()

            response_data = {
                "user": user_serializer.data,
                "user_details": userdetail_serializer.data
            }

            return Response(response_data)
    
# class companyjoblist(APIView):
#     def get(self, request, *args, **kwargs):
#         posts = JobPost.objects.all()
#         serializer = postcreationserializer(posts, many=True, context={'request': request})
#         for post_data in serializer.data:
#             company_id = post_data.get('company')
#             try:
#                 company_name = CustomUser.objects.get(id=company_id).username
#                 user_image = UserImage.objects.get(user=company_id)
#                 post_data['user_image'] = user_image.image_url
#                 post_data['company_name'] = company_name
#             except CustomUser.DoesNotExist:
#                 post_data['user_image'] = None
#                 post_data['company_name'] = None
#         return Response(serializer.data, status=status.HTTP_200_OK)
class companyjoblist(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user  # Assuming you are using authentication

        # Get all the job posts that are not ignored by the user
        posts = JobPost.objects.exclude(
            Q(ignorejobpost__user=user)
        )

        serializer = postcreationserializer(posts, many=True, context={'request': request})
        for post_data in serializer.data:
            company_id = post_data.get('company')
            try:
                company_name = CustomUser.objects.get(id=company_id).username
                user_image = UserImage.objects.get(user=company_id)
                post_data['user_image'] = user_image.image_url
                post_data['company_name'] = company_name
            except CustomUser.DoesNotExist:
                post_data['user_image'] = None
                post_data['company_name'] = None

        return Response(serializer.data, status=status.HTTP_200_OK)
        
class Jobdetailsview(APIView):
    def get(self, request, *args, **kwargs):
        post_id = self.kwargs['pk']
        post = get_object_or_404(JobPost, id=post_id)
        serializer = postcreationserializer(post)
        company_id = serializer.data['company']
        try:
            company_name = CustomUser.objects.get(id=company_id).username
            companylocation=RecruiterDetails.objects.get(user=company_id)
            companystate=companylocation.state
            companycountry=companylocation.country
            image_url=UserImage.objects.get(user=company_id).image_url
        except CustomUser.DoesNotExist:
            company_name = None
            image_url=None
        
        # Create a new dictionary to hold the modified data
        modified_data = serializer.data.copy()
        modified_data['company_name'] = company_name
        modified_data['company_state'] = companystate
        modified_data['company_country'] = companycountry
        modified_data['image_url'] = image_url


        return Response(modified_data, status=status.HTTP_200_OK)



class Applieduser(APIView):
     permission_classes = [IsAuthenticated]
    
     def post(self, request, pk,company_id, format=None):
        try:
            user = CustomUser.objects.get(pk=pk)
            company =company_id
          
            # Create a dictionary with the request data and add 'user' and 'created_at' fields
            data = request.data
            
            data['user'] = user.id
            data['company'] = company
            data['created_at'] = timezone.now()  # Set the 'created_at' field to the current timestamp

            serializer = Applicantserializer(data=data)
            post_id = request.data.get('postid')
            existing_application = Applicants.objects.filter(user=user, postid=post_id).first()
            if existing_application:
                return Response({'message': 'You have already applied for this job.'}, status=status.HTTP_400_BAD_REQUEST)

            if serializer.is_valid():
                serializer.save()
                

                return Response({'message': 'Successfully applied'}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except CustomUser.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

class Appiedjobview(APIView):
    def get(self, request, *args, **kwargs):
        user_id = self.kwargs['pk']
        try:
            applicants_list = Applicants.objects.filter(user=user_id)
            if applicants_list:
                serializer = Applicantserializer(applicants_list, many=True)
                company_ids = list(set([item['companyid'] for item in serializer.data]))
                print(company_ids)
                
                # Retrieve both 'id' and 'username' fields from CustomUser model
                company_usernames = CustomUser.objects.filter(id__in=company_ids).values_list('id', 'username')
                company_images = UserImage.objects.filter(user__in=company_ids).values_list('user','image_url')
                # Debugging: Print the company_ids and company_usernames
              
                
                # Create a dictionary to map company IDs to usernames
                company_id_to_username = dict(company_usernames)
                company_id_to_image_url = dict(company_images)
                
                # Iterate through the serializer data and assign company_username
                for item in serializer.data:
                    company_id = item['companyid']
                    item['company_username'] = company_id_to_username.get(company_id, '')
                    item['company_image'] = company_id_to_image_url.get(company_id, '')
                
                return Response(serializer.data)
            else:
                # Return a response indicating no applications found
                return JsonResponse({'message': 'No applications found for this user.'})
        except Applicants.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)




                    

class JobPostSearchView(generics.ListAPIView):
    queryset = JobPost.objects.all()
    serializer_class = JobPostSerializer  # Use the modified serializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['skills__icontains']

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('skills')

        if search_query:
            queryset = queryset.filter(skills__icontains=search_query)
            
        return queryset
    
    



class Homeview(APIView):
    def get(self, request):
        companies = CustomUser.objects.filter(is_recruiter=True)

        try:
            serializer = CustomUserSerializer(companies, many=True)
            data = serializer.data

            # Loop through the data and add the image URL and recruiter details for each company
            for company_data in data:
                company_id = company_data['id']

                # Retrieve user image
                user_image = UserImage.objects.filter(user_id=company_id).first()

                if user_image:
                    # Access the image URL directly from the UserImage object
                    company_data['image_url'] = user_image.image_url

                # Retrieve recruiter details
                recruiter_details = RecruiterDetails.objects.filter(user_id=company_id).first()

                if recruiter_details:
                    # Serialize the recruiter details
                    recruiter_details_serializer = RecruiterDetailsSerializer(recruiter_details)
                    company_data['recruiter_details'] = recruiter_details_serializer.data

            return Response(data)
        except CustomUser.DoesNotExist:
            return Response({'message': 'Data not found'}, status=status.HTTP_404_NOT_FOUND)

        

         
         
class CompanyProfile(APIView):
    def get(self, request, *args, **kwargs):
        user_id = self.kwargs['pk']
        try:
            companydetails = CustomUser.objects.get(id=user_id)
            Aboutcompany = RecruiterDetails.objects.get(user_id=user_id)
            
            custom_user_serializer = CustomUserSerializer(companydetails)
            recruiter_details_serializer = RecruiterDetailsSerializer(Aboutcompany)
            imageurl=UserImage.objects.get(user=user_id)
           
            # Check if both objects exist
            if companydetails and Aboutcompany:
                # Create a dictionary to hold both serialized data
                data = {
                    'custom_user': custom_user_serializer.data,
                    'recruiter_details': recruiter_details_serializer.data,
                    'imageurl':imageurl.image_url
                }
                
                return Response(data)
            else:
                return Response({'message': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)
        except CustomUser.DoesNotExist:
            return Response({'message': 'CustomUser not found'}, status=status.HTTP_404_NOT_FOUND)
        except RecruiterDetails.DoesNotExist:
            return Response({'message': 'RecruiterDetails not found'}, status=status.HTTP_404_NOT_FOUND)
        
# follow and unfollow

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def follow_company(request, company_id):
    try:
        company_to_follow = CustomUser.objects.get(id=company_id)
        current_user = request.user

        # Ensure the current user is not trying to follow themselves
        if company_to_follow == current_user:
            return Response({'detail': 'You cannot follow yourself.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the follow relationship already exists
        if not UserFollowsCompany.objects.filter(user=current_user, company=company_to_follow).exists():
            UserFollowsCompany.objects.create(user=current_user, company=company_to_follow)
            return Response({'detail': 'You are now following this company.'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'You are already following this company.'}, status=status.HTTP_400_BAD_REQUEST)

    except CustomUser.DoesNotExist:
        return Response({'detail': 'Company not found.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def unfollow_company(request, company_id):
    try:
        company_to_unfollow = CustomUser.objects.get(id=company_id)
        current_user = request.user

        if request.method == 'DELETE':
            # Check if the follow relationship exists
            follow_relationship = UserFollowsCompany.objects.filter(user=current_user, company=company_to_unfollow)
            if follow_relationship.exists():
                follow_relationship.delete()
                return Response({'detail': 'You have unfollowed this company.'}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'You are not following this company.'}, status=status.HTTP_400_BAD_REQUEST)

    except CustomUser.DoesNotExist:
        return Response({'detail': 'Company not found.'}, status=status.HTTP_404_NOT_FOUND)

    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def is_following_company(request, company_id):
    try:
        current_user = request.user
        company_to_check = CustomUser.objects.get(id=company_id)

        # Check if the follow relationship exists
        is_following = UserFollowsCompany.objects.filter(user=current_user, company=company_to_check).exists()

        data = {'is_following': is_following}
        serializer = IsFollowingSerializer(data)
        print(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except CustomUser.DoesNotExist:
        return Response({'detail': 'Company not found.'}, status=status.HTTP_404_NOT_FOUND)
    





class RecommendedJobListView(APIView):
    serializer_class = JobPostSerializer

    def get(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        user_details = Userdetails.objects.get(user=user)

        user_skills = user_details.skills  # Use userdetails object
        user_experience = user_details.experience  # Use userdetails object

        # Split the user's skills into a list
        user_skill_list = [skill.strip() for skill in user_skills.split(",")]

        # Define a Q object to filter job posts based on skills
        skill_filters = Q()
        for skill in user_skill_list:
            skill_filters |= Q(skills__icontains=skill)

        # Define a Q object to filter job posts based on experience
        experience_filters = Q()
        if user_experience == "0-1 years":
            # Filter for 0-1 years experience
            experience_filters |= Q(experience_from__lte=0, experience_to__gte=1)
        elif user_experience == "5 years and more":
            # Filter for 5 years and more experience
            experience_filters |= Q(experience_from__lte=5)
        else:
            # For other experience ranges, split the range and filter
            try:
                min_exp, max_exp = map(int, user_experience.split("-"))
                experience_filters |= Q(experience_from__lte=max_exp, experience_to__gte=min_exp)
            except ValueError:
                # Handle invalid experience format here (e.g., log an error)
                pass
        
        # Print the user's experience and the generated experience filter
        print(f"User Experience: {user_experience}")
        print(f"Experience Filter: {experience_filters}")

        # Combine skill and experience filters using the AND operator
        queryset = JobPost.objects.filter(skill_filters & experience_filters)

        # Exclude ignored jobs by the user
        queryset = queryset.exclude(ignorejobpost__user=user)

        serializer = self.serializer_class(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)



class IgnoreJobPostView(APIView):
    def post(self, request, pk, format=None):
        # Get the user based on the provided PK
        try:
            user = get_user_model().objects.get(pk=pk)
        except get_user_model().DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Extract job_post_id from request data
        job_post_id = request.data.get('postid')
        
        # Create an IgnoreJobPost entry
        ignore_job_post = IgnoreJobPost.objects.create(
            user=user,
            ignorepostid_id=job_post_id,
            
        )
        
        # Serialize the created entry (you can customize the serializer as needed)
        serializer = IgnoreJobPostSerializer(ignore_job_post)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)