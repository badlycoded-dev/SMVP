from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F
from django.utils import timezone
from django.utils.text import slugify
from .models import (
    Product, Category, Company, CompanyMember, SellerApplication, Comment,
    Proposition, PropositionComment, Notification, SiteAnnouncement,
)
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.contrib.auth import get_user_model
from .forms import (
    ContactForm, SellerApplicationForm, SellerApplicationReviewForm, CompanyDetailsForm,
    CommentForm, PropositionForm, PropositionCommentForm, PropositionDecisionForm,
    AddMemberForm, AnnouncementForm,
)
from .cart import Cart
from .notifications import notify
from django.views.decorators.http import require_POST


def _send_contact_message(request, form, template_name, title, success_redirect):
    """Shared handling for the contact and support forms."""
    if request.method == 'POST':
        form = form.__class__(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            subject = f"Нове повідомлення: {data['subject']}"
            body = (
                f"Ім'я: {data['name']}\n"
                f"Email: {data['email']}\n\n"
                f"Повідомлення:\n{data['message']}"
            )
            try:
                send_mail(
                    subject,
                    body,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.ADMIN_EMAIL],
                    fail_silently=False,
                )
                messages.success(request, "Ваше повідомлення успішно надіслано!")
                return redirect(success_redirect)
            except Exception:
                messages.error(request, "Сталася помилка при надсиланні листа. Спробуйте пізніше.")
    else:
        form = form.__class__()

    categories = Category.objects.all()
    return render(request, template_name, {
        'form': form,
        'categories': categories,
        'title': title,
    })


def contact_view(request):
    return _send_contact_message(request, ContactForm(), 'app/contact.html', 'Контакти', 'app:contact')


def support_view(request):
    return _send_contact_message(request, ContactForm(), 'app/support.html', 'Support', 'app:support')


def product_list(request, category_slug=None):
    products = Product.objects.select_related('category', 'company').filter(is_active=True)
    categories = Category.objects.all()
    category = None

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    sort = request.GET.get('sort', 'new')
    if sort == 'old':
        products = products.order_by('created_at')
    elif sort == 'popular':
        products = products.order_by('-views', '-created_at')
    elif sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'company':
        products = products.order_by('company__name', '-created_at')
    else:
        products = products.order_by('-created_at')

    context = {
        "title": f"Категорія: {category.name}" if category else "Каталог товарів",
        "categories": categories,
        "category": category,
        "products": products,
        "current_sort": sort,
    }
    return render(request, "app/product_list.html", context)


def product_detail(request, id, slug):
    product = get_object_or_404(
        Product.objects.select_related('category', 'company'),
        id=id,
        slug=slug,
        is_active=True
    )

    Product.objects.filter(id=id).update(views=F('views') + 1)
    product.refresh_from_db(fields=['views'])

    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id).select_related('category')[:4]

    comments = product.comments.select_related('author')
    comment_form = CommentForm()
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Увійдіть, щоб залишити коментар.")
            return redirect('accounts:login')
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.product = product
            comment.author = request.user
            comment.save()
            return redirect('app:product_detail', id=product.id, slug=product.slug)

    context = {
        "title": product.name,
        "product": product,
        "related_products": related_products,
        "comments": comments,
        "comment_form": comment_form,
    }
    return render(request, "app/product_detail.html", context)


@login_required
def product_create(request):
    company = getattr(request.user, 'company', None)
    if company is None:
        messages.error(request, "Тільки схвалені продавці можуть додавати товари.")
        return redirect('app:seller_apply')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        category_id = request.POST.get('category')
        description = request.POST.get('description', '').strip()
        price = request.POST.get('price')
        image = request.FILES.get('image')

        if name and category_id and description and price:
            category = get_object_or_404(Category, id=category_id)
            slug = slugify(name)
            base_slug, i = slug, 1
            while Product.objects.filter(slug=slug).exists():
                i += 1
                slug = f"{base_slug}-{i}"

            product = Product.objects.create(
                category=category, company=company, name=name, slug=slug,
                description=description, price=price, image=image,
            )
            messages.success(request, "Товар додано!")
            return redirect(product.get_absolute_url())
        messages.error(request, "Заповніть усі обов'язкові поля.")

    categories = Category.objects.all()
    return render(request, 'app/product_form.html', {
        'title': 'Додати товар', 'categories': categories,
    })

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    override_quantity = request.POST.get('override', False)
    cart.add(product=product, quantity=quantity, override_quantity=bool(override_quantity))
    return redirect('app:cart_detail')
 
 
@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('app:cart_detail')
 
 
def cart_detail(request):
    cart = Cart(request)
    return render(request, 'app/cart_detail.html', {'cart': cart, 'title': 'Кошик'})


