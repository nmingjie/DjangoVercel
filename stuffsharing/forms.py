from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from stuffsharing.models import Profile

#Form used for signing up, the classs UserCreationForm has pre-established fields
class SignUpForm(UserCreationForm):
  
    class Meta:
		#Django recognize which fields to display from the model
        model = User
		#Fields of the form
        fields = ('username','email')
       
class UserProfileInfoForm(forms.ModelForm):

     class Meta():
         model = Profile
         fields = ('Name','phone','address')

class SearchForm(forms.Form):
	search=forms.CharField(max_length=30,widget=forms.TextInput(attrs={'class': "form-control form-control-lg form-control-borderless",'type':"Search",'placeholder':"Search stuffs or keywords"}))

class BidForm(forms.Form):
	price=forms.FloatField(label = 'Bidding price:', required=False)
	loan_prop_id=forms.IntegerField()
	submitRequest=forms.CharField()
	
class MyAdsAddForm(forms.Form):
	tags = forms.CharField(label = 'Item tags:', max_length=1000,widget=forms.TextInput(attrs={'class': "form-control",'type':"Name",'placeholder':"tag1,tag2,..."}))
	name=forms.CharField(label = 'Item name:', max_length=1000,widget=forms.TextInput(attrs={'class': "form-control",'type':"Name",'placeholder':"name"}))
	description = forms.CharField(label = 'Item Desctiption:', widget=forms.Textarea(attrs={'class': "form-control", 'rows':'3','type':"Description",'placeholder':"item description"}))
	
class MyAdsInactiveForm(forms.Form):
	stuff_for_lown=forms.IntegerField()
	start_date=forms.DateField(label = 'Pick up date:',widget=forms.widgets.SelectDateWidget())
	end_date=forms.DateField(label = 'Return date:',widget=forms.widgets.SelectDateWidget())
	price=forms.FloatField(label = 'Price')
	pickupAddress=forms.CharField(label='Address',max_length=255)
	returnAddress=forms.CharField(label='Address',max_length=255)	
	selectType=forms.ChoiceField(label='Selection', choices=[('auto','automatic'),('manual','manual')], widget=forms.RadioSelect)
	submitter=forms.CharField()

class MyAdsActiveBidForm(forms.Form):
	loan_request_id=forms.IntegerField()
	submitter=forms.CharField()

class MyAdsActiveAdForm(forms.Form):
	loan_prop_id=forms.IntegerField()
	submitter=forms.CharField()