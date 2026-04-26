from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.conf import settings
import requests
from .serializers import UserRegisterSerializer
from django.contrib.auth import authenticate, login, logout
from .models import product, Cart, CartItem, Order,  Vendor, Category, OrderItem, Notification, VendorPayout, Address
from django.http import JsonResponse


# HOME
def home_view(request):
    # If user is already authenticated, redirect to dashboard
    if request.user.is_authenticated:
        return redirect("dashboard")
    
    # Otherwise, show the landing page
    return render(request, "home.html")

# REGISTER VIEW
def register_view(request):

    if request.method == "POST":
        serializer = UserRegisterSerializer(data=request.POST)

        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, serializer.errors)

    return render(request, "register.html")


# LOGIN VIEW
def login_view(request):

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "login.html")


#PAY
def pay_order_view(request, id):

    order = Order.objects.get(id=id)

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "email": request.user.email,
        "amount": int(order.total_price * 100),
        "callback_url": "http://127.0.0.1:8000/payment-success/",
        "metadata": {
            "order_id": order.id
        }
    }

    response = requests.post(
        "https://api.paystack.co/transaction/initialize",
        json=data,
        headers=headers
    )

    res = response.json()

    # DEBUG PRINT
    print(res)

    if res.get("status") == True:
        return redirect(res["data"]["authorization_url"])
    else:
        messages.error(request, res.get("message"))
        return redirect("orders")


#pay suss
def payment_success(request):

    reference = request.GET.get("reference")

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
    }

    response = requests.get(
        f"https://api.paystack.co/transaction/verify/{reference}",
        headers=headers
    )

    res = response.json()

    if res["data"]["status"] == "success":
        order_id = res["data"]["metadata"]["order_id"]
        order = Order.objects.get(id=order_id)

        order.status = "paid"
        order.save()

    return redirect("orders")

#ORDER HISTORY
def order_history_view(request):

    if not request.user.is_authenticated:
        return redirect("login")

    orders = Order.objects.filter(
        buyer=request.user
    ).order_by("-created_at")

    context = {
        "orders": orders
    }

    return render(request, "order_history.html", context)




    # CART PAGE
def cart_view(request):

    if not request.user.is_authenticated:
        return redirect("login")

    cart, created = Cart.objects.get_or_create(user=request.user)

    items = CartItem.objects.filter(cart=cart)

    total = 0
    for item in items:
        total += item.product.price * item.quantity

    context = {
        "items": items,
        "total": total
    }

    return render(request, "cart.html", context)


# ADD TO CART
def add_to_cart_view(request, product_id):

    if not request.user.is_authenticated:
        return redirect("login")

    product_obj = get_object_or_404(product, id=product_id)

    # get or create cart
    cart, created = Cart.objects.get_or_create(user=request.user)

    # get or create cart item
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product_obj
    )

    # increase quantity if exists
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect("cart")

# REMOVE FROM CART
def remove_from_cart(request, id):

    item = CartItem.objects.get(id=id)
    item.delete()

    return redirect("cart")


# DASHBOARD
def dashboard_view(request):

    if not request.user.is_authenticated:
        return redirect("login")

    user = request.user

    # RECENT PRODUCTS
    products = product.objects.filter(is_active=True).order_by("-id")[:6]

    # ORDERS COUNT
    orders_count = Order.objects.filter(buyer=user).count()

    # CART COUNT
    cart_count = 0
    cart = Cart.objects.filter(user=user).first()
    if cart:
        cart_count = CartItem.objects.filter(cart=cart).count()

    # VENDOR DATA
    vendor_products = 0
    if user.role == "vendor":
        vendor = Vendor.objects.filter(user=user).first()
        if vendor:
            vendor_products = product.objects.filter(vendor=vendor).count()

    # NOTIFICATIONS
    notifications_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()

    context = {
        "products": products,
        "orders_count": orders_count,
        "cart_count": cart_count,
        "vendor_products": vendor_products,
        "notifications_count": notifications_count
    }

    return render(request, "dashboard.html", context)

    # ORDERS PAGE
def orders_view(request):

    if not request.user.is_authenticated:
        return redirect("login")

    user = request.user

    # BUYER ORDERS
    if user.role == "buyer":
        orders = Order.objects.filter(buyer=user).order_by("-created_at")

    # VENDOR ORDERS
    elif user.role == "vendor":
        vendor = Vendor.objects.filter(user=user).first()
        orders = OrderItem.objects.filter(vendor=vendor).order_by("-order__created_at")

    else:
        orders = Order.objects.all().order_by("-created_at")

    context = {
        "orders": orders
    }

    return render(request, "orders.html", context)

    # CHECKOUT