# ---------- Seller application ----------

@login_required
def seller_apply(request):
    if hasattr(request.user, 'company'):
        messages.info(request, "Ви вже є продавцем.")
        return redirect('accounts:profile')

    existing = request.user.seller_applications.filter(status=SellerApplication.STATUS_PENDING).first()
    if existing:
        messages.info(request, "Ваша заявка вже на розгляді.")
        return redirect('accounts:profile')

    if request.method == 'POST':
        form = SellerApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            messages.success(request, "Заявку надіслано на розгляд.")
            return redirect('accounts:profile')
    else:
        form = SellerApplicationForm()

    return render(request, 'app/seller_apply.html', {'form': form, 'title': 'Стати продавцем'})


@login_required
def company_setup(request, application_id):
    """Filled in by the applicant right after their application is approved."""
    application = get_object_or_404(
        SellerApplication, id=application_id, user=request.user, status=SellerApplication.STATUS_APPROVED,
    )
    if hasattr(request.user, 'company'):
        return redirect('accounts:profile')

    if request.method == 'POST':
        form = CompanyDetailsForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.save(commit=False)
            company.owner = request.user
            company.save()
            messages.success(request, "Компанію створено!")
            return redirect('accounts:profile')
    else:
        form = CompanyDetailsForm(initial={'name': application.company_name, 'slug': slugify(application.company_name)})

    return render(request, 'app/company_setup.html', {'form': form, 'title': 'Налаштування компанії'})


def company_detail(request, slug):
    company = get_object_or_404(Company, slug=slug)
    products = company.products.filter(is_active=True)
    propositions = company.propositions.select_related('author')
    return render(request, 'app/company_detail.html', {
        'title': company.name,
        'company': company,
        'products': products,
        'propositions': propositions,
    })


# ---------- Propositions ----------

@login_required
def proposition_create(request, slug):
    company = get_object_or_404(Company, slug=slug)
    if request.method == 'POST':
        form = PropositionForm(request.POST)
        if form.is_valid():
            proposition = form.save(commit=False)
            proposition.company = company
            proposition.author = request.user
            try:
                proposition.save()
                notify(
                    company.owner, Notification.CATEGORY_COMPANY,
                    f"Нова пропозиція: {proposition.title}",
                    f"{request.user.username} залишив(ла) нову пропозицію для {company.name}.",
                    reverse_proposition_url(company, proposition),
                )
                messages.success(request, "Пропозицію додано!")
                return redirect('app:proposition_detail', slug=company.slug, pk=proposition.pk)
            except Exception:
                messages.error(request, "Пропозиція з такою темою для цієї компанії вже існує.")
    else:
        form = PropositionForm()

    return render(request, 'app/proposition_form.html', {
        'form': form, 'company': company, 'title': 'Нова пропозиція',
    })


def proposition_detail(request, slug, pk):
    company = get_object_or_404(Company, slug=slug)
    proposition = get_object_or_404(Proposition, pk=pk, company=company)
    comments = proposition.comments.select_related('author')
    comment_form = PropositionCommentForm()
    is_owner = request.user.is_authenticated and request.user == company.owner
    is_member = request.user.is_authenticated and company.is_member(request.user)

    if request.method == 'POST' and 'body' in request.POST:
        if not request.user.is_authenticated:
            messages.error(request, "Увійдіть, щоб коментувати.")
            return redirect('accounts:login')
        comment_form = PropositionCommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.proposition = proposition
            comment.author = request.user
            comment.save()
            if request.user != proposition.author:
                notify(
                    proposition.author, Notification.CATEGORY_COMPANY,
                    f"Нова відповідь на \"{proposition.title}\"",
                    f"{request.user.username} відповів(ла) на вашу пропозицію.",
                    reverse_proposition_url(company, proposition),
                )
            if request.user != company.owner:
                notify(
                    company.owner, Notification.CATEGORY_COMPANY,
                    f"Новий коментар до \"{proposition.title}\"",
                    f"{request.user.username} залишив(ла) коментар.",
                    reverse_proposition_url(company, proposition),
                )
            return redirect('app:proposition_detail', slug=company.slug, pk=proposition.pk)

    decision_form = PropositionDecisionForm() if is_owner and proposition.status == Proposition.STATUS_OPEN else None

    return render(request, 'app/proposition_detail.html', {
        'title': proposition.title,
        'company': company,
        'proposition': proposition,
        'comments': comments,
        'comment_form': comment_form,
        'decision_form': decision_form,
        'is_owner': is_owner,
        'is_member': is_member,
    })


def reverse_proposition_url(company, proposition):
    return reverse('app:proposition_detail', args=[company.slug, proposition.pk])


