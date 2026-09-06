from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import Product, Category, Cart, CartItem, Order, Wishlist, Review, Coupon, Profile, OrderItem
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from django.db.models import Avg
from django.db.models import Sum
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required





def home(request):
    query = request.GET.get("q")
    category_id = request.GET.get("category")
    sort = request.GET.get("sort")

    products = Product.objects.all()
    reviews = Review.objects.all().order_by("-created_at")

    if query:
        products = products.filter(name__icontains=query)

    if category_id:
        products = products.filter(category__id=category_id)
    if sort == "price_low":
        products = products.order_by("price")
    elif sort == "price_high":
        products = products.order_by("-price")
    elif sort == "name":
        products = products.order_by("name")

    categories = Category.objects.all()
    recent_ids = request.session.get("recent_products", [])
    recent_products = Product.objects.filter(id__in=recent_ids)
    paginator = Paginator(products, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    

    return render(request, "shop/home.html", {
        "categories": categories,
        "reviews": reviews,
        "recent_products": recent_products,
        "sort": sort,
        "page_obj": page_obj,
        "selected_category": category_id,
    })

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

@login_required(login_url='/login/')
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('shop:cart')
@login_required
def cart(request):
    user = request.user

    cart, created = Cart.objects.get_or_create(user=user)

    cart_items = CartItem.objects.filter(cart=cart)

    total = sum(
        item.product.price * item.quantity
        for item in cart_items
    )

    return render(request, "shop/cart.html", {
        "cart": cart,
        "cart_items": cart_items,
        "total": total,
    })
@login_required(login_url="/login/")
def remove_from_cart(request, product_id):
    cart = get_object_or_404(Cart, user=request.user)

    CartItem.objects.filter(
        cart=cart,
        product_id=product_id
    ).delete()

    return redirect("shop:cart")


@login_required(login_url="/login/")
def cart_add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    Cart.objects.filter(user=request.user).first().items.filter(
        product=product
    ).delete()

    return redirect("shop:cart")
@login_required(login_url="/login/")
def increase_quantity(request, product_id):

    cart = get_object_or_404(
        Cart,
        user=request.user
    )

    cart_item = get_object_or_404(
        CartItem,
        cart=cart,
        product_id=product_id
    )

    if cart_item.quantity < cart_item.product.stock:
        cart_item.quantity += 1
        cart_item.save()

    return redirect("shop:cart")


@login_required(login_url="/login/")
def decrease_quantity(request, product_id):

    cart = get_object_or_404(
        Cart,
        user=request.user
    )

    cart_item = get_object_or_404(
        CartItem,
        cart=cart,
        product_id=product_id
    )

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()

    return redirect("shop:cart")
@login_required(login_url="/login/")
def buy_now(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    if product.stock <= 0:
        return redirect("shop:home")

    # Store only the selected product
    # for Buy Now checkout
    request.session["buy_now_product_id"] = product.id

    return redirect("shop:checkout")
@login_required(login_url="/login/")
def checkout(request):

    # Check whether this is a Buy Now checkout
    buy_now_product_id = request.session.get("buy_now_product_id")

    if buy_now_product_id:

        product = get_object_or_404(
            Product,
            id=buy_now_product_id
        )

        quantity = 1

        subtotal = product.price * quantity

        discount = 0
        total = subtotal

        if request.method == "POST":

            name = request.POST.get("name")
            phone = request.POST.get("phone")
            address = request.POST.get("address")
            coupon_code = request.POST.get("coupon")

            if coupon_code:
                try:
                    coupon = Coupon.objects.get(
                        code=coupon_code,
                        active=True
                    )

                    discount = (
                        subtotal * coupon.discount
                    ) / 100

                    total = subtotal - discount

                except Coupon.DoesNotExist:
                    pass

            request.session["order_name"] = name
            request.session["order_phone"] = phone
            request.session["order_address"] = address
            request.session["order_total"] = str(total)
            request.session["order_discount"] = str(discount)

            # Remember this is a Buy Now order
            request.session["buy_now_product_id"] = product.id

            return redirect("shop:payment")

        return render(
            request,
            "shop/checkout.html",
            {
                "buy_now": True,
                "buy_now_product": product,
                "buy_now_quantity": quantity,
                "subtotal": subtotal,
                "discount": discount,
                "total": total,
            }
        )

    # --------------------------------------------------
    # NORMAL CART CHECKOUT
    # --------------------------------------------------

    user = request.user

    cart, created = Cart.objects.get_or_create(
        user=user
    )

    cart_items = CartItem.objects.filter(
        cart=cart
    )

    subtotal = sum(
        item.product.price * item.quantity
        for item in cart_items
    )

    discount = 0
    total = subtotal

    if request.method == "POST":

        name = request.POST.get("name")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        coupon_code = request.POST.get("coupon")

        if coupon_code:
            try:
                coupon = Coupon.objects.get(
                    code=coupon_code,
                    active=True
                )

                discount = (
                    subtotal * coupon.discount
                ) / 100

                total = subtotal - discount

            except Coupon.DoesNotExist:
                pass

        request.session["order_name"] = name
        request.session["order_phone"] = phone
        request.session["order_address"] = address
        request.session["order_total"] = str(total)
        request.session["order_discount"] = str(discount)

        return redirect("shop:payment")

    return render(
        request,
        "shop/checkout.html",
        {
            "buy_now": False,
            "cart_items": cart_items,
            "subtotal": subtotal,
            "discount": discount,
            "total": total,
        }
    )
        
def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("shop:home")
    else:
        form = UserCreationForm()

    return render(request, "shop/register.html", {"form": form})
def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("shop:home")
    else:
        form = AuthenticationForm()

    return render(request, "shop/login.html", {"form": form})


def user_logout(request):
    logout(request)
    return redirect("shop:home")
@login_required(login_url="/login/")
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)

    return render(request, "shop/wishlist.html", {
        "wishlist_items": wishlist_items
    })
@login_required(login_url="/login/")
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    return redirect("shop:wishlist")

@login_required(login_url="/login/")
def wishlist_add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if product.stock <= 0:
        return redirect("shop:wishlist")

    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()

    return redirect("shop:cart")
@login_required(login_url="/login/")
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    Wishlist.objects.filter(
        user=request.user,
        product=product
    ).delete()

    return redirect("shop:wishlist")

@login_required(login_url="/login/")
def wishlist_buy_now(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id
    )

    if product.stock <= 0:
        return redirect("shop:wishlist")

    # Store only the selected product for Buy Now
    request.session["buy_now_product_id"] = product.id

    return redirect("shop:checkout")
@login_required(login_url="/login/")
def payment(request):

    # Get Buy Now product from session
    buy_now_product_id = request.session.get("buy_now_product_id")

    if request.method == "POST":

        payment_method = request.POST.get("payment")

        name = request.session.get("order_name")
        phone = request.session.get("order_phone")
        address = request.session.get("order_address")
        total = request.session.get("order_total")
        discount = request.session.get("order_discount", "0")

        # Safety check
        if not total:
            return redirect("shop:checkout")

        # ==================================================
        # BUY NOW ORDER
        # ==================================================
        if buy_now_product_id:

            product = get_object_or_404(
                Product,
                id=buy_now_product_id
            )

            # Check stock before creating the order
            if product.stock < 1:
                return redirect("shop:checkout")

            with transaction.atomic():

                # Create order only after stock check
                order = Order.objects.create(
                    user=request.user,
                    customer_name=name,
                    phone=phone,
                    address=address,
                    total_amount=total,
                    payment_method=payment_method,
                )

                # Create OrderItem
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=1,
                    price=product.price
                )

                # Reduce stock
                product.stock -= 1
                product.save()

            # Remove Buy Now session
            request.session.pop("buy_now_product_id", None)

        # ==================================================
        # CART ORDER
        # ==================================================
        else:

            cart = get_object_or_404(
                Cart,
                user=request.user
            )

            cart_items = CartItem.objects.filter(
                cart=cart
            )

            # Check whether cart is empty
            if not cart_items.exists():
                return redirect("shop:cart")

            # Check stock for ALL cart items first
            for item in cart_items:
                if item.quantity > item.product.stock:
                    return redirect("shop:cart")

            with transaction.atomic():

                # Create order only after all stock checks pass
                order = Order.objects.create(
                    user=request.user,
                    customer_name=name,
                    phone=phone,
                    address=address,
                    total_amount=total,
                    payment_method=payment_method,
                )

                for item in cart_items:

                    # Create OrderItem
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.price
                    )

                    # Reduce stock
                    item.product.stock -= item.quantity
                    item.product.save()

                # Clear cart
                cart_items.delete()

        # ==================================================
        # EMAIL
        # ==================================================

        message = (
            f"Hello {name},\n\n"
            f"Your order has been placed successfully.\n\n"
            f"Subtotal: ₹{float(total) + float(discount)}\n"
            f"Discount: ₹{discount}\n"
            f"Final Total: ₹{total}\n"
            f"Status: Pending\n\n"
            f"Thank you for shopping with us!"
        )

        customer_email = request.user.email

        if customer_email:
            send_mail(
                subject="Order Confirmation",
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[customer_email],
                fail_silently=False,
            )

        # Clear checkout session data
        request.session.pop("order_name", None)
        request.session.pop("order_phone", None)
        request.session.pop("order_address", None)
        request.session.pop("order_total", None)
        request.session.pop("order_discount", None)

        return redirect("shop:order_success")

    # GET request
    return render(request, "shop/payment.html")

