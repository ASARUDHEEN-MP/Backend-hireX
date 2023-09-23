from django.urls import path
from .views import register_user_and_recruiter,register_verify,RecruiterDetailsView,employeerplanview,paymentview,walletview,imageurl,JobpostView,jobView,Applicantjobview,updatestatus,EmployeerHomeView


urlpatterns = [
   
path('register-recruiter/', register_user_and_recruiter.as_view(), name='register_recruiter'),
path('verify-recruiter/', register_verify.as_view(), name='verify-recruiter'),
path('user-recruiter-details/<int:pk>/', RecruiterDetailsView.as_view(), name='user-recruiter-details'),
path('plan-view/', employeerplanview.as_view(), name='plan-view'),
path('payment-details/<int:pk>/', paymentview.as_view(), name='payment-details'),
path('wallet-view/<int:pk>/', walletview.as_view(), name='wallet-view'),
path('image-view/<int:pk>/', imageurl.as_view(), name='image-view'),
path('jobpost-view/<int:pk>/', JobpostView.as_view(), name='jobpost-view'),
path('job-view/<int:pk>/', jobView.as_view(), name='job-view'),
path('applicant-view/<int:pk>/', Applicantjobview.as_view(), name='applicant-view'),
path('update-status/<int:user_id>/<int:post_id>/', updatestatus.as_view(), name='update-status'),
path('employeer-home/<int:pk>/', EmployeerHomeView.as_view(), name='employeer-home'),
]



