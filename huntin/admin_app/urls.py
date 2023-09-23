from django.urls import path
from .views import EmployeeUserListView,CompanyListView,CreatePostAPIView,AdminPostListView,paymentsuccessAPI,PaymentHistoryview,Dashboardview

urlpatterns = [
    path('user-manage/', EmployeeUserListView.as_view(), name='employee-user-list'),
    path('user-manage/<int:pk>/', EmployeeUserListView.as_view(), name='employee-user-detail'),
    path('company-manage/', CompanyListView.as_view(), name='compnay-list'),
    path('company-manage/<int:pk>/', CompanyListView.as_view(), name='company-detail'),
    path('create-post/', CreatePostAPIView.as_view(), name='create-post'),
    path('postview/', AdminPostListView.as_view(), name='postview'),
    path('postview/<int:pk>/', AdminPostListView.as_view(), name='postview-delete'),
    path('planpayment/', paymentsuccessAPI.as_view(), name='planpayment'),
    path('paymenthistory/', PaymentHistoryview.as_view(), name='paymenthistory'),
    path('dashboardview/', Dashboardview.as_view(), name='dashboardview'),




    
]
