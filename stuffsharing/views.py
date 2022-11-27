from django.shortcuts import render,redirect
from stuffsharing.models import  Profile, Stuff, LoanProposition, LoanRequest
from .forms import SearchForm
from .forms import SignUpForm
from .forms import UserProfileInfoForm
from .forms import MyAdsAddForm
from .forms import MyAdsInactiveForm
from .forms import MyAdsActiveBidForm
from .forms import MyAdsActiveAdForm
from .forms import BidForm
from django.db import connection
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import uuid
from django.contrib.auth import login, authenticate
import os
from django.core.files.base import ContentFile
from django.contrib import messages
import datetime

##################All the views#####################
@csrf_protect
#Home page
def home(request):
	if request.method=='POST':
		#Submit request
		if 'submitRequest' in request.POST:
			if request.user.is_authenticated:
				borrow=request.user.profile
				form=BidForm(request.POST)
				if form.is_valid():
					prop_id = form.cleaned_data['loan_prop_id']
					bid_price = form.cleaned_data['price']
					origin_prop = LoanProposition.objects.raw('SELECT * FROM stuffsharing_LoanProposition WHERE id = %s', [prop_id])[0]
					already_requested = LoanProposition.objects.raw("SELECT * FROM stuffsharing_loanRequest LR WHERE LR.borrower_id = %s AND LR.original_proposition_id = %s", [borrow.user_id, origin_prop.id])
 
					if bid_price == None:
						message='Please put a price'
						return render(request, 'stuffsharing/error.html',{'message':message})

					else:
						if bid_price < 0:
							message='Please put a positive price'
							return render(request, 'stuffsharing/error.html',{'message':message})

						else:
							if len(already_requested) > 0:
								message='You have already requested this item'
								return render(request, 'stuffsharing/error.html',{'message':message})

							else: 
								newreq = LoanRequest(original_Proposition=origin_prop,borrower=borrow,price=bid_price)
								newreq.save()
								return redirect('/myrequestspending/')
				
				form=SearchForm()
				return render(request, 'stuffsharing/home.html', {'form': form})
		else:
			#Search request
			form=SearchForm(request.POST)
			if form.is_valid():
				search='%'+form.cleaned_data['search']+'%'
				query=LoanProposition.objects.raw('SELECT * FROM stuffsharing_LoanProposition L join stuffsharing_Stuff S on L.stuff_for_lown_id=S.id WHERE S.tags LIKE %s AND L.available = 1 ORDER BY L.price', [search])
				result=[i for i in query]

				if len(result)!=0:
					propositions=[]
					for proposition in result:
						if proposition.available:
							propositions.append((proposition, BidForm(initial={'loan_prop_id':proposition.id})))
					return render(request, 'stuffsharing/search.html', {'form': form,'propositions':propositions})
	else:
		form=SearchForm()
	return render(request, 'stuffsharing/home.html', {'form': form})

#Search page (almost the same as home page)
@csrf_protect
def search(request):
	if request.method=='POST':
		#Submit request
		if 'submitRequest' in request.POST:
			if request.user.is_authenticated:
				borrow=request.user.profile
				form=BidForm(request.POST)
				if form.is_valid():
					prop_id = form.cleaned_data['loan_prop_id']
					bid_price = form.cleaned_data['price']
					origin_prop = LoanProposition.objects.raw('SELECT * FROM stuffsharing_LoanProposition WHERE id = %s', [prop_id])[0]
					already_requested = LoanProposition.objects.raw("SELECT * FROM stuffsharing_loanRequest LR WHERE LR.borrower_id = %s AND LR.original_proposition_id = %s", [borrow.user_id, origin_prop.id])
 
					if bid_price == None:
						message='Please put a price'
						return render(request, 'stuffsharing/error.html',{'message':message})

					else:
						if bid_price < 0:
							message='Please put a positive price'
							return render(request, 'stuffsharing/error.html',{'message':message})

						else:
							if len(already_requested) > 0:
								message='You have already requested this item'
								return render(request, 'stuffsharing/error.html',{'message':message})

							else: 
								newreq = LoanRequest(original_Proposition=origin_prop,borrower=borrow,price=bid_price)
								newreq.save()
								return redirect('/myrequestspending/')
				
				form=SearchForm()
				return render(request, 'stuffsharing/search.html', {'form': form})
		else:
			#Search request
			form=SearchForm(request.POST)
			if form.is_valid():
				search='%'+form.cleaned_data['search']+'%'
				query=LoanProposition.objects.raw('SELECT * FROM stuffsharing_LoanProposition L join stuffsharing_Stuff S on L.stuff_for_lown_id=S.id WHERE S.tags LIKE %s AND L.available = 1 ORDER BY L.price', [search])
				result=[i for i in query]

				if len(result)!=0:
					propositions=[]
					for proposition in result:
						if proposition.available:
							propositions.append((proposition, BidForm(initial={'loan_prop_id':proposition.id})))
					return render(request, 'stuffsharing/search.html', {'form': form,'propositions':propositions})
	else:
		form=SearchForm()
	return render(request, 'stuffsharing/search.html', {'form': form})

