from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    path('', views.product_list, name="product_list"),
    path('category/<slug:category_slug>/', views.product_list, name="product_list_by_category"),
    path('product/add/', views.product_create, name="product_create"),
    path('product/<int:id>/<slug:slug>/', views.product_detail, name="product_detail"),
    path('contact/', views.contact_view, name='contact'),
    path('support/', views.support_view, name='support'),
    path('cart/', views.cart_detail, name="cart_detail"),
    path('cart/add/<int:product_id>/', views.cart_add, name="cart_add"),
    path('cart/remove/<int:product_id>/', views.cart_remove, name="cart_remove"),

    # Seller onboarding
    path('sell/apply/', views.seller_apply, name="seller_apply"),
    path('sell/setup/<int:application_id>/', views.company_setup, name="company_setup"),
    path('company/<slug:slug>/', views.company_detail, name="company_detail"),
    path('company/<slug:slug>/members/', views.company_members, name="company_members"),

    # Propositions
    path('company/<slug:slug>/propositions/new/', views.proposition_create, name="proposition_create"),
    path('company/<slug:slug>/propositions/<int:pk>/', views.proposition_detail, name="proposition_detail"),
    path('company/<slug:slug>/propositions/<int:pk>/decide/', views.proposition_decide, name="proposition_decide"),

    # Manager review queue
    path('manage/applications/', views.application_review_list, name="application_review_list"),
    path('manage/applications/<int:application_id>/', views.application_review_detail, name="application_review_detail"),
    path('manage/announcements/new/', views.announcement_create, name="announcement_create"),

    # Notifications
    path('notifications/', views.notification_list, name="notification_list"),
]