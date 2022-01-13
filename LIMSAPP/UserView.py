from .forms import SignUpForm, EditProfileForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth import authenticate, login, logout



def user_login(request):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			messages.success(request, ('You have been Logged In!'))
			return redirect('home')
		else:
			messages.success(request, ('Error Logging In - Please Try Again...'))
			return redirect('user_login')
	else:
		return render(request, 'authenticate/login.html', {})

def logout_user(request):
	logout(request)
	messages.success(request, ('You have been logged out...'))
	return redirect ('home')


def register_user(request):
	if request.method == 'POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data['username']
			password = form.cleaned_data['password1']
			user = authenticate(username=username, password=password)
			login(request,user)
			messages.success(request, ('Register Successful...'))
			return redirect('home')

	else:
		form = SignUpForm()
	context = {'form': form}
	return render(request, 'authenticate/register.html', context)

def edit_profile(request):
	if request.method == 'POST':
		form = EditProfileForm(request.POST, instance=request.user)
		if form.is_valid():
			form.save()
			messages.success(request, ('Edit Successful...'))
			return redirect('home')

	else:
		form = EditProfileForm(instance=request.user)
	context = {'form': form}
	return render(request, 'authenticate/edit_profile.html', context)

def change_password(request):
	if request.method == 'POST':
		form = PasswordChangeForm(data=request.POST, user=request.user)
		if form.is_valid():
			form.save()
			#Save session so users don't have to re log in but might not want to put it in so users can remember their password by relogging in
			#update_session_auth_hash(request, form.user)
			messages.success(request, ('Password Change Successful...'))
			return redirect('home')

	else:
		form = PasswordChangeForm(user=request.user)
	context = {'form': form}
	return render(request, 'authenticate/change_password.html', context)