#Adding a new stuff (add and stuff may be confusing here, it's a stuff that is added)
def myadsadd(request):
	if request.user.is_authenticated :
		if request.method=='POST':
			form=MyAdsAddForm(request.POST)
			if form.is_valid():
				name=form.cleaned_data['name']
				t=form.cleaned_data['tags']
				d=form.cleaned_data['description']
				o=request.user.profile
				s=Stuff(tags=t,description=d,owner=o,name=name)
				#Check if picture has been loaded.
				if 'myfile' in request.FILES:
					pic1=request.FILES['myfile']
					image_path='Storage/%s/'%(request.user.username)+name+str(pic1)[:-4]
					save_path = './stuffsharing/static/'+image_path
					
					print('path',save_path)
					directory = os.path.dirname(save_path)
					if not os.path.exists(directory):
						os.makedirs(directory)      

					fout = open(save_path, 'wb+')
					file_content = ContentFile( pic1.read() )
					for chunk in file_content.chunks():
						fout.write(chunk)
					s.image=image_path
				s.save()

	form=MyAdsAddForm()
	return render(request, 'stuffsharing/myadsadd.html', {'form': form})
#Active ads
def myadsactive(request):
	if request.user.is_authenticated :
		o=request.user.profile
		if request.method=='POST':
			if request.POST['submitter'] == 'remove':
				form=MyAdsActiveAdForm(request.POST)
				if form.is_valid():
					p_id = form.cleaned_data['loan_prop_id']
					with connection.cursor() as cursor:
						cursor.execute("DELETE FROM stuffsharing_loanproposition WHERE id = %s",[p_id])
			else:
				form=MyAdsActiveBidForm(request.POST)
				if form.is_valid():
					r_id = form.cleaned_data['loan_request_id']
					if form.cleaned_data['submitter']=='accept':
						lreq = LoanRequest.objects.raw('SELECT * FROM stuffsharing_loanrequest WHERE id = %s',[r_id])[0]
						lreq.accepted=True
						lreq.save()
						lprop = lreq.original_Proposition
						lprop.available=False
						lprop.save()
						
		
		propsList=LoanProposition.objects.raw("SELECT * FROM stuffsharing_loanproposition WHERE owner_id = %s ORDER BY available DESC",[o.user_id])
		if len(propsList) > 0:
			propsAndForms=[]
			for prop in propsList:
				lrequests=LoanRequest.objects.raw('SELECT * FROM stuffsharing_loanrequest WHERE original_proposition_id = %s ORDER BY price DESC LIMIT 5',[prop.id])
				reqAndForm=[]
				for req in lrequests:
					reqAndForm.append((req, MyAdsActiveBidForm(initial={'loan_request_id': req.id})))
				propsAndForms.append((prop, MyAdsActiveAdForm(initial={'loan_prop_id': prop.id}), reqAndForm))
			return render(request, 'stuffsharing/myadsactive.html', {'propsAndForms': propsAndForms})
		else:
			return render(request, 'stuffsharing/myadsactive.html')
	else:
		return render(request, 'stuffsharing/myadsactive.html')
