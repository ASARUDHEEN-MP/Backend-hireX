from django.urls import path
from .views import RegisterView, LoginView,VerifyOTPView,ForgotPasswordView,Logoutview,ImageUploadView,userdetailsview,companyjoblist,Jobdetailsview,Applieduser,Appiedjobview,JobPostSearchView,Homeview,CompanyProfile,follow_company,unfollow_company,is_following_company,RecommendedJobListView,IgnoreJobPostView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('forgotpassword/', ForgotPasswordView.as_view(), name='forgotpassword'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/',Logoutview.as_view(),name='logout'),
    path('upload-image/', ImageUploadView.as_view(), name='upload-image'),
    path('user-details/<int:pk>/', userdetailsview.as_view(), name='user-details'),
    path('company-joblist/<int:pk>/', companyjoblist.as_view(), name='company-joblist'),
    path('jobdetails-view/<int:pk>/', Jobdetailsview.as_view(), name='jobdetails-view/'),
    path('applicands/<int:pk>/<int:company_id>/',Applieduser.as_view(), name='your-view-name'),
    path('Appliedjobview/<int:pk>/',Appiedjobview.as_view(), name='your-view-name'),
    path('search-jobposts/', JobPostSearchView.as_view(), name='search-jobposts'),
    path('home-view/', Homeview.as_view(), name='home-view'),
    path('Companydetails-view/<int:pk>/', CompanyProfile.as_view(), name='Companydetails-view'),
    # follow and unfollow
    path('follow/<int:company_id>/', follow_company, name='follow_company'),
    path('unfollow/<int:company_id>/', unfollow_company, name='unfollow_company'),
    path('is_following/<int:company_id>/', is_following_company, name='is_following_company'),
    path('recommended-jobs/<int:pk>/', RecommendedJobListView.as_view(), name='recommended-jobs'),
    path('ignore-job-post/<int:pk>/', IgnoreJobPostView.as_view(), name='ignore-job-post')


]


