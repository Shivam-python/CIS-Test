from django.urls import path,include
from .views import *
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('user', UserClass, basename="user")
router.register('tags', TagsAPI, basename="tags")

urlpatterns=[
    path('', include(router.urls)),
    path('validate-otp/', ValidateOtp.as_view(), name='validate-otp'),
    path('change-password/', ForgotPasswordChange.as_view(), name='change-password'),
    path('logout/', Logout.as_view(), name='logout'),
    path('category/', CategoryAPI.as_view(), name='category'),
    path('category_detail/<int:pk>', CategoryDetailsAPI.as_view(), name='category_detail'),
    path('products/', ProductsAPI.as_view(), name='category'),
    path('product_detail/<int:pk>', ProductsDetailsAPI.as_view(), name='product_detail'),

]