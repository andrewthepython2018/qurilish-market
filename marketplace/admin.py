from django.contrib import admin
from .models import Category, Order, Product, Seller


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "city", "is_active")
    list_filter = ("city", "is_active")
    search_fields = ("name", "phone", "city", "address")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "seller", "price", "unit", "stock", "city", "is_active")
    list_filter = ("category", "city", "is_active", "seller")
    search_fields = ("name", "description", "seller__name")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("category", "seller")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_name", "phone", "product", "quantity", "status", "created_at")
    list_filter = ("status", "city", "created_at")
    search_fields = ("customer_name", "phone", "product__name", "comment")
    autocomplete_fields = ("product",)
    readonly_fields = ("created_at",)
    list_editable = ("status",)
