from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return super().update(is_deleted=True, deleted_at=timezone.now())

    def hard_delete(self):
        return super().delete()

    def alive(self):
        return self.filter(is_deleted=False)

    def deleted(self):
        return self.filter(is_deleted=True)


class SoftDeleteManager(models.Manager.from_queryset(SoftDeleteQuerySet)):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class AllObjectsManager(models.Manager.from_queryset(SoftDeleteQuerySet)):
    pass


class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField("удалён", default=False)
    deleted_at = models.DateTimeField("дата удаления", null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = AllObjectsManager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])

    def hard_delete(self, using=None, keep_parents=False):
        return super().delete(using=using, keep_parents=keep_parents)


class Category(SoftDeleteModel):
    title = models.CharField("название", max_length=255)
    parent = models.ForeignKey(
        "self",
        verbose_name="родительская категория",
        related_name="subcategories",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    image = models.ImageField("иконка/изображение", upload_to="categories/", blank=True)
    is_active = models.BooleanField("активна", default=True)
    sort_index = models.PositiveIntegerField("индекс сортировки", default=0)

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "категории"
        ordering = ["sort_index", "title"]

    def clean(self):
        if self.parent and self.parent.parent:
            raise ValidationError("Максимальный уровень вложенности категорий — 2.")

    def __str__(self):
        return self.title


class Tag(models.Model):
    name = models.CharField("название", max_length=100, unique=True)
    categories = models.ManyToManyField(
        Category,
        verbose_name="категории",
        related_name="tags",
        blank=True,
    )

    class Meta:
        verbose_name = "тег"
        verbose_name_plural = "теги"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(SoftDeleteModel):
    category = models.ForeignKey(
        Category,
        verbose_name="категория",
        related_name="products",
        on_delete=models.PROTECT,
    )
    title = models.CharField("название", max_length=255)
    description = models.TextField("краткое описание", blank=True)
    full_description = models.TextField("полное описание", blank=True)
    price = models.DecimalField(
        "цена",
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    count = models.PositiveIntegerField("количество на складе", default=0)
    tags = models.ManyToManyField(Tag, verbose_name="теги", related_name="products", blank=True)

    free_delivery = models.BooleanField("бесплатная доставка", default=False)
    limited_edition = models.BooleanField("ограниченный тираж", default=False)
    is_active = models.BooleanField("активен", default=True)

    sort_index = models.PositiveIntegerField("индекс сортировки", default=0)
    purchases_count = models.PositiveIntegerField("количество покупок", default=0)
    rating = models.DecimalField(
        "рейтинг",
        max_digits=3,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    created_at = models.DateTimeField("дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("дата обновления", auto_now=True)

    class Meta:
        verbose_name = "товар"
        verbose_name_plural = "товары"
        ordering = ["sort_index", "-purchases_count", "title"]

    def __str__(self):
        return self.title


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        verbose_name="товар",
        related_name="images",
        on_delete=models.CASCADE,
    )
    image = models.ImageField("изображение", upload_to="products/")
    alt = models.CharField("alt-текст", max_length=255, blank=True)
    is_main = models.BooleanField("главное изображение", default=False)

    class Meta:
        verbose_name = "изображение товара"
        verbose_name_plural = "изображения товаров"

    def __str__(self):
        return self.alt or f"Изображение товара {self.product_id}"


class ProductSpecification(models.Model):
    product = models.ForeignKey(
        Product,
        verbose_name="товар",
        related_name="specifications",
        on_delete=models.CASCADE,
    )
    name = models.CharField("характеристика", max_length=255)
    value = models.CharField("значение", max_length=255)

    class Meta:
        verbose_name = "характеристика товара"
        verbose_name_plural = "характеристики товаров"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}: {self.value}"


class ProductReview(models.Model):
    product = models.ForeignKey(
        Product,
        verbose_name="товар",
        related_name="reviews",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="пользователь",
        related_name="product_reviews",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    author = models.CharField("автор", max_length=255)
    email = models.EmailField("email", blank=True)
    text = models.TextField("текст отзыва")
    rate = models.PositiveSmallIntegerField("оценка", default=5)
    is_active = models.BooleanField("активен", default=True)
    created_at = models.DateTimeField("дата создания", auto_now_add=True)

    class Meta:
        verbose_name = "отзыв"
        verbose_name_plural = "отзывы"
        ordering = ["-created_at"]

    def clean(self):
        if not 1 <= self.rate <= 5:
            raise ValidationError("Оценка должна быть от 1 до 5.")

    def __str__(self):
        return f"Отзыв {self.author} о {self.product}"


class Sale(models.Model):
    product = models.ForeignKey(
        Product,
        verbose_name="товар",
        related_name="sales",
        on_delete=models.CASCADE,
    )
    sale_price = models.DecimalField(
        "цена со скидкой",
        max_digits=10,
        decimal_places=2,
    )
    date_from = models.DateField("дата начала")
    date_to = models.DateField("дата окончания")
    is_active = models.BooleanField("активна", default=True)

    class Meta:
        verbose_name = "скидка"
        verbose_name_plural = "скидки"
        ordering = ["-date_from"]

    def clean(self):
        if self.date_to < self.date_from:
            raise ValidationError("Дата окончания скидки не может быть раньше даты начала.")

    def __str__(self):
        return f"Скидка на {self.product}"
