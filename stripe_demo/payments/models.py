from django.core.validators import MinValueValidator
from django.db import models


class Item(models.Model):
    CURRENCY_CHOICES = [
        ("usd", "USD"),
        ("eur", "EUR"),
    ]

    name = models.CharField(max_length=200, blank=False)
    description = models.TextField(blank=False)
    price = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    currency = models.CharField(
        max_length=3, choices=CURRENCY_CHOICES, default="usd")

    def __str__(self) -> str:
        return f"{self.name} ({self.currency.upper()} {self.price})"


class Discount(models.Model):
    """
    Простой вариант: либо процент, либо фиксированная сумма (в минимальных единицах).
    Применение: уменьшаем итог на сервере и отдаём корректный unit_amount в Stripe.
    """
    name = models.CharField(max_length=120)
    percent_off = models.PositiveSmallIntegerField(
        null=True, blank=True)  # 1..100
    amount_off = models.PositiveIntegerField(null=True, blank=True)  # cents

    def clean(self):
        return super().clean()

    def __str__(self) -> str:
        if self.percent_off is not None:
            return f"{self.name} (-{self.percent_off}%)"
        return f"{self.name} (-{self.amount_off})"


class Tax(models.Model):
    """
    Налог: процент. (Можно расширить до фиксированного)
    """
    name = models.CharField(max_length=120)
    percent = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)])  # 1..100

    def __str__(self) -> str:
        return f"{self.name} (+{self.percent}%)"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    discounts = models.ManyToManyField(Discount, blank=True)
    taxes = models.ManyToManyField(Tax, blank=True)

    def __str__(self) -> str:
        return f"Order #{self.pk}"

    def subtotal(self) -> int:
        return sum(oi.item.price * oi.quantity for oi in self.items.all())

    def total(self) -> int:
        total = self.subtotal()

        # применим скидки
        for d in self.discounts.all():
            if d.percent_off is not None:
                total -= (total * d.percent_off) // 100
            elif d.amount_off is not None:
                total -= d.amount_off

        if total < 0:
            total = 0

        # применим налоги
        for t in self.taxes.all():
            total += (total * t.percent) // 100

        return total


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, related_name="items", on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1)])

    def __str__(self) -> str:
        return f"{self.order} - {self.item} x{self.quantity}"