@login_required(login_url="/login/")
def order_success(request):
    return render(request, "shop/order_success.html")

@login_required(login_url="/login/")
def my_orders(request):

    orders = Order.objects.filter(
        user=request.user
    ).prefetch_related(
        "orderitem_set"
    ).order_by("-created_at")

    for order in orders:

        active_items = order.orderitem_set.filter(
            status="Active"
        )

        order.active_total = sum(
            item.price * item.quantity
            for item in active_items
        )

        # If active items exist, show their total.
        # Otherwise, show the original order total.
        if active_items.exists():
            order.display_total = order.active_total
        else:
            order.display_total = order.total_amount

    return render(
        request,
        "shop/my_orders.html",
        {"orders": orders}
    )
@login_required(login_url="/login/")
def cancel_order(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    if request.method == "POST" and order.status == "Pending":

        order_items = OrderItem.objects.filter(
            order=order
        )

        for item in order_items:
            item.product.stock += item.quantity
            item.product.save()

        order.status = "Cancelled"
        order.save()

        order_items.update(status="Cancelled")

    return redirect("shop:my_orders")
@login_required(login_url="/login/")
def cancel_order_item(request, item_id):

    order_item = get_object_or_404(
        OrderItem,
        id=item_id,
        order__user=request.user
    )

    if order_item.status == "Active" and order_item.order.status == "Pending":

        # Restore the cancelled product quantity to stock
        order_item.product.stock += order_item.quantity
        order_item.product.save()

        # Mark only this product as cancelled
        order_item.status = "Cancelled"
        order_item.save()

        # Calculate remaining active items
        active_items = OrderItem.objects.filter(
            order=order_item.order,
            status="Active"
        )

        # If no active products remain, cancel the whole order
        if not active_items.exists():
            order_item.order.status = "Cancelled"
            order_item.order.save()

    return redirect("shop:my_orders")


@login_required(login_url="/login/")
def return_order(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    if order.status == "Delivered":

        if request.method == "POST":
            reason = request.POST.get("return_reason")

            order.status = "Returned"
            order.return_reason = reason
            order.save()

            return redirect("shop:my_orders")

    return redirect("shop:my_orders")


@login_required(login_url="/login/")
def exchange_order(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    if order.status == "Delivered":

        if request.method == "POST":
            reason = request.POST.get("exchange_reason")

            order.status = "Exchanged"
            order.exchange_reason = reason
            order.save()

            return redirect("shop:my_orders")

    return redirect("shop:my_orders")

@login_required(login_url="/login/")
def add_review(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id
    )

    # Check whether the user purchased this product
    has_purchased = OrderItem.objects.filter(
        order__user=request.user,
        order__status="Delivered",
        product=product
    ).exists()

    if not has_purchased:
        return redirect("shop:product_detail", product_id=product.id)

    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        if rating and comment:
            Review.objects.create(
                user=request.user,
                product=product,
                rating=rating,
                comment=comment
            )

    return redirect(
        "shop:product_detail",
        product_id=product.id
    )

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    recent_products = request.session.get("recent_products", [])

    if product.id in recent_products:
       recent_products.remove(product.id)

    recent_products.insert(0, product.id)

    request.session["recent_products"] = recent_products[:5]

    reviews = Review.objects.filter(product=product).order_by("-created_at")

    similar_products = Product.objects.filter(
        category=product.category
    ).exclude(id=product.id)

    average_rating = reviews.aggregate(Avg("rating"))["rating__avg"]

    return render(request, "shop/product_detail.html", {
        "product": product,
        "reviews": reviews,
        "similar_products": similar_products,
        "average_rating": average_rating,
    })
@login_required(login_url="/login/")
def download_invoice(request, order_id):
    order = get_object_or_404(
    Order,
    id=order_id,
    user=request.user
)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'

    p = canvas.Canvas(response)

    p.setFont("Helvetica-Bold", 18)
    p.drawString(180, 800, "E-Commerce Invoice")

    p.setFont("Helvetica", 12)
    p.drawString(50, 760, f"Order ID: {order.id}")
    p.drawString(50, 740, f"Customer: {order.customer_name}")
    p.drawString(50, 720, f"Phone: {order.phone}")
    p.drawString(50, 700, f"Address: {order.address}")
    p.drawString(50, 680, f"Amount: ₹{order.total_amount}")
    p.drawString(50, 660, f"Status: {order.status}")
    p.drawString(50, 640, f"Date: {order.created_at.strftime('%d-%m-%Y %H:%M')}")

    p.drawString(50, 600, "Thank you for shopping with us!")

    p.showPage()
    p.save()

    return response
def contact(request):
    return render(request, "shop/contact.html")

@login_required(login_url="/login/")
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect("shop:home")
    total_orders = Order.objects.count()
    total_products = Product.objects.count()
    total_users = User.objects.count()

    total_revenue = Order.objects.aggregate(
        total=Sum("total_amount")
    )["total"] or 0

    low_stock_products = Product.objects.filter(stock__lt=5)
    best_products = (
    CartItem.objects.values("product__name")
    .annotate(total_sales=Sum("quantity"))
    .order_by("-total_sales")[:5]
)

    pending_orders = Order.objects.filter(status="Pending").count()
    shipped_orders = Order.objects.filter(status="Shipped").count()

    return render(request, "shop/admin_dashboard.html", {
        "total_orders": total_orders,
        "total_products": total_products,
        "total_users": total_users,
        "total_revenue": total_revenue,
        "pending_orders": pending_orders,
        "shipped_orders": shipped_orders,
        "low_stock_products": low_stock_products,
        'best_products': best_products,
    })
@login_required(login_url="/login/")
def profile(request):

    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":

        # Save full name
        request.user.first_name = request.POST.get(
            "first_name",
            ""
        )

        # Save phone
        profile.phone = request.POST.get(
            "phone",
            ""
        )

        # Save address
        profile.address = request.POST.get(
            "address",
            ""
        )

        # Save profile picture
        if request.FILES.get("profile_image"):
            profile.profile_image = request.FILES["profile_image"]

        # Save everything
        request.user.save()
        profile.save()

        # Show updated profile again
        return redirect("shop:profile")

    return render(
        request,
        "shop/profile.html",
        {
            "profile": profile
        }
    )


