from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from .forms import OrderForm
from .models import Category, Product
from .telegram import send_order_notification


def _catalog_filters(request, products):
    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()
    city = request.GET.get("city", "").strip()
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if category_slug:
        products = products.filter(category__slug=category_slug)
    if city:
        products = products.filter(city__iexact=city)
    return products, {"q": query, "category": category_slug, "city": city}


def home(request):
    categories = Category.objects.annotate(active_count=Count("products", filter=Q(products__is_active=True)))[:6]
    products = Product.objects.filter(is_active=True).select_related("category", "seller")[:8]
    cities = Product.objects.filter(is_active=True).order_by("city").values_list("city", flat=True).distinct()
    return render(request, "marketplace/home.html", {"categories": categories, "products": products, "cities": cities})


def catalog(request):
    products = Product.objects.filter(is_active=True).select_related("category", "seller")
    products, filters = _catalog_filters(request, products)
    cities = Product.objects.filter(is_active=True).order_by("city").values_list("city", flat=True).distinct()
    return render(request, "marketplace/catalog.html", {"products": products, "categories": Category.objects.all(), "cities": cities, "filters": filters, "page_title": "Каталог товаров"})


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(is_active=True, category=category).select_related("category", "seller")
    products, filters = _catalog_filters(request, products)
    cities = Product.objects.filter(is_active=True, category=category).order_by("city").values_list("city", flat=True).distinct()
    return render(request, "marketplace/catalog.html", {"category": category, "products": products, "categories": Category.objects.all(), "cities": cities, "filters": filters, "page_title": category.name})


def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related("category", "seller"), slug=slug, is_active=True)
    similar_products = Product.objects.filter(is_active=True, category=product.category).exclude(pk=product.pk).select_related("category", "seller")[:4]
    return render(request, "marketplace/product_detail.html", {"product": product, "similar_products": similar_products})


def order_create(request, product_id):
    product = get_object_or_404(Product.objects.select_related("category", "seller"), pk=product_id, is_active=True)
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.product = product
            order.save()
            send_order_notification(order)
            messages.success(request, "Заявка отправлена. Менеджер скоро свяжется с вами.")
            return redirect("product_detail", slug=product.slug)
    else:
        form = OrderForm(initial={"city": product.city, "quantity": 1})
    return render(request, "marketplace/order_form.html", {"product": product, "form": form})
