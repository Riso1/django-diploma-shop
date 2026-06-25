from django.contrib import admin

from .models import (
    Category,
    Product,
    ProductImage,
    ProductReview,
    ProductSpecification,
    Sale,
    Tag,
)


class SoftDeleteAdmin(admin.ModelAdmin):
    actions = ["restore_selected"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if hasattr(self.model, "all_objects"):
            return self.model.all_objects.all()
        return queryset

    def delete_model(self, request, obj):
        obj.delete()

    def delete_queryset(self, request, queryset):
        queryset.delete()

    @admin.action(description="Восстановить выбранные записи")
    def restore_selected(self, request, queryset):
        queryset.update(is_deleted=False, deleted_at=None)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1


class SaleInline(admin.TabularInline):
    model = Sale
    extra = 0


@admin.register(Category)
class CategoryAdmin(SoftDeleteAdmin):
    list_display = ("title", "parent", "is_active", "sort_index", "is_deleted")
    list_filter = ("is_active", "is_deleted", "parent")
    search_fields = ("title",)
    ordering = ("sort_index", "title")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(SoftDeleteAdmin):
    list_display = (
        "title",
        "category",
        "price",
        "count",
        "is_active",
        "limited_edition",
        "free_delivery",
        "sort_index",
        "purchases_count",
        "is_deleted",
    )
    list_filter = (
        "category",
        "is_active",
        "limited_edition",
        "free_delivery",
        "is_deleted",
        "tags",
    )
    search_fields = ("title", "description", "full_description")
    filter_horizontal = ("tags",)
    inlines = [ProductImageInline, ProductSpecificationInline, SaleInline]
    ordering = ("sort_index", "-purchases_count", "title")


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "author", "email", "rate", "is_active", "created_at")
    list_filter = ("is_active", "rate", "created_at")
    search_fields = ("author", "email", "text", "product__title")
    readonly_fields = ("created_at",)


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("product", "sale_price", "date_from", "date_to", "is_active")
    list_filter = ("is_active", "date_from", "date_to")
    search_fields = ("product__title",)
