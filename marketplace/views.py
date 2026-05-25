import re

from django.contrib import messages
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import OrderForm
from .models import Category, Order, Product
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


def _extract_phone(text):
    match = re.search(r"(\+?\d[\d\s().-]{7,}\d)", text)
    return match.group(1).strip() if match else ""


def _extract_quantity(text):
    match = re.search(r"(?:количество|нужно|надо|возьму|закажу|need)\D{0,12}(\d{1,5})", text, re.IGNORECASE)
    return int(match.group(1)) if match else 1


def _extract_name(text):
    match = re.search(r"(?:меня зовут|имя)\s+([А-Яа-яA-Za-z' -]{2,40})", text, re.IGNORECASE)
    return match.group(1).strip() if match else "Клиент из чата"


def _product_payload(product):
    return {"id": product.id, "name": product.name, "price": f"{product.price:,.0f}".replace(",", " "), "unit": product.unit, "city": product.city, "url": product.get_absolute_url()}


@require_POST
def assistant_chat(request):
    message = request.POST.get("message", "").strip()
    selected_product_id = request.POST.get("product_id", "").strip()

    if selected_product_id:
        product = get_object_or_404(Product, pk=selected_product_id, is_active=True)
        request.session["chat_product_id"] = product.id
        return JsonResponse({"reply": f"Выбран товар: {product.name}. Напишите телефон и количество, например: +998 90 123 45 67, нужно 5 мешков.", "products": [_product_payload(product)]})

    if not message:
        return JsonResponse({"reply": "Напишите, какой материал нужен: цемент, кирпич, арматура или другой товар."})

    phone = _extract_phone(message)
    product_id = request.session.get("chat_product_id")
    if phone and product_id:
        product = get_object_or_404(Product, pk=product_id, is_active=True)
        order = Order.objects.create(customer_name=_extract_name(message), phone=phone, city=product.city, product=product, quantity=_extract_quantity(message), comment=f"Заявка из чат-виджета: {message}")
        send_order_notification(order)
        request.session.pop("chat_product_id", None)
        return JsonResponse({"reply": f"Заявка #{order.id} создана: {product.name}, количество {order.quantity} {product.unit}. Менеджер свяжется с вами."})

    aliases = {"cement": "цемент", "kirpich": "кирпич", "brick": "кирпич", "armatura": "арматура", "rebar": "арматура", "kley": "клей"}
    search_text = aliases.get(message.lower(), message)
    raw_tokens = [token for token in re.split(r"\W+", search_text.lower()) if len(token) > 1]
    tokens = raw_tokens + [aliases[token] for token in raw_tokens if token in aliases]
    query = Q(name__icontains=search_text) | Q(description__icontains=search_text) | Q(category__name__icontains=search_text)
    for token in tokens:
        query |= Q(name__icontains=token) | Q(description__icontains=token) | Q(category__name__icontains=token)

    products = Product.objects.filter(is_active=True).select_related("category", "seller").filter(query)[:5]
    if not products:
        return JsonResponse({"reply": "Пока не нашёл точный товар. Попробуйте написать название проще: цемент, кирпич, арматура, клей."})
    return JsonResponse({"reply": "Нашёл подходящие товары. Выберите один, и я помогу оформить заявку.", "products": [_product_payload(product) for product in products]})