def checkout_view(request):

    if not request.user.is_authenticated:
        return redirect("login")

    cart = Cart.objects.filter(user=request.user).first()

    if not cart:
        messages.error(request, "Cart is empty")
        return redirect("cart")

    items = CartItem.objects.filter(cart=cart)

    total = 0
    for item in items:
        total += item.product.price * item.quantity

    if request.method == "POST":

        full_name = request.POST.get("full_name")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        city = request.POST.get("city")
        state = request.POST.get("state")
        country = request.POST.get("country")

        # create address
        addr = Address.objects.create(
            user=request.user,
            full_name=full_name,
            phone=phone,
            address=address,
            city=city,
            state=state,
            country=country
        )

        # create order
        order = Order.objects.create(
            buyer=request.user,
            address=addr,
            total_price=total
        )

        # create order items
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                vendor=item.product.vendor,
                quantity=item.quantity,
                price=item.product.price
            )
            
        Notification.objects.create(
        user=item.product.vendor.user,
        message=f"New order for {item.product.name}"
    )

        # clear cart
        items.delete()

        messages.success(request, "Order placed successfully")
        return redirect("dashboard")

    context = {
        "items": items,
        "total": total
    }

    return render(request, "checkout.html", context)

    #NOTIFICATIONS
def notifications_check(request):

    notif = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).order_by("-created_at").first()

    count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()

    if notif:
        return JsonResponse({
            "new": True,
            "message": notif.message,
            "count": count
        })

    return JsonResponse({
        "new": False,
        "count": count
    })

# POST PRODUCT
def post_product_view(request):

    if not request.user.is_authenticated:
        return redirect("login")

    if request.user.role != "vendor":
        return redirect("dashboard")

    vendor = Vendor.objects.filter(user=request.user).first()

    categories = Category.objects.all()

    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        price = request.POST.get("price")
        stock = request.POST.get("stock")
        category_id = request.POST.get("category")
        image = request.FILES.get("image")

        category = Category.objects.get(id=category_id)

        product.objects.create(
            vendor=vendor,
            category=category,
            name=name,
            description=description,
            price=price,
            stock=stock,
            image=image
        )

        messages.success(request, "Product posted successfully")
        return redirect("dashboard")

    context = {
        "categories": categories
    }

    return render(request, "post_product.html", context)


#PROFILE VIEW 
def profile_view(request):

    if not request.user.is_authenticated:
        return redirect("login")

    user = request.user

    orders = Order.objects.filter(buyer=user).order_by("-created_at")[:5]

    vendor = None
    if user.role == "vendor":
        vendor = Vendor.objects.filter(user=user).first()

    context = {
        "orders": orders,
        "vendor": vendor
    }

    return render(request, "profile.html", context)


   

# SETTINGS PAGE
def settings_view(request):

    if not request.user.is_authenticated:
        return redirect("login")

    user = request.user

    if request.method == "POST":
        user.username = request.POST.get("username")
        user.email = request.POST.get("email")

        password = request.POST.get("password")
        if password:
            user.password = make_password(password)

        user.save()

        messages.success(request, "Profile updated successfully")
        return redirect("profile")

    return render(request, "settings.html")


    # PRODUCT DETAIL
def product_detail_view(request, id):

    if not request.user.is_authenticated:
        return redirect("login")

    product_obj = product.objects.get(id=id)

    reviews = Review.objects.filter(product=product_obj)

    related_products = product.objects.filter(
        category=product_obj.category
    ).exclude(id=product_obj.id)[:4]

    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        Review.objects.create(
            product=product_obj,
            user=request.user,
            rating=rating,
            comment=comment
        )

        return redirect("product_detail", id=id)

    context = {
        "product": product_obj,
        "reviews": reviews,
        "related_products": related_products
    }

    return render(request, "product_detail.html", context)
    

# # VENDOR EARNINGS
# def vendor_earnings_view(request):

#     if not request.user.is_authenticated:
#         return redirect("login")

#     if request.user.role != "vendor":
#         return redirect("dashboard")

#     vendor, created = Vendor.objects.get_or_create(
#         user=request.user,
#         defaults={"shop_name": request.user.username}
#     )

#     order_items = OrderItem.objects.filter(vendor=vendor)

#     total_earnings = 0
#     total_sold = 0

#     for item in order_items:
#         total_earnings += item.price * item.quantity
#         total_sold += item.quantity

#     payouts = VendorPayout.objects.filter(vendor=vendor)

