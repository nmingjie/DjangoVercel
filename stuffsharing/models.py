from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
# Create your models here.


#Profile entity
class Profile(models.Model): 	
	user = models.OneToOneField(User, on_delete=models.CASCADE) #Connected to User entity
	Name = models.CharField(max_length=255,unique=False)
	phone = models.CharField(max_length=12)
	address= models.CharField(max_length=1000,default='')

#Stuff entity
class Stuff(models.Model):
	name=models.CharField(max_length=255,default='')
	owner=models.ForeignKey(Profile,to_field='user_id',on_delete=models.CASCADE) #Foreign key connected on user_id
	description=models.CharField(max_length=255,default='')
	tags=models.CharField(max_length=1000,default='')
	image=models.CharField(max_length=1000,default='') #Path where the image is stored

#LoanProposition entity
class LoanProposition(models.Model):
	owner=models.ForeignKey(Profile,to_field='user_id',on_delete=models.CASCADE,default='')
	stuff_for_lown=models.ForeignKey(Stuff,on_delete=models.CASCADE) #Connected to Stuff on stuff_id
	start_date=models.DateField('Data available')
	end_date=models.DateField('Data end return')
	price=models.FloatField(default=0.0)
	pickupAdress=models.CharField(max_length=1000,default='')
	returnAdress=models.CharField(max_length=1000,default='')
	available=models.BooleanField(default=True)
	
#LoanRequest entity
class LoanRequest(models.Model):
    original_Proposition = models.ForeignKey(LoanProposition, on_delete=models.CASCADE) #Connected to Loan on LoanProposition_id
    borrower = models.ForeignKey(Profile,to_field='user_id', on_delete=models.CASCADE) #Connected to Profile on user_id
    accepted=models.BooleanField(default=False)
    price=models.FloatField()
    