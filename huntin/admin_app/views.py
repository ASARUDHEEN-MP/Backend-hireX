from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from User.models import CustomUser
from User.serializers import CustomUserSerializer
from .serializers import PostSerializer,PaymentSerializer
from .models import post,Payment
from django.shortcuts import get_object_or_404
from datetime import datetime
from Recruiter.models import Wallet
from django.db.models import Sum

class EmployeeUserListView(APIView):
    
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request, format=None):
        employees = CustomUser.objects.filter(is_employee=True)
        
        serializer = CustomUserSerializer(employees, many=True)
        return Response(serializer.data)
    
    def delete(self, request, pk, format=None):
        try:
            employee = CustomUser.objects.get(pk=pk, is_employee=True)
        except CustomUser.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        employee.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, pk, format=None):
        
        try:
            employee = CustomUser.objects.get(pk=pk, is_employee=True)
        except CustomUser.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        # Invert the is_active field
        employee.is_active = not employee.is_active
        employee.save()

        serializer = CustomUserSerializer(employee)
        return Response(serializer.data)
    

class CompanyListView(APIView):
    
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request, format=None):
        company = CustomUser.objects.filter(is_recruiter=True)
        
        serializer = CustomUserSerializer(company, many=True)
        return Response(serializer.data)
    
    def delete(self, request, pk, format=None):
        try:
            company = CustomUser.objects.get(pk=pk, is_recruiter=True)
        except CustomUser.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        company.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, pk, format=None):
        print("hello hudfjsbj")
        try:
            
            company = CustomUser.objects.get(pk=pk, is_recruiter=True)
        except CustomUser.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        # Invert the is_active field
        company.is_active = not company.is_active
        company.save()

        serializer = CustomUserSerializer(company)
        return Response(serializer.data)
    


# post creatation api


class CreatePostAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]
    def post(self, request, format=None):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class AdminPostListView(APIView):
    def get(self, request):
        posts = post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, pk, format=None):
        try:
            Post = post.objects.get(pk=pk)
        except post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        Post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    


# payment 


class paymentsuccessAPI(APIView):
       
        def post(self, request, format=None):
            serializer = PaymentSerializer(data=request.data)
            if serializer.is_valid():
                payment_instance = serializer.save( createdat=datetime.now()) 
                user_id = request.data.get('user_id')  # Get the user_id from request data
                postcount = request.data.get('postcount')
                if payment_instance.status == 'completed':
                    user = CustomUser.objects.get(id=user_id)
                    wallet, created = Wallet.objects.get_or_create(user=user)
                    wallet.post_count += int(postcount) 
                    wallet.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class PaymentHistoryview(APIView):
     permission_classes = [permissions.IsAdminUser]
     def get(self, request):
          pay = Payment.objects.all()
          paymentSerializer=PaymentSerializer(pay, many=True)
          return Response(paymentSerializer.data, status=status.HTTP_200_OK)


class Dashboardview(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        # Get all payments
        payments = Payment.objects.all()
        Employeer_count = CustomUser.objects.filter(is_recruiter=True).count()
        Employee_count=CustomUser.objects.filter(is_employee=True).count()
        # Calculate the total amount using the aggregate function on the QuerySet
        total_amount = payments.aggregate(total_amount=Sum('amount'))['total_amount'] or 0.0
  
        # Serialize the payments
        paymentSerializer = PaymentSerializer(payments, many=True)

        # Create a response dictionary that includes the total amount
        response_data = {
            'total_amount': total_amount,
            'payments': paymentSerializer.data,
            'Employeer': Employeer_count,
            'Employee':Employee_count,
        }

        return Response(response_data, status=status.HTTP_200_OK)
        

        