#     paid = payouts.filter(paid=True)
#     pending = payouts.filter(paid=False)

#     context = {
#         "order_items": order_items,
#         "total_earnings": total_earnings,
#         "total_sold": total_sold,
#         "paid": paid,
#         "pending": pending
#     }

#     return render(request, "vendor_earnings.html", context)

#PRODUCT
def products_view(request):

    products = product.objects.filter(is_active=True)
    categories = Category.objects.all()

    search = request.GET.get("search")
    category = request.GET.get("category")

    if search:
        products = products.filter(name__icontains=search)

    if category:
        products = products.filter(category_id=category)

    products = products.order_by("-created_at")

    context = {
        "products": products,
        "categories": categories
    }

    return render(request, "products.html", context)


# VENDOR EARNINGS
def vendor_earnings_view(request):

    if not request.user.is_authenticated:
        return redirect("login")

    if request.user.role != "vendor":
        return redirect("dashboard")

    vendor = Vendor.objects.get(user=request.user)

    order_items = OrderItem.objects.filter(vendor=vendor)

    total_earnings = 0
    total_sold = 0

    for item in order_items:
        total_earnings += item.price * item.quantity
        total_sold += item.quantity

    payouts = VendorPayout.objects.filter(vendor=vendor)

    paid = payouts.filter(paid=True)
    pending = payouts.filter(paid=False)

    context = {
        "order_items": order_items,
        "total_earnings": total_earnings,
        "total_sold": total_sold,
        "paid": paid,
        "pending": pending
    }

    return render(request, "vendor_earnings.html", context)

    # VENDOR PRODUCTS
def vendor_products_view(request):

    if not request.user.is_authenticated:
        return redirect("login")

    if request.user.role != "vendor":
        return redirect("dashboard")

    vendor = Vendor.objects.filter(user=request.user).first()

    products = product.objects.filter(vendor=vendor)

    context = {
        "products": products
    }

    return render(request, "vendor_products.html", context)

    # NOTIFICATIONS
def notifications_view(request):

    if not request.user.is_authenticated:
        return redirect("login")

    notifications = Notification.objects.filter(
        user=request.user
    ).order_by("-created_at")

    context = {
        "notifications": notifications
    }

    return render(request, "notifications.html", context)


  # NOTIFICATION READ
def mark_notification_read(request, id):

    if not request.user.is_authenticated:
        return redirect("login")

    notification = get_object_or_404(
        Notification,
        id=id,
        user=request.user   # security (user can only mark own notification)
    )

    notification.is_read = True
    notification.save()

    return redirect("notifications")


    # DELETE PRODUCT
def delete_product_view(request, id):

    if request.user.role != "vendor":
        return redirect("dashboard")

    product.objects.filter(id=id).delete()

    return redirect("vendor_products")



def vendor_products_view(request):

    if not request.user.is_authenticated:
        return redirect("login")

    if request.user.role != "vendor":
        return redirect("dashboard")

    vendor, created = Vendor.objects.get_or_create(
        user=request.user,
        defaults={"shop_name": request.user.username}
    )

    products = product.objects.filter(vendor=vendor)

    context = {
        "products": products
    }

    return render(request, "vendor_products.html", context)


    # EDIT PRODUCT
def edit_product_view(request, id):

    product_obj = product.objects.get(id=id)
    categories = Category.objects.all()

    if request.method == "POST":
        product_obj.name = request.POST.get("name")
        product_obj.description = request.POST.get("description")
        product_obj.price = request.POST.get("price")
        product_obj.stock = request.POST.get("stock")

        category_id = request.POST.get("category")
        product_obj.category = Category.objects.get(id=category_id)

        if request.FILES.get("image"):
            product_obj.image = request.FILES.get("image")

        product_obj.save()

        return redirect("vendor_products")

    context = {
        "product": product_obj,
        "categories": categories
    }

    return render(request, "edit_products.html", context)


#APPROVE_ORDER
def approve_order_view(request, id):

    if not request.user.is_authenticated:
        return redirect("login")

    if request.user.role != "vendor":
        return redirect("dashboard")

    vendor = Vendor.objects.filter(user=request.user).first()

    order_item = OrderItem.objects.filter(
        order_id=id,
        vendor=vendor
    ).first()

    if order_item:
        order = order_item.order
        order.status = "approved"
        order.save()

    return redirect("orders")

#PAYMENT
def payment_view(request, id):

    order = Order.objects.get(id=id)

    return render(request, "payment.html", {
        "order": order
    })

