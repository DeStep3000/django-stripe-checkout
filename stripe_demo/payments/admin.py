from django import forms
from django.contrib import admin

from .models import Discount, Item, Order, OrderItem, Tax


class ItemAdminForm(forms.ModelForm):
    """Валидация полей Item на уровне админки (чтобы не улетать в Stripe с пустыми значениями)."""

    class Meta:
        model = Item
        fields = "__all__"

    def clean_name(self) -> str:
        name = (self.cleaned_data.get("name") or "").strip()
        if not name:
            raise forms.ValidationError("Название товара обязательно.")
        return name

    def clean_description(self) -> str:
        desc = (self.cleaned_data.get("description") or "").strip()
        if not desc:
            raise forms.ValidationError(
                "Описание обязательно. Пустое описание может привести к ошибке Stripe при создании Checkout Session."
            )
        return desc


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    form = ItemAdminForm
    list_display = ("id", "name", "price", "currency")
    search_fields = ("name",)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at")
    inlines = [OrderItemInline]
    filter_horizontal = ("discounts", "taxes")


admin.site.register(Discount)
admin.site.register(Tax)
