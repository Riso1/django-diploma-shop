from django.contrib import admin

from .models import Basket, BasketItem, DeliverySettings, Order, OrderItem, Payment


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


class BasketItemInline(admin.TabularInline):
    model = BasketItem
    extra = 0


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "product_title", "price", "count")
    can_delete = False


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ("number", "status", "error", "created_at")
    can_delete = False


@admin.register(DeliverySettings)
class DeliverySettingsAdmin(admin.ModelAdmin):
    list_display = (
        "express_delivery_price",
        "free_delivery_threshold",
        "standard_delivery_price",
    )


@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "session_key", "created_at", "updated_at")
    search_fields = ("user__username", "session_key")
    inlines = [BasketItemInline]


@admin.register(Order)
class OrderAdmin(SoftDeleteAdmin):
    list_display = (
        "id",
        "user",
        "full_name",
        "email",
        "phone",
        "total_cost",
        "delivery_type",
        "payment_type",
        "status",
        "is_deleted",
        "created_at",
    )
    list_filter = ("delivery_type", "payment_type", "status", "is_deleted", "created_at")
    search_fields = ("full_name", "email", "phone", "user__username")
    readonly_fields = ("created_at", "updated_at")
    inlines = [OrderItemInline, PaymentInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "number", "status", "error", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("order__id", "number")
    readonly_fields = ("created_at",)
    