# LOGOUT
def logout_view(request):
    logout(request)
    return redirect("login")


# EDIT PROFILE
def edit_profile_view(request):
    
    if not request.user.is_authenticated:
        return redirect("login")
    
    user = request.user
    
    if request.method == "POST":
        # Update basic user info
        user.username = request.POST.get("username", user.username)
        user.email = request.POST.get("email", user.email)
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.save()
        
        messages.success(request, "Profile updated successfully")
        return redirect("profile")
    
    # Get user profile if exists
    user_profile = None
    try:
        user_profile = user.userprofile
    except:
        user_profile = None
    
    context = {
        "user": user,
        "user_profile": user_profile
    }
    
    return render(request, "edit_profile.html", context)


# CHANGE EMAIL
def change_email_view(request):
    
    if not request.user.is_authenticated:
        return redirect("login")
    
    if request.method == "POST":
        user = request.user
        new_email = request.POST.get("new_email")
        password = request.POST.get("password")
        
        # Verify password
        if not user.check_password(password):
            messages.error(request, "Incorrect password")
            return redirect("edit_profile")
        
        # Check if email already exists
        from django.contrib.auth.models import User
        if User.objects.filter(email=new_email).exclude(id=user.id).exists():
            messages.error(request, "Email already in use")
            return redirect("edit_profile")
        
        # Update email
        user.email = new_email
        user.save()
        
        messages.success(request, "Email changed successfully")
        return redirect("profile")
    
    return redirect("edit_profile")


# CHANGE PASSWORD
def change_password_view(request):
    
    if not request.user.is_authenticated:
        return redirect("login")
    
    if request.method == "POST":
        user = request.user
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")
        
        # Verify current password
        if not user.check_password(current_password):
            messages.error(request, "Current password is incorrect")
            return redirect("edit_profile")
        
        # Check if new passwords match
        if new_password != confirm_password:
            messages.error(request, "New passwords do not match")
            return redirect("edit_profile")
        
        # Check password length
        if len(new_password) < 8:
            messages.error(request, "Password must be at least 8 characters long")
            return redirect("edit_profile")
        
        # Update password
        user.set_password(new_password)
        user.save()
        
        # Re-authenticate user to keep session active
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(request, user)
        
        messages.success(request, "Password changed successfully")
        return redirect("profile")
    
    return redirect("edit_profile")

# EDIT PROFILE
def edit_profile_view(request):
    
    if not request.user.is_authenticated:
        return redirect("login")
    
    user = request.user
    
    if request.method == "POST":
        # Update basic user info
        user.username = request.POST.get("username", user.username)
        user.email = request.POST.get("email", user.email)
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.save()
        
        messages.success(request, "Profile updated successfully")
        return redirect("profile")
    
    # Get user profile if exists
    user_profile = None
    try:
        user_profile = user.userprofile
    except:
        user_profile = None
    
    context = {
        "user": user,
        "user_profile": user_profile
    }
    
    return render(request, "edit_profile.html", context)


# CHANGE EMAIL
def change_email_view(request):
    
    if not request.user.is_authenticated:
        return redirect("login")
    
    if request.method == "POST":
        user = request.user
        new_email = request.POST.get("new_email")
        password = request.POST.get("password")
        
        # Verify password
        if not user.check_password(password):
            messages.error(request, "Incorrect password")
            return redirect("edit_profile")
        
        # Check if email already exists
        from django.contrib.auth.models import User
        if User.objects.filter(email=new_email).exclude(id=user.id).exists():
            messages.error(request, "Email already in use")
            return redirect("edit_profile")
        
        # Update email
        user.email = new_email
        user.save()
        
        messages.success(request, "Email changed successfully")
        return redirect("profile")
    
    return redirect("edit_profile")


# CHANGE PASSWORD
def change_password_view(request):
    
    if not request.user.is_authenticated:
        return redirect("login")
    
    if request.method == "POST":
        user = request.user
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")
        
        # Verify current password
        if not user.check_password(current_password):
            messages.error(request, "Current password is incorrect")
            return redirect("edit_profile")
        
        # Check if new passwords match
        if new_password != confirm_password:
            messages.error(request, "New passwords do not match")
            return redirect("edit_profile")
        
        # Check password length
        if len(new_password) < 8:
            messages.error(request, "Password must be at least 8 characters long")
            return redirect("edit_profile")
        
        # Update password
        user.set_password(new_password)
        user.save()
        
        # Re-authenticate user to keep session active
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(request, user)
        
        messages.success(request, "Password changed successfully")
        return redirect("profile")
    
    return redirect("edit_profile")
