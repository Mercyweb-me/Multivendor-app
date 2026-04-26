from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("register/",views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("login/", views.login_view, name="login"),
    path("products/", views.products_view, name="products"),
    path("product/<int:id>/", views.product_detail_view, name="product_detail"),
    path("cart/", views.cart_view, name="cart"),
    path("add-to-cart/<int:product_id>/", views.add_to_cart_view, name="add_to_cart"),
    path("remove-from-cart/<int:id>/", views.remove_from_cart, name="remove_from_cart"),
    path("checkout/", views.checkout_view, name="checkout"),
    path("approve-order/<int:id>/", views.approve_order_view, name="approve_order"),
    path("orders/", views.orders_view, name="orders"),
    path("settings/", views.settings_view, name="settings"),
    path("vendor-products/", views.vendor_products_view, name="vendor_products"),
    path("vendor-earnings/", views.vendor_earnings_view, name="vendor_earnings"),
    path("delete-product/<int:id>/", views.delete_product_view, name="delete_product"),
    path("edit-product/<int:id>/", views.edit_product_view, name="edit_product"),
    path("payment/<int:id>/", views.payment_view, name="payment"),
    path("post-product/", views.post_product_view, name="post_product"),
    path("notifications-check/", views.notifications_check, name="notifications_check"),
    path("notifications/", views.notifications_view, name="notifications"),
    path("notification-read/<int:id>/", views.mark_notification_read, name="notification_read"),
    path("orders/", views.order_history_view, name="orders"),
    path("payment-success/", views.payment_success, name="payment_success"),
    path("pay-order/<int:id>/", views.pay_order_view, name="pay_order"),
    path("edit-profile/", views.edit_profile_view, name="edit_profile"),
    path("change-email/", views.change_email_view, name="change_email"),
    path("change-password/", views.change_password_view, name="change_password"),
    # vendor
    # path("vendor/", views.vendor_dashboard_view, name="vendor_dashboard"),
    
]