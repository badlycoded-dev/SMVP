from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Product, Category, Company, CompanyMember, SellerApplication, Comment,
    Proposition, PropositionComment, Notification, SiteAnnouncement,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "price", "is_active", "image_tag")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "description")
    prepopulated_fields = {'slug': ('name',)}

    def image_tag(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return format_html('<span>немає зображення</span>')

    image_tag.short_description = "Зображення"


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner", "is_single", "created_at")
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ("name", "owner__username")


@admin.register(SellerApplication)
class SellerApplicationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "company_name", "status", "created_at", "reviewed_by")
    list_filter = ("status",)
    search_fields = ("user__username", "company_name")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "author", "created_at")
    search_fields = ("body",)


@admin.register(Proposition)
class PropositionAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "company", "author", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("title", "body")


@admin.register(PropositionComment)
class PropositionCommentAdmin(admin.ModelAdmin):
    list_display = ("id", "proposition", "author", "created_at")


@admin.register(CompanyMember)
class CompanyMemberAdmin(admin.ModelAdmin):
    list_display = ("id", "company", "user", "added_at")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "recipient", "category", "title", "is_read", "created_at")
    list_filter = ("category", "is_read")


@admin.register(SiteAnnouncement)
class SiteAnnouncementAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_by", "created_at")
