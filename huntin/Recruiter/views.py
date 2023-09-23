from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import RecruiterDetailsSerializer,WalletSerializer,postcreationserializer,companyfollower
from User.serializers import CustomUserSerializer,UserImageSerializer,Applicantserializer
from .models import RecruiterDetails,Wallet,JobPost,Applicants
from User.models import CustomUser,UserImage,UserFollowsCompany
from User.otp import send_mail
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import generics
from admin_app.models import post
from admin_app.serializers import PostSerializer,PaymentSerializer
from rest_framework.permissions import IsAuthenticated
from admin_app.models import Payment
from django.core.serializers import serialize
from datetime import datetime
from chat.models import Message

class register_user_and_recruiter(APIView):
    def post(self,request):
        if request.method == 'POST':
            user_serializer = CustomUserSerializer(data=request.data)
            
            if user_serializer.is_valid():
                user = user_serializer.save()  # Create user
                
                otp = user.generate_otp()
                user.otp = otp
                user.save()

                subject = 'Your OTP for Registration with HireX'
                message = f'Your OTP is: {otp}'
                from_email = 'hirexjobs66@gmail.com'  
                recipient_list = [user.email]

                # Send the OTP to the user's email
                send_mail(subject, message, from_email, recipient_list)

                # Create and link RecruiterDetails instance
                recruiter_data = {
                    'user': user.id,
                    'state': request.data.get('state'),
                    'country': request.data.get('country'),
                    'district': request.data.get('district'),
                   
                    
                    
                }
                recruiter_serializer = RecruiterDetailsSerializer(data=recruiter_data)
                if recruiter_serializer.is_valid():
                    
                    recruiter_serializer.save()
                else:
                    print(recruiter_serializer.errors)

                return Response(user_serializer.data, status=status.HTTP_201_CREATED)
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class register_verify(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp_code = request.data.get('otp')
        try:
            
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        if not user.is_otp_valid(otp_code):
            raise AuthenticationFailed({'invalid': 'Invalid OTP'})
        

        # Mark the email as verified and save the user object
        user.mark_email_verified()
        user.is_active = True  # Activate the user account
        user.is_recruiter = True 
        user.save()  # Save the changes to the database

        return Response({'message': 'Email verified successfully. Account activated.'}, status=status.HTTP_200_OK)
    


class RecruiterDetailsView(generics.RetrieveAPIView):
    
    serializer_class = RecruiterDetailsSerializer

    def get(self, request, *args, **kwargs):
        user_pk = self.kwargs['pk']
        try:
            user = CustomUser.objects.get(id=user_pk)
            recruiter_details = RecruiterDetails.objects.get(user=user)
            user_serializer = CustomUserSerializer(user)
            recruiter_serializer = self.get_serializer(recruiter_details)
            
            try:
                image_url = UserImage.objects.get(user=user)
                imagerserializer = UserImageSerializer(image_url)
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
                "recruiter_details": recruiter_serializer.data,
                "image_url": imagerserializer,
                
            
                 # Use the dictionary directly
            }
            
            return Response(response_data)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found."}, status=404)
        except RecruiterDetails.DoesNotExist:
            return Response({"error": "Recruiter details not found for this user."}, status=404)

        

    def patch(self, request, *args, **kwargs):
        user_pk = self.kwargs['pk']
        try: 
           
            user = CustomUser.objects.get(id=user_pk)
            recruiter_details = RecruiterDetails.objects.get(user=user)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found."}, status=404)
        except RecruiterDetails.DoesNotExist:
            return Response({"error": "Recruiter details not found for this user."}, status=404)
        
        # Update user data
        user_serializer = CustomUserSerializer(user, data=request.data['user'], partial=True)
        user_serializer.is_valid(raise_exception=True)
        user_serializer.save()
        
        # Update recruiter details
        recruiter_serializer = RecruiterDetailsSerializer(recruiter_details, data=request.data['recruiter_details'], partial=True)
        recruiter_serializer.is_valid(raise_exception=True)
        recruiter_serializer.save()
        
        response_data = {
            "user": user_serializer.data,
            "recruiter_details": recruiter_serializer.data
        }
        
        return Response(response_data)



# to get the plandetails api

