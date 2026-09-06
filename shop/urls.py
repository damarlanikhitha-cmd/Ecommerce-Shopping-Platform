from django.urls import path 
from . import views 

app_name = "shop"

urlpatterns = [
    path("",views.home, name='home'),
    path(
    "buy-now/<int:product_id>/",
    views.buy_now,
    name="buy_now"
),
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("add_to_cart/<int:product_id>/", views.add_to_cart, name='add_to_cart'),
    path("cart/", views.cart, name='cart'),
    path(
    "cart/remove/<int:product_id>/",
    views.remove_from_cart,
    name="remove_from_cart"
),

path(
    "cart/wishlist/<int:product_id>/",
    views.cart_add_to_wishlist,
    name="cart_add_to_wishlist"
),
path(
    "cart/increase/<int:product_id>/",
    views.increase_quantity,
    name="increase_quantity"
),

path(
    "cart/decrease/<int:product_id>/",
    views.decrease_quantity,
    name="decrease_quantity"
),
    path("checkout/", views.checkout, name="checkout"),
    path(
    "wishlist/add/<int:product_id>/",
    views.add_to_wishlist,
    name="add_to_wishlist"
),

path(
    "wishlist/",
    views.wishlist,
    name="wishlist"
),

path(
    "wishlist/add-to-cart/<int:product_id>/",
    views.wishlist_add_to_cart,
    name="wishlist_add_to_cart"
),

path(
    "wishlist/buy-now/<int:product_id>/",
    views.wishlist_buy_now,
    name="wishlist_buy_now"
),

path(
    "wishlist/remove/<int:product_id>/",
    views.remove_from_wishlist,
    name="remove_from_wishlist"
),
    path("payment/", views.payment, name="payment"),
    path("order-success/", views.order_success, name="order_success"),
    path("my-orders", views.my_orders, name="my_orders"),
    path(
    "cancel-order/<int:order_id>/",
    views.cancel_order,
    name="cancel_order"
),
path(
    "cancel-order-item/<int:item_id>/",
    views.cancel_order_item,
    name="cancel_order_item"
),
path(
    "order/item/cancel/<int:item_id>/",
    views.cancel_order_item,
    name="cancel_order_item"
),

path(
    "return-order/<int:order_id>/",
    views.return_order,
    name="return_order"
),

path(
    "exchange-order/<int:order_id>/",
    views.exchange_order,
    name="exchange_order"
),
    path("review/<int:product_id>/", views.add_review, name="add_review"),
    path("product/<int:product_id>/", views.product_detail, name="product_detail"), 
    path("invoice/<int:order_id>/", views.download_invoice, name="download_invoice"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("profile/", views.profile, name="profile"),
]
from django.conf import settings
from django.conf.urls.static import static
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
