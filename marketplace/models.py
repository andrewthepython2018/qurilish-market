from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField("Название", max_length=120)
    slug = models.SlugField("Slug", max_length=140, unique=True)
    description = models.TextField("Описание", blank=True)
    image = models.ImageField("Изображение", upload_to="categories/", blank=True, null=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("category_detail", kwargs={"slug": self.slug})


class Seller(models.Model):
    name = models.CharField("Название продавца", max_length=160)
    phone = models.CharField("Телефон", max_length=40)
    city = models.CharField("Город", max_length=80)
    address = models.CharField("Адрес", max_length=255, blank=True)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Продавец"
        verbose_name_plural = "Продавцы"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.city})"


class Product(models.Model):
    name = models.CharField("Название", max_length=180)
    slug = models.SlugField("Slug", max_length=200, unique=True)
    category = models.ForeignKey(Category, verbose_name="Категория", on_delete=models.PROTECT, related_name="products")
    seller = models.ForeignKey(Seller, verbose_name="Продавец", on_delete=models.PROTECT, related_name="products")
    description = models.TextField("Описание")
    price = models.DecimalField("Цена", max_digits=12, decimal_places=2)
    unit = models.CharField("Единица", max_length=30, default="шт")
    stock = models.PositiveIntegerField("Остаток", default=0)
    city = models.CharField("Город", max_length=80)
    image = models.ImageField("Фото", upload_to="products/", blank=True, null=True)
    is_active = models.BooleanField("Активен", default=True)
    created_at = models.DateTimeField("Создан", auto_now_add=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["slug"]), models.Index(fields=["city"]), models.Index(fields=["is_active"])]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("product_detail", kwargs={"slug": self.slug})


class Order(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Новая"
        PROCESSING = "processing", "В обработке"
        CONFIRMED = "confirmed", "Подтверждена"
        CANCELLED = "cancelled", "Отменена"
        COMPLETED = "completed", "Выполнена"

    customer_name = models.CharField("Имя клиента", max_length=120)
    phone = models.CharField("Телефон", max_length=40)
    city = models.CharField("Город", max_length=80, blank=True)
    product = models.ForeignKey(Product, verbose_name="Товар", on_delete=models.PROTECT, related_name="orders")
    quantity = models.PositiveIntegerField("Количество", default=1)
    comment = models.TextField("Комментарий", blank=True)
    status = models.CharField("Статус", max_length=20, choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField("Создана", auto_now_add=True)

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Заявка #{self.pk} - {self.product.name}"