@login_required
@require_POST
def proposition_decide(request, slug, pk):
    company = get_object_or_404(Company, slug=slug, owner=request.user)
    proposition = get_object_or_404(Proposition, pk=pk, company=company, status=Proposition.STATUS_OPEN)

    form = PropositionDecisionForm(request.POST)
    if form.is_valid():
        proposition.status = form.cleaned_data['status']
        proposition.decision_note = form.cleaned_data['decision_note']
        proposition.closed_at = timezone.now()
        proposition.save()
        notify(
            proposition.author, Notification.CATEGORY_COMPANY,
            f"Рішення щодо \"{proposition.title}\": {proposition.get_status_display()}",
            proposition.decision_note,
            reverse_proposition_url(company, proposition),
        )
        messages.success(request, "Рішення збережено.")

    return redirect('app:proposition_detail', slug=company.slug, pk=proposition.pk)


# ---------- Manager/admin review of seller applications ----------

@user_passes_test(lambda u: u.is_staff)
def application_review_list(request):
    applications = SellerApplication.objects.select_related('user').filter(
        status=SellerApplication.STATUS_PENDING
    )
    return render(request, 'app/application_review_list.html', {
        'title': 'Заявки на продаж', 'applications': applications,
    })


@user_passes_test(lambda u: u.is_staff)
def application_review_detail(request, application_id):
    application = get_object_or_404(SellerApplication, id=application_id)

    if request.method == 'POST':
        form = SellerApplicationReviewForm(request.POST)
        if form.is_valid() and application.status == SellerApplication.STATUS_PENDING:
            action = form.cleaned_data['action']
            application.status = (
                SellerApplication.STATUS_APPROVED if action == 'approve' else SellerApplication.STATUS_REJECTED
            )
            application.review_note = form.cleaned_data['review_note']
            application.reviewed_by = request.user
            application.reviewed_at = timezone.now()
            application.save()
            notify(
                application.user, Notification.CATEGORY_ADMIN,
                f"Заявку на продаж {application.get_status_display().lower()}",
                application.review_note,
                '/sell/setup/' + str(application.id) + '/' if application.status == SellerApplication.STATUS_APPROVED else '',
            )
            messages.success(request, "Рішення збережено.")
            return redirect('app:application_review_list')
    else:
        form = SellerApplicationReviewForm()

    return render(request, 'app/application_review_detail.html', {
        'title': 'Розгляд заявки', 'application': application, 'form': form,
    })


# ---------- Company members ----------

@login_required
def company_members(request, slug):
    company = get_object_or_404(Company, slug=slug, owner=request.user)

    if request.method == 'POST':
        if 'remove_member_id' in request.POST:
            CompanyMember.objects.filter(company=company, id=request.POST['remove_member_id']).delete()
            messages.success(request, "Учасника видалено.")
            return redirect('app:company_members', slug=company.slug)

        form = AddMemberForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['username']
            if user == company.owner:
                messages.error(request, "Ви вже власник компанії.")
            elif CompanyMember.objects.filter(company=company, user=user).exists():
                messages.error(request, "Цей користувач вже є учасником.")
            else:
                CompanyMember.objects.create(company=company, user=user)
                messages.success(request, f"{user.username} додано до команди.")
                return redirect('app:company_members', slug=company.slug)
    else:
        form = AddMemberForm()

    return render(request, 'app/company_members.html', {
        'title': 'Команда компанії', 'company': company, 'form': form,
        'members': company.members.select_related('user'),
    })


# ---------- Notifications ----------

@login_required
def notification_list(request):
    category = request.GET.get('tab', 'company')
    if category not in (Notification.CATEGORY_COMPANY, Notification.CATEGORY_ADMIN):
        category = Notification.CATEGORY_COMPANY

    notifications = request.user.notifications.filter(category=category)
    request.user.notifications.filter(category=category, is_read=False).update(is_read=True)

    announcements = SiteAnnouncement.objects.all()[:10] if category == Notification.CATEGORY_ADMIN else None

    return render(request, 'app/notification_list.html', {
        'title': 'Сповіщення',
        'notifications': notifications,
        'announcements': announcements,
        'active_tab': category,
    })


# ---------- Site announcements (staff) ----------

@user_passes_test(lambda u: u.is_staff)
def announcement_create(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.created_by = request.user
            announcement.save()

            User = get_user_model()
            for user in User.objects.filter(is_active=True):
                notify(
                    user, Notification.CATEGORY_ADMIN, announcement.title, announcement.body,
                    '',
                )
            messages.success(request, "Оголошення надіслано всім користувачам.")
            return redirect('app:announcement_create')
    else:
        form = AnnouncementForm()

    return render(request, 'app/announcement_form.html', {
        'title': 'Нове оголошення', 'form': form,
    })