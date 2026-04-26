from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User,
    Vendor,
    Category,
    product,
    Address,
    Cart,
    CartItem,
    Order,
    OrderItem,
    Payment,
    Review,
    VendorPayout,
    Notification,
)

# ---------------------------
# CUSTOM USER ADMIN
# ---------------------------
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "is_verified", "is_staff")
    list_filter = ("role", "is_verified", "is_staff")
    search_fields = ("username", "email")
    fieldsets = UserAdmin.fieldsets + (
        ("Marketplace Info", {
            "fields": ("role", "phone", "is_verified")
        }),
    )

admin.site.register(User, CustomUserAdmin)

# ---------------------------
# VENDOR ADMIN
# ---------------------------
class VendorAdmin(admin.ModelAdmin):
    list_display = ("shop_name", "user", "is_approved", "created_at")
    list_filter = ("is_approved",)
    search_fields = ("shop_name", "user__username")

admin.site.register(Vendor, VendorAdmin)

# ---------------------------
# CATEGORY ADMIN
# ---------------------------
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)

admin.site.register(Category, CategoryAdmin)

# ---------------------------
# PRODUCT ADMIN
# ---------------------------
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "vendor", "price", "stock", "is_active", "created_at")
    list_filter = ("is_active", "category")
    search_fields = ("name",)
    list_editable = ("price", "stock", "is_active")

admin.site.register(product, ProductAdmin)

# ---------------------------
# ADDRESS ADMIN
# ---------------------------
class AddressAdmin(admin.ModelAdmin):
    list_display = ("full_name", "user", "city", "state", "country")
    search_fields = ("full_name", "user__username", "city")

admin.site.register(Address, AddressAdmin)

# ---------------------------
# CART ADMIN
# ---------------------------
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at")

admin.site.register(Cart, CartAdmin)

# ---------------------------
# CART ITEM ADMIN
# ---------------------------
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "product", "quantity")

admin.site.register(CartItem, CartItemAdmin)

# ---------------------------
# ORDER ADMIN
# ---------------------------
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "buyer", "status", "total_price", "created_at")
    list_filter = ("status",)
    search_fields = ("buyer__username",)

admin.site.register(Order, OrderAdmin)

# ---------------------------
# ORDER ITEM ADMIN
# ---------------------------
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "vendor", "quantity", "price")

admin.site.register(OrderItem, OrderItemAdmin)

# ---------------------------
# PAYMENT ADMIN
# ---------------------------
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("transaction_id", "order", "payment_method", "amount", "paid")
    list_filter = ("payment_method", "paid")
    search_fields = ("transaction_id",)

admin.site.register(Payment, PaymentAdmin)

# ---------------------------
# REVIEW ADMIN
# ---------------------------
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "created_at")
    list_filter = ("rating",)

admin.site.register(Review, ReviewAdmin)

# ---------------------------
# VENDOR PAYOUT ADMIN
# ---------------------------
class VendorPayoutAdmin(admin.ModelAdmin):
    list_display = ("vendor", "amount", "paid", "payout_date")
    list_filter = ("paid",)

admin.site.register(VendorPayout, VendorPayoutAdmin)

# ---------------------------
# NOTIFICATION ADMIN
# ---------------------------
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "notification_type", "is_read", "created_at")
    list_filter = ("notification_type", "is_read")

admin.site.register(Notification, NotificationAdmin)
