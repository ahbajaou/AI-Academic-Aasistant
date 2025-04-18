from django.urls import path
from .views import signin, signup, verify

urlpatterns = [
    path('signup', signup, name="User Sign Up"),
    path('verify', verify, name="Account Verification"),
    path('signin', signin, name="User Sign In"),
    # path('profile', profile_data, name="Get User Data"),
    # path('fields', storeUserFileds, name="User Fileds"),
    # path('getUserFields', getUserFields, name="User fields geter")
]