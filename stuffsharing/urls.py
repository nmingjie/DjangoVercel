from django.urls import path 
from . import views
#All the urls are defined in this file
urlpatterns = [
    path('', views.home, name='stuffsharing-home'),
    path('search/', views.search, name='stuffsharing-search'),
    path('myadsadd/', views.myadsadd, name='stuffsharing-myadsadd'),
    path('myadsactive/', views.myadsactive, name='stuffsharing-myadsactive'),
    path('myadsinactive/', views.myadsinactive, name='stuffsharing-myadsinactive'),
    path('myrequestspending/', views.myrequestspending, name='stuffsharing-myrequestspending'),
    path('myrequestsaccepted/', views.myrequestsaccepted, name='stuffsharing-myrequestsaccepted'),
    path('about/', views.about, name='stuffsharing-about'),
    path('myaccount/', views.myaccount, name='stuffsharing-myaccount'),
    path('signup/',views.signup,name='stuffsharing-signup'),
    path('mystats/',views.mystats,name='stuffsharing-mystats'),
]
