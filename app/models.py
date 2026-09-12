from django.db import models
from django.conf import settings
from django.urls import reverse


class Company(models.Model):
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='company',
        verbose_name="Owner",
    )
    name = models.CharField(max_length=150, verbose_name="Company name")
    slug = models.SlugField(max_length=150, unique=True)
    description = models.TextField(blank=True, verbose_name="Description")
    logo = models.ImageField(upload_to='companies/', blank=True, null=True, verbose_name="Logo")
    is_single = models.BooleanField(default=True, verbose_name="Solo seller")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("app:company_detail", args=[self.slug])

    def is_member(self, user):
        if not user.is_authenticated:
            return False
        if user_id := getattr(user, 'id', None):
            if self.owner_id == user_id:
                return True
        return self.members.filter(user=user).exists()


class CompanyMember(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='company_memberships')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('company', 'user')

    def __str__(self):
        return f"{self.user} @ {self.company}"


class SellerApplication(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'На розгляді'),
        (STATUS_APPROVED, 'Схвалено'),
        (STATUS_REJECTED, 'Відхилено'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='seller_applications',
    )
    company_name = models.CharField(max_length=150, verbose_name="Proposed company name")
    message = models.TextField(verbose_name="Why do you want to sell?")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='reviewed_applications',
    )
    review_note = models.TextField(blank=True, verbose_name="Reviewer note")
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Seller application"
        verbose_name_plural = "Seller applications"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} -> {self.company_name} ({self.status})"


class Category(models.Model):
    name = models.CharField(max_length=50, db_index=True)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("app:product_list_by_category", args=[self.slug])


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="Category")
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='products', verbose_name="Company",
        null=True, blank=True,
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL Slug")
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True, verbose_name="Image")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    views = models.IntegerField(default=0, verbose_name="Views")

    def __str__(self):
        return f"{self.name} ({self.created_at:%Y-%m-%d})"

    def get_absolute_url(self):
        return reverse("app:product_detail", args=[self.id, self.slug])


class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='product_comments')
    body = models.TextField(verbose_name="Comment")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.author} on {self.product}"


class Proposition(models.Model):
    STATUS_OPEN = 'open'
    STATUS_APPROVED = 'approved'
    STATUS_DECLINED = 'declined'
    STATUS_CHOICES = [
        (STATUS_OPEN, 'Відкрито'),
        (STATUS_APPROVED, 'Схвалено'),
        (STATUS_DECLINED, 'Відхилено'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='propositions')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='propositions')
    title = models.CharField(max_length=150)
    body = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_OPEN)
    decision_note = models.TextField(blank=True, verbose_name="Owner's explanation")
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['company', 'title'], name='unique_proposition_title_per_company'),
        ]

    def __str__(self):
        return f"{self.title} @ {self.company}"


class PropositionComment(models.Model):
    proposition = models.ForeignKey(Proposition, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='proposition_comments')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.author} on {self.proposition}"


class SiteAnnouncement(models.Model):
    """Platform-wide news: maintenance windows, feature changes, etc."""
    title = models.CharField(max_length=200)
    body = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='announcements',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Notification(models.Model):
    CATEGORY_COMPANY = 'company'
    CATEGORY_ADMIN = 'admin'
    CATEGORY_CHOICES = [
        (CATEGORY_COMPANY, 'Компанія'),
        (CATEGORY_ADMIN, 'Від адміністрації'),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications',
    )
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    url = models.CharField(max_length=300, blank=True, verbose_name="Link (relative URL)")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.category}] {self.title} -> {self.recipient}"