#Inactive ads
def myadsinactive(request):
	if request.user.is_authenticated :
		o=request.user.profile
		if request.method=='POST':
			if request.POST['submitter']=='Delete':
				sid = request.POST['stuff_for_lown']
				with connection.cursor() as cursor:
					cursor.execute("DELETE FROM stuffsharing_stuff WHERE id = %s",[sid])
			else: 
				form=MyAdsInactiveForm(request.POST)
				if form.is_valid():
					sid = form.cleaned_data['stuff_for_lown']
					sdate = form.cleaned_data['start_date']
					edate = form.cleaned_data['end_date']
					pr=form.cleaned_data['price']
					paddr = form.cleaned_data['pickupAddress']
					raddr = form.cleaned_data['returnAddress']
					if sdate < edate:
						stuff = Stuff.objects.raw('SELECT * FROM stuffsharing_stuff WHERE id = %s',[sid])[0]
						newloanprop=LoanProposition(owner=o,stuff_for_lown=stuff, start_date=sdate,end_date=edate,price=pr,pickupAdress=paddr,returnAdress=raddr,available=True)
						newloanprop.save()
					else:
						message='The pick up date must be sooner than the return date.'
						return render(request, 'stuffsharing/error.html',{'message':message})
				
		inactiveStuff = Stuff.objects.raw('SELECT * from stuffsharing_stuff S WHERE owner_id = %s', [o.user_id])
		if len(inactiveStuff)!=0:
				propForms=[]
				for item in inactiveStuff:
					propForms.append((item, MyAdsInactiveForm(initial={'stuff_for_lown': item.id,'pickupAddress': o.address, 'returnAddress': o.address})))
				return render(request, 'stuffsharing/myadsinactive.html', {'formList': propForms})
				
	return render(request, 'stuffsharing/myadsinactive.html')
#About view
def about(request):
    return render(request, 'stuffsharing/about.html')
#Pending requests view
def myrequestspending(request):
	if request.user.is_authenticated :
		o=request.user.profile
		if request.method=='POST':
			form=MyAdsActiveBidForm(request.POST)
			if form.is_valid():
				r_id=form.cleaned_data['loan_request_id']
				with connection.cursor() as cursor:
					cursor.execute("DELETE FROM stuffsharing_loanrequest WHERE id = %s",[r_id])
		reqList=LoanRequest.objects.raw("SELECT * FROM stuffsharing_loanrequest R JOIN stuffsharing_LoanProposition P ON R.original_Proposition_id=P.id WHERE R.borrower_id = %s AND R.accepted = 0 AND P.available = 1",[o.user_id])
		reqAndForm=[]
		for req in reqList:
			reqAndForm.append((req,MyAdsActiveBidForm(initial={'loan_request_id': req.id})))
		return render(request, 'stuffsharing/myrequestspending.html',{'reqAndForm':reqAndForm})
	return render(request, 'stuffsharing/myrequestspending.html')

#Accepted requests view
def myrequestsaccepted(request): 
	if request.user.is_authenticated :
		o=request.user.profile
		reqList=LoanRequest.objects.raw("SELECT * FROM stuffsharing_loanrequest WHERE borrower_id = %s AND accepted = 1",[o.user_id])
		requests=[]
		for req in reqList:
			requests.append(req)
		return render(request, 'stuffsharing/myrequestsaccepted.html',{'requests':requests})
	return render(request, 'stuffsharing/myrequestsaccepted.html')

#My account view
def myaccount(request):
	return render(request, 'stuffsharing/myaccount.html')
