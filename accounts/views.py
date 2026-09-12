from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from app.models import Category, Proposition, SellerApplication
from .forms import UserEditForm, ProfileEditForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('app:product_list')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('app:product_list')
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('app:product_list')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('app:product_list')
    else:
        form = UserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('app:product_list')


@login_required
def profile_view(request):
    categories = Category.objects.all()
    company = getattr(request.user, 'company', None)

    open_propositions = None
    if company is not None:
        open_propositions = company.propositions.filter(
            status=Proposition.STATUS_OPEN
        ).select_related('author')[:10]

    pending_application = request.user.seller_applications.filter(
        status=SellerApplication.STATUS_PENDING
    ).first()
    approved_unclaimed_application = request.user.seller_applications.filter(
        status=SellerApplication.STATUS_APPROVED
    ).first() if company is None else None

    context = {
        'categories': categories,
        'company': company,
        'open_propositions': open_propositions,
        'pending_application': pending_application,
        'approved_unclaimed_application': approved_unclaimed_application,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def profile_edit(request):
    categories = Category.objects.all()

    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=request.user)
        profile_form = ProfileEditForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Ваш профіль успішно оновлено!")
            return redirect('accounts:profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)

    return render(request, 'accounts/profile_edit.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'categories': categories,
        'title': 'Редагування профілю',
    })