import stripe
from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET

from .models import Item, Order


def home(request):
    items = Item.objects.all().order_by("id")[:5]
    return render(request, "payments/home.html", {"items": items})


def _get_stripe_keys_for_currency(currency: str) -> dict:
    currency = (currency or "").lower()
    if currency not in settings.STRIPE_KEYS:
        raise ValueError(f"Unsupported currency: {currency}")
    keys = settings.STRIPE_KEYS[currency]
    if not keys["public"] or not keys["secret"]:
        raise ValueError(f"Stripe keys are not set for currency={currency}")
    return keys


@require_GET
def item_page(request: HttpRequest, id: int) -> HttpResponse:
    item = get_object_or_404(Item, pk=id)
    keys = _get_stripe_keys_for_currency(item.currency)
    return render(
        request,
        "payments/item.html",
        {"item": item, "stripe_public_key": keys["public"]},
    )


@require_GET
def buy_item(request: HttpRequest, id: int) -> JsonResponse:
    item = get_object_or_404(Item, pk=id)
    keys = _get_stripe_keys_for_currency(item.currency)
    stripe.api_key = keys["secret"]

    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=[{
                "price_data": {
                    "currency": item.currency,
                    "unit_amount": item.price,
                    "product_data": {
                        "name": item.name,
                        "description": item.description,
                    },
                },
                "quantity": 1,
            }],
            success_url=f"{settings.DOMAIN}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.DOMAIN}/cancel",
        )
        return JsonResponse({"id": session.id})

    except Exception as e:
        # Всегда JSON, чтобы фронт мог показать alert
        return JsonResponse({"error": str(e)}, status=502)


@require_GET
def order_page(request: HttpRequest, id: int) -> HttpResponse:
    order = get_object_or_404(Order, pk=id)

    # валюта заказа == валюта первого товара
    first = order.items.select_related("item").first()
    currency = first.item.currency if first else "usd"
    keys = _get_stripe_keys_for_currency(currency)

    return render(
        request,
        "payments/order.html",
        {"order": order,
            "stripe_public_key": keys["public"], "currency": currency},
    )


@require_GET
def buy_order(request: HttpRequest, id: int) -> JsonResponse:
    order = get_object_or_404(Order, pk=id)
    order_items = order.items.select_related("item").all()

    if not order_items:
        return JsonResponse({"error": "Order is empty"}, status=400)

    currency = order_items[0].item.currency
    if any(oi.item.currency != currency for oi in order_items):
        return JsonResponse(
            {"error": "Mixed currencies in one order are not supported in this demo"},
            status=400,
        )

    keys = _get_stripe_keys_for_currency(currency)
    stripe.api_key = keys["secret"]

    line_items = []
    for oi in order_items:
        line_items.append({
            "price_data": {
                "currency": oi.item.currency,
                "unit_amount": oi.item.price,  # важно: int в минимальных единицах валюты
                "product_data": {
                    "name": oi.item.name,
                    "description": oi.item.description,
                },
            },
            "quantity": oi.quantity,
        })

    subtotal = order.subtotal()
    total = order.total()
    adjustment = total - subtotal

    # Важно: в Checkout нельзя передать отрицательный unit_amount.
    # Поэтому если adjustment < 0, уменьшаем первую позицию.
    if adjustment > 0:
        line_items.append({
            "price_data": {
                "currency": currency,
                "unit_amount": adjustment,
                "product_data": {"name": "Tax/Discount adjustment"},
            },
            "quantity": 1,
        })
    elif adjustment < 0:
        discount_abs = -adjustment
        first_item = line_items[0]
        first_amount = first_item["price_data"]["unit_amount"]
        first_item["price_data"]["unit_amount"] = max(
            0, first_amount - discount_abs)

    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=line_items,
            success_url=f"{settings.DOMAIN}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.DOMAIN}/cancel",
        )
        return JsonResponse({"id": session.id})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=502)


@require_GET
def success(request: HttpRequest) -> HttpResponse:
    return render(request, "payments/success.html", {"session_id": request.GET.get("session_id")})


@require_GET
def cancel(request: HttpRequest) -> HttpResponse:
    return render(request, "payments/cancel.html")