#My stats view
def mystats(request):
	#User Profile
	profile=request.user.profile

	#Inactive ads
	query=Stuff.objects.raw("SELECT S.id from stuffsharing_stuff S WHERE S.owner_id = %s AND NOT EXISTS(SELECT 1 FROM stuffsharing_LoanProposition WHERE stuff_for_lown_id = S.id)",  [profile.user_id] )
	if len(query)>0:
		inactive_ads_result=len([i for i in query])
	else:
		inactive_ads_result=0
	#Active ads
	query=Stuff.objects.raw("SELECT LP.id FROM stuffsharing_LoanProposition LP WHERE LP.owner_id = %s",  [profile.user_id])
	if len(query)>0:
		active_ads_result=len([i for i in query])
	else:
		active_ads_result=0
	#Most frequent ads
	query = Stuff.objects.raw("SELECT * FROM stuffsharing_Stuff S WHERE S.owner_id = %s", [profile.user_id])
	if len(query)>0:
		tags_result=[i for i in query]
		repeated_tags=[]
		distinct_tags=[]
		for stuff in query:
			tab=stuff.tags.split(',')
			for word in tab:
				if word.lower() not in distinct_tags:
					distinct_tags.append(word.lower())
			repeated_tags+=tab
			limit=0
			most_used_tags=[]
			for tag in distinct_tags:
				nb=repeated_tags.count(tag)
				if nb > limit :
					limit = nb
					most_used_tags=[tag]
				elif nb == limit :
					most_used_tags.append(tag)
	else:
		most_used_tags=["You don't have any stuff"]
	#Average duration of the ads
	query= LoanProposition.objects.raw("SELECT id FROM stuffsharing_LoanProposition WHERE owner_id=%s" , [profile.user_id])
	if len(query)>0:
		all_durations=[(i.end_date-i.start_date) for i in query]
		sum=datetime.timedelta(microseconds=0)
		for date in all_durations:
			sum+=date
		average_duration=sum/len(all_durations)
	else:
		average_duration=0

	#Number of requests
	query=LoanProposition.objects.raw("SELECT * FROM stuffsharing_LoanRequest LR Join stuffsharing_LoanProposition LP on LR.original_Proposition_id = LP.id WHERE LP.owner_id=%s", [profile.user_id])
	if len(query)>0:
		number_requests=len([i for i in query])
	else:
		number_requests=0
	
	#Most used tags in requests
	query=Stuff.objects.raw("SELECT S.tags,S.id FROM stuffsharing_Stuff S, stuffsharing_LoanRequest LR, stuffsharing_LoanProposition LP WHERE S.id=LP.stuff_for_lown_id AND LP.id=LR.original_Proposition_id AND LR.borrower_id=%s", [profile.user_id])
	if len(query)>0:
		tags_result=[i for i in query]
		repeated_tags=[]
		distinct_tags=[]
		for stuff in query:
			tab=stuff.tags.split(',')
			for word in tab:
				if word.lower() not in distinct_tags:
					distinct_tags.append(word.lower())
			repeated_tags+=tab
			limit=0
			most_used_tags_requests=[]
			for tag in distinct_tags:
				nb=repeated_tags.count(tag)
				if nb > limit :
					limit = nb
					most_used_tags_requests=[tag]
				elif nb == limit :
					most_used_tags_requests.append(tag)
	else:
		most_used_tags_requests['You never had any loan request']
	#Average duration of the requests 
	query= LoanProposition.objects.raw("SELECT * FROM stuffsharing_LoanRequest LR WHERE LR.borrower_id=%s" , [profile.user_id])
	if len(query)>0:
		all_durations=[(i.end_date-i.start_date) for i in query]
		sum=datetime.timedelta(microseconds=0)
		for date in all_durations:
			sum+=date
		average_duration_requests=sum/len(all_durations)
	else:
		average_duration_requests=0

	return render(request, 'stuffsharing/mystats.html',{'inactive_ads':inactive_ads_result,'active_ads':active_ads_result,'freq_tags':most_used_tags,'average_duration':average_duration,'number_requests':number_requests,'freq_tags_req':most_used_tags_requests,'average_duration_request':average_duration_requests})

#Signup view
def signup(request):
    if request.method == 'POST':
		#user form 
        user_form = SignUpForm(request.POST)
		#profile form
        profile_form = UserProfileInfoForm(request.POST)
 
        if user_form.is_valid() and profile_form.is_valid() :
        
        	user = user_form.save()
        	user.save()
        	profile = profile_form.save(commit=False)
        	profile.user = user
        	profile.save()
        	registered = True
        	if registered : 
        		login(request, user)
        		return redirect('/')
    else:
        user_form = SignUpForm()
        profile_form = UserProfileInfoForm()
    return render(request, 'stuffsharing/signup.html', {'user_form': user_form,'profile_form':profile_form})