class employeerplanview(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        posts = post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class paymentview(APIView):
    
    def get(self, request, *args, **kwargs):
           user_id = self.kwargs['pk']
           try:
               
               paymentdetails=Payment.objects.filter(user_id=user_id)
               serializer = PaymentSerializer(paymentdetails, many=True)
               response_data = {
                'payment_details': serializer.data,
               }
               
               return Response(response_data)
           except CustomUser.DoesNotExist:
                return Response({'error': 'User not found'}, status=404)
           
class walletview(APIView):
     def get(self, request, *args, **kwargs):
          user = self.kwargs['pk']
      
          try:
              
              walletdetails=Wallet.objects.get(user=user)
              
              serializer=WalletSerializer(walletdetails)

              Response_data={
                  'walletdetails':serializer.data
              }
              return Response(Response_data)
          except Wallet.DoesNotExist:
              return Response({'error':'wallet not found'})
          


class imageurl(APIView):
    def get(self, request, *args, **kwargs):
        user = self.kwargs['pk']
        try:
            image = UserImage.objects.get(user=user)
            serializer = UserImageSerializer(image)
            response_data = serializer.data
            return Response(response_data)
        except UserImage.DoesNotExist:
            return Response({'message': 'Image not found.'}, status=status.HTTP_404_NOT_FOUND)
        

class JobpostView(APIView):
    def post(self, request, *args, **kwargs):
        user = self.kwargs['pk']
       
        try:
            
            postSerializer = postcreationserializer(data=request.data)
            wallet = Wallet.objects.get(user=user)
            if postSerializer.is_valid():
                if wallet.post_count > 0:
                    wallet.post_count -= 1
                    wallet.save()
                    postcreation = postSerializer.save()
                    return Response(postSerializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response({"message": "Unable to create post. Please Recharge."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                print(postSerializer.errors)
                return Response(postSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Wallet.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
    def get(self, request, *args, **kwargs):
         serializer_class = postcreationserializer
         user = self.kwargs['pk']
         try:
             posts=JobPost.objects.filter(company=user)
             serializer = postcreationserializer(posts, many=True)
             response_data = serializer.data
             return Response(response_data)
         except JobPost.DoesNotExist:
            return Response({'message': 'Data not found.'}, status=status.HTTP_404_NOT_FOUND)

         
             
class jobView(APIView):
    def get(self, request, *args, **kwargs):
        postid=self.kwargs['pk']
        try:
             posts=JobPost.objects.get(id=postid)
             serializer = postcreationserializer(posts)
             response_data = serializer.data
             return Response(response_data)
        except JobPost.DoesNotExist:
            return Response({'message': f'Data not found for postid: {postid}'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, pk):
        try:
            job_post = JobPost.objects.get(id=pk)

        except JobPost.DoesNotExist:
            return Response({'message': 'Job post not found.'}, status=status.HTTP_404_NOT_FOUND)
        job_post.is_active = not job_post.is_active
        job_post.save()
        return Response({'message': 'Job post updated successfully.'})
    

class Applicantjobview(APIView):
    def get(self, request, *args, **kwargs):
        postid = self.kwargs['pk']
        applicandslist = Applicants.objects.filter(postid=postid)
        if applicandslist:
            serializer = Applicantserializer(applicandslist, many=True)
            user_ids = [applicant_data['user'] for applicant_data in serializer.data]
            user_data = CustomUser.objects.filter(id__in=user_ids).values('id', 'username', 'email','phonenumber')
            user_data_dict = {user['id']: {'username': user['username'], 'email': user['email'],'phonenumber':user['phonenumber']} for user in user_data}
            for applicant_data in serializer.data:
                user_id = applicant_data['user']
                if user_id in user_data_dict:
                    user_info = user_data_dict[user_id]
                    applicant_data['username'] = user_info['username']
                    applicant_data['email'] = user_info['email']
                    applicant_data['phonenumber'] = user_info['phonenumber']
            
            return Response(serializer.data)
        else:
            return Response({'message': 'No applicants found'}, status=status.HTTP_404_NOT_FOUND)
        
class updatestatus(APIView):
    def patch(self, request, user_id, post_id, format=None):
        try:
            applicant = Applicants.objects.get(user=user_id, postid=post_id)
            usermail=CustomUser.objects.get(id=user_id)
            print(usermail.email)
        except Applicants.DoesNotExist:
            return Response({"error": "Applicant not found."}, status=status.HTTP_404_NOT_FOUND)
        new_status = request.data.get('selectedValue')
        
        if new_status in [choice[0] for choice in Applicants.STATUS_CHOICES]:
            print('hellooooo')
            applicant.status = new_status
            applicant.save()
            return Response({"message": "Applicant status updated successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid status value."}, status=status.HTTP_400_BAD_REQUEST)


class EmployeerHomeView(APIView):
    def get(self, request, pk, *args, **kwargs):
        try:
            applicants = Applicants.objects.filter(companyid=pk)
            followers = UserFollowsCompany.objects.filter(company=pk)
            follow_serializer = companyfollower(followers, many=True)  # Serialize the followers
            serialized_applicants = []
            serialized_followers = []  # Create a separate list for followers

            for applicant in applicants:
                user_username = applicant.user.username
                postname = applicant.postid.skills  # Assuming skills is a field in JobPost model
                user_id = applicant.user.id  # Get the user ID
                serialized_applicant = {
                    'username': user_username,
                    'status': applicant.status,
                    'created_at': applicant.created_at,
                    'post_id': postname,
                    'user_id': user_id,  # Include the user ID
                    'postid': applicant.postid.id,
                    'FOLLOWERS': follow_serializer.data  # Use follow_serializer.data to include the serialized data
                    # Add other fields you need
                }
                serialized_applicants.append(serialized_applicant)

            for follower in followers:
                follower_username = follower.user.username
                followerid=follower.user.id
                serialized_follower = {
                    'username': follower_username,
                    'userid':followerid
                }
                serialized_followers.append(serialized_follower)

            return Response({'applicants': serialized_applicants, 'followers': serialized_followers}, status=status.HTTP_200_OK)
        except Applicants.DoesNotExist:
            return Response({"error": "Applicant not found."}, status=status.HTTP_404_NOT_FOUND)


             
         


