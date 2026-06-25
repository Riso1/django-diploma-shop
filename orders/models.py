from decimal import Decimal

from django.conf import settings
from django.db import models

from shop.models import Product, SoftDeleteModel


class DeliverySettings(models.Model):
    express_delivery_price = models.DecimalField(
        "стоимость экспресс-доставки",
        max_digits=10,
        decimal_places=2,
        default=Decimal("500.00"),
    )
    free_delivery_threshold = models.DecimalField(
        "порог бесплатной обычной доставки",
        max_digits=10,
        decimal_places=2,
        default=Decimal("2000.00"),
    )
    standard_delivery_price = models.DecimalField(
        "стоимость обычной доставки до порога",
        max_digits=10,
        decimal_places=2,
        default=Decimal("200.00"),
    )

    class Meta:
        verbose_name = "настройки доставки"
        verbose_name_plural = "настройки доставки"

    def save(self, *args, **kwargs):
        if not self.pk and DeliverySettings.objects.exists():
            self.pk = DeliverySettings.objects.first().pk
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        settings_obj, _ = cls.objects.get_or_create(pk=1)
        return settings_obj

    def __str__(self):
        return "Настройки доставки"


class Basket(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="пользователь",
        related_name="baskets",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    session_key = models.CharField("ключ сессии", max_length=100, blank=True)
    created_at = models.DateTimeField("дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("дата обновления", auto_now=True)

    class Meta:
        verbose_name = "корзина"
        verbose_name_plural = "корзины"

    def __str__(self):
        if self.user:
            return f"Корзина {self.user}"
        return f"Корзина сессии {self.session_key}"


class BasketItem(models.Model):
    basket = models.ForeignKey(
        Basket,
        verbose_name="корзина",
        related_name="items",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        verbose_name="товар",
        related_name="basket_items",
        on_delete=models.CASCADE,
    )
    count = models.PositiveIntegerField("количество", default=1)

    class Meta:
        verbose_name = "товар в корзине"
        verbose_name_plural = "товары в корзине"
        unique_together = ("basket", "product")

    def __str__(self):
        return f"{self.product} x {self.count}"


class Order(SoftDeleteModel):
    DELIVERY_ORDINARY = "ordinary"
    DELIVERY_EXPRESS = "express"

    DELIVERY_CHOICES = (
        (DELIVERY_ORDINARY, "Обычная доставка"),
        (DELIVERY_EXPRESS, "Экспресс-доставка"),
    )

    PAYMENT_ONLINE = "online"
    PAYMENT_SOMEONE = "someone"

    PAYMENT_CHOICES = (
        (PAYMENT_ONLINE, "Онлайн картой"),
        (PAYMENT_SOMEONE, "Онлайн со случайного чужого счёта"),
    )

    STATUS_CREATED = "created"
    STATUS_ACCEPTED = "accepted"
    STATUS_PAID = "paid"
    STATUS_PAYMENT_ERROR = "payment_error"

    STATUS_CHOICES = (
        (STATUS_CREATED, "Создан"),
        (STATUS_ACCEPTED, "Подтверждён"),
        (STATUS_PAID, "Оплачен"),
        (STATUS_PAYMENT_ERROR, "Ошибка оплаты"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="пользователь",
        related_name="orders",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    full_name = models.CharField("Ф. И. О.", max_length=255, blank=True)
    email = models.EmailField("email", blank=True)
    phone = models.CharField("телефон", max_length=30, blank=True)

    delivery_type = models.CharField(
        "способ доставки",
        max_length=20,
        choices=DELIVERY_CHOICES,
        default=DELIVERY_ORDINARY,
    )
    payment_type = models.CharField(
        "способ оплаты",
        max_length=20,
        choices=PAYMENT_CHOICES,
        default=PAYMENT_ONLINE,
    )

    city = models.CharField("город", max_length=255, blank=True)
    address = models.TextField("адрес", blank=True)
    comment = models.TextField("комментарий к заказу", blank=True)

    total_cost = models.DecimalField(
        "общая стоимость",
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    delivery_cost = models.DecimalField(
        "стоимость доставки",
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    status = models.CharField(
        "статус",
        max_length=30,
        choices=STATUS_CHOICES,
        default=STATUS_CREATED,
    )
    payment_error = models.TextField("ошибка оплаты", blank=True)

    created_at = models.DateTimeField("дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("дата обновления", auto_now=True)

    class Meta:
        verbose_name = "заказ"
        verbose_name_plural = "заказы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Заказ №{self.pk}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        verbose_name="заказ",
        related_name="items",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        verbose_name="товар",
        related_name="order_items",
        on_delete=models.PROTECT,
    )
    product_title = models.CharField("название товара на момент заказа", max_length=255)
    price = models.DecimalField("цена на момент заказа", max_digits=10, decimal_places=2)
    count = models.PositiveIntegerField("количество", default=1)

    class Meta:
        verbose_name = "товар в заказе"
        verbose_name_plural = "товары в заказе"

    def __str__(self):
        return f"{self.product_title} x {self.count}"


class Payment(models.Model):
    STATUS_WAITING = "waiting"
    STATUS_SUCCESS = "success"
    STATUS_ERROR = "error"

    STATUS_CHOICES = (
        (STATUS_WAITING, "Ожидает подтверждения"),
        (STATUS_SUCCESS, "Оплата подтверждена"),
        (STATUS_ERROR, "Ошибка оплаты"),
    )

    order = models.ForeignKey(
        Order,
        verbose_name="заказ",
        related_name="payments",
        on_delete=models.CASCADE,
    )
    number = models.CharField("номер карты/счёта", max_length=8)
    status = models.CharField(
        "статус",
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_WAITING,
    )
    error = models.TextField("текст ошибки", blank=True)
    created_at = models.DateTimeField("дата создания", auto_now_add=True)

    class Meta:
        verbose_name = "платёж"
        verbose_name_plural = "платежи"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Платёж по заказу №{self.order_id}"
