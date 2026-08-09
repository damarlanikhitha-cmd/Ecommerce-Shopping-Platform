from django.contrib import admin
from .models import Product, Category, Cart, CartItem, Wishlist, Order, OrderItem, Coupon, Review, Profile, ProductImage

admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Wishlist)
admin.site.register(Coupon)
admin.site.register(Review)
admin.site.register(Profile)
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "customer_name",
        "phone",
        "total_amount",
        "status",
        "created_at",
    )

    fields = (
        "user",
        "customer_name",
        "phone",
        "address",
        "total_amount",
        "status",
    )
admin.site.register(OrderItem)





# Register your models here.
