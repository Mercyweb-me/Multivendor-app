from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    ROLE_CHOICES = (
        ("buyer", "Buyer"),
        ("vendor", "Vendor"),
        ("admin", "Admin"),
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default="buyer"
    )

    phone = models.CharField(max_length=15, blank=True)
    is_verified = models.BooleanField(default=False)
   

    def __str__(self):
        return self.username


   # --------------------
# VENDOR STORE
# --------------------
class Vendor(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    shop_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to="vendors/", blank=True)

    is_approved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.shop_name


#----------
# #PRODUCT CATEGORY
# ---------
class Category(models.Model):

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


#------------
#PRODUCT
#------------
class product(models.Model):

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete= models.SET_NULL, null=True)

    name = models.CharField(max_length=260)
    description = models.TextField()

    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    
    image = models.ImageField(upload_to="products/", blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name 


#------------
# SHIPPING ADDRESS
# ----------- 
class Address(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    full_name = models.CharField(max_length=260)
    phone = models.CharField(max_length=20)

    address = models.CharField(max_length=600)
    city = models.CharField(max_length=250)
    state = models.CharField(max_length=200)
    country = models.CharField(max_length=250)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.city}"


# --------------------
# CART
# --------------------
class Cart(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart {self.id}"


class CartItem(models.Model):

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)

    product = models.ForeignKey(product, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.product.name



#-----------
# ORDER
# ----------
class Order(models.Model):

    STATUS = (
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("shipping", "Shipping"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    )        

    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)

    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    status =models.CharField(max_length=20, choices=STATUS, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Order {self.id}"


# --------------------
# ORDER ITEMS
# --------------------
class OrderItem(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    product = models.ForeignKey(product, on_delete=models.CASCADE)

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)

    quantity = models.IntegerField()

    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.product.name



# --------------------
# PAYMENT
# --------------------
class Payment(models.Model):

    PAYMENT_METHOD = (
        ("paystack", "Paystack"),
        ("stripe", "Stripe"),
        ("paypal", "Paypal"),
    )

    order = models.OneToOneField(Order, on_delete=models.CASCADE)

    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD)

    transaction_id = models.CharField(max_length=255)

    amount = models.DecimalField(max_digits=12, decimal_places=2)

    paid = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.transaction_id



# --------------------
# PRODUCT REVIEW
# --------------------
class Review(models.Model):

    product = models.ForeignKey(product, on_delete=models.CASCADE)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    rating = models.IntegerField()

    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} review"




# --------------------
# VENDOR PAYOUT
# --------------------
class VendorPayout(models.Model):

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)

    amount = models.DecimalField(max_digits=12, decimal_places=2)

    paid = models.BooleanField(default=False)

    payout_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vendor.shop_name} payout"

#----------
#REAL TIME NOTIFICATIONS
#----------

class Notification(models.Model):

    NOTIFICATION_TYPES = (
        ("order", "Order Update"),
        ("payment", "Payment Update"),
        ("product", "Product Update"),
        ("system", "System Notification"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")

    title = models.CharField(max_length=255)
    message = models.TextField()

    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} notification"    




    
    
            
# Create your models here.
