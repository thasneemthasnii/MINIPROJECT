from django.contrib import admin
from django.urls import path

from marketplace import settings
from marketplace_app import views,admin_views,userviews

urlpatterns = [
    path('', views.home, name='home'),
    path('login_view/', views.login_view, name='login_view'),
    path('user_register/', views.user_register, name='user_register'),
    path('logout_view/', views.logout_view, name='logout_view'),


    path('admin_home/', admin_views.admin_home, name='admin_home'),
    path('category_add/', admin_views.category_add, name='category_add'),
    path('category/', admin_views.category, name='category'),
    path('category_update/<int:id>/', admin_views.category_update, name='category_update'),
    path('category_delete/<int:id>/', admin_views.category_delete, name='category_delete'),
    path('products_from_users/', admin_views.products_from_users, name='products_from_users'),
    path('approve_product/<int:id>/', admin_views.approve_product, name='approve_product'),
    path('reject_product/<int:id>/', admin_views.reject_product, name='reject_product'),
    path('approved_products/', admin_views.approved_products, name='approved_products'),
    path('feedback_admin/', admin_views.feedback_admin, name='feedback_admin'),
    path('orders_admin/', admin_views.orders_admin, name='orders_admin'),
    path('users_view/', admin_views.users_view, name='users_view'),
    path('user_delete/<int:user_id>/', admin_views.user_delete, name='user_delete'),
    path('payments/', admin_views.payments, name='payments'),

    path('user_home/', userviews.user_home, name='user_home'),
    path('detail_view/<int:id>/', userviews.detail_view, name='detail_view'),
    path('cart/', userviews.cart, name='cart'),
    path('add_to_cart/<int:id>/', userviews.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:id>/', userviews.remove_from_cart, name='remove_from_cart'),
    path('remove_single_item_from_cart/<int:id>/', userviews.remove_single_item_from_cart, name='remove_single_item_from_cart'),
    path('checkout/', userviews.checkout, name='checkout'),
    path('payment/', userviews.payment, name='payment'),
    path('order_status/', userviews.order_status, name='order_status'),
    path('add_feedback/', userviews.add_feedback, name='add_feedback'),
    path('item_add/', userviews.item_add, name='item_add'),
    path('update_item/<int:id>/', userviews.update_item, name='update_item'),
    path('delete_item/<int:id>/', userviews.delete_item, name='delete_item'),
    path('profile/', userviews.profile, name='profile'),
    path('update_profile/', userviews.update_profile, name='update_profile'),
    path('earnings/', userviews.earnings, name='earnings'),
    path('orders_seller/', userviews.orders_seller, name='orders_seller'),
    path('accept_order/<int:id>/', userviews.accept_order, name='accept_order'),
    path('complete_order/<int:id>/', userviews.complete_order, name='complete_order'),

]