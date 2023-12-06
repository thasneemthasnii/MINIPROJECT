import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Avg, Sum
from django.utils import timezone
from marketplace_app.filters import ProductFilter
from marketplace_app.forms import AddItem, CheckoutForm, PaymentForm, FeedbackForm, UserProfileUpdate, AcceptOrder

from marketplace_app.models import Category, User, Item, Order, OrderItem, Review, Earning


def user_home(request):
    customer = User.objects.get(user=request.user)

    item = Item.objects.filter(approval_status=1)
    category = Category.objects.all()
    categoryID = request.GET.get('category')
    rating = item.annotate(rat=Avg('reviews__rating')).order_by('-rat')[:3]

    if categoryID:
        item_list = Item.objects.filter(category=categoryID, approval_status=1)
    else:
        item_list = Item.objects.filter(approval_status=1)
    itemFilter = ProductFilter(request.GET, queryset=item_list)
    item_list = itemFilter.qs

    page = request.GET.get('page', 1)
    paginator = Paginator(item_list, 10)
    try:
        item = paginator.page(page)
    except PageNotAnInteger:
        item = paginator.page(1)
    except EmptyPage:
        item = paginator.page(paginator.num_pages)

    context = {
        'items': item,
        'categories': category,
        'ratings': rating,
        'itemFilter': itemFilter,
    }
    return render(request, 'shop/products.html', context)


def detail_view(request, id):
    item = Item.objects.filter(id=id)
    reviews_count = Review.objects.filter(item=id).count()
    context = {
        'items': item,
        'reviews_count': reviews_count,
    }
    if request.method == 'POST':
        rating = request.POST.get('rating')
        review = request.POST.get('review')
        obj = Review()
        obj.item = Item.objects.get(id=id)
        obj.user = User.objects.get(user=request.user)
        obj.rating = rating
        obj.review = review
        obj.save()
        return redirect('detail_view', id)
    return render(request, 'shop/detail_view.html', context)


def cart(request, ):
    try:
        customer = User.objects.get(user=request.user)
        order = Order.objects.filter(user=customer, ordered=False)
        total = sum(i.get_total() for i in Order.objects.filter(user=customer, ordered=False))

        context = {
            'object': order,
            'total': total

        }
        return render(request, 'shop/cart.html', context)
    except ObjectDoesNotExist:
        messages.warning(request, "You do not have an active order")
        return redirect("user_home")


def add_to_cart(request, id):
    item = get_object_or_404(Item, id=id)
    u = User.objects.get(user=request.user)
    if item.user == u:
        messages.info(request, "You Can't Order Your Own Products")
        return redirect('user_home')
    else:
        if item.instock == 0:
            messages.info(request, 'Product out of stock')
            return redirect('detail_view', item.id)
        else:
            order_item, created = OrderItem.objects.get_or_create(
                item=item,
                user=User.objects.get(user=request.user),
                ordered=False,
                seller=item.user
            )

            order_qs = Order.objects.filter(user=User.objects.get(user=request.user), ordered=False, seller=item.user)
            if order_qs.exists():
                order = order_qs[0]

                # check if the order item is in the order
                if order.items.filter(item_id=item.id).exists():
                    order_item.quantity += 1
                    order_item.save()
                    messages.info(request, "This item quantity was updated.")
                    return redirect("cart")
                else:
                    order.items.add(order_item)
                    messages.info(request, "This item was added to your cart.")
                    return redirect("cart")
            else:
                ordered_date = timezone.now()
                order = Order.objects.create(user=User.objects.get(user=request.user), ordered_date=ordered_date,
                                             seller=item.user)
                order.items.add(order_item)
                messages.info(request, "This item was added to your cart.")
                return redirect("cart")


def remove_from_cart(request, id):
    item = get_object_or_404(Item, id=id)
    order_qs = Order.objects.filter(
        user=User.objects.get(user=request.user),
        ordered=False,
        seller=item.user
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item_id=item.id).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=User.objects.get(user=request.user),
                ordered=False,
                seller=item.user
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "This item was removed from your cart.")

            return redirect("cart", )

        else:
            messages.info(request, "This item was not in your cart")
            return redirect("cart", )
    else:
        messages.info(request, "You do not have an active order")
        return redirect("cart", )


def remove_single_item_from_cart(request, id):
    item = get_object_or_404(Item, id=id)
    order_qs = Order.objects.filter(
        user=User.objects.get(user=request.user),
        ordered=False,
        seller=item.user
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item_id=item.id).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=User.objects.get(user=request.user),
                ordered=False,
                seller=item.user
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("cart")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("cart", )
    else:
        messages.info(request, "You do not have an active order")
        return redirect("cart", )


def checkout(request, ):
    user = User.objects.get(user=request.user)
    orders = Order.objects.filter(user=user, ordered=False)
    print(orders)
    cart_total = sum(i.get_total() for i in orders)

    addressform = CheckoutForm()
    if request.method == 'POST':
        addressform = CheckoutForm(request.POST)
        if addressform.is_valid():
            address = addressform.save(commit=False)
            address.user = User.objects.get(user=request.user)
            addressform.save()
            for order in orders:
                print(order)
                order.shipping_address = address
                order.save()
            return redirect('payment')
    context = {
        'addressform': addressform,
        'object': orders,
        'cart_total': cart_total,
    }
    return render(request, 'shop/checkout.html', context)


def payment(request, ):
    user = User.objects.get(user=request.user)
    orders = Order.objects.filter(user=user, ordered=False)
    cart_total = sum(i.get_total() for i in orders)
    payment_form = PaymentForm()
    context = {
        'payment_form': payment_form,
        'object': orders,
        'cart_total': cart_total,
    }
    if request.method == 'POST':
        payment_form = PaymentForm(request.POST)
        if payment_form.is_valid():
            pay = payment_form.save(commit=False)
            pay.user = User.objects.get(user=request.user)
            for order in orders:
                pay.amount = order.get_total()
                payment_form.save()
                order.ordered = True
                order.ordered_date = timezone.now()
                order.payment = pay
                order.amount = order.get_total()
                order.save()
                order_items = order.items.all()
                order_items.update(ordered=True)
                for item in order_items:
                    item.save()
                for item in order_items:
                    if item.item.quantity_sold == 0:
                        item.item.quantity_sold = item.quantity
                        item.item.instock = (item.item.instock) - (item.quantity)
                        item.item.save()
                    else:
                        item.item.quantity_sold = item.item.quantity_sold + item.quantity
                        item.item.instock = (item.item.instock) - (item.quantity)
                        item.item.save()

                for item in order_items:
                    earning = Earning()
                    it_qs = Earning.objects.filter(item=item.item.id)

                    if it_qs.exists():
                        it = it_qs[0]
                        it.quantity += item.quantity
                        it.total = (it.quantity) * (item.item.price)
                        it.save()

                    else:
                        earning.item = Item.objects.get(id=item.item.id)
                        earning.user = item.item.user
                        earning.quantity = item.quantity
                        earning.total = (earning.quantity) * (item.item.price)
                        earning.save()
            messages.info(request, 'Congratulations!! Your Order Placed Successfully')
            return redirect('order_status')
        else:
            context = {
                'payment_form': payment_form,
                'object': orders,
                'cart_total': cart_total,
            }

    return render(request, 'shop/payment.html', context)


def order_status(request):
    u = User.objects.get(user=request.user)
    order = Order.objects.filter(user=u, ordered=True)
    return render(request, 'shop/order_status.html', {'orders': order})


def add_feedback(request):
    form = FeedbackForm()
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feed = form.save(commit=False)
            feed.user = User.objects.get(user=request.user)
            feed.save()
            messages.info(request, 'Thank You for Your Feedback')
            return redirect('user_home')
    return render(request, 'shop/feedback.html', {'form': form})


def profile(request):
    profile = User.objects.filter(user=request.user)
    return render(request, 'shop/profile.html', {'profiles': profile})


def update_profile(request):
    profile = User.objects.get(user=request.user)
    form = UserProfileUpdate(request.POST or None, instance=profile)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileUpdate(instance=profile)
    return render(request, 'shop/update_profile.html', {'form': form})


def item_add(request):
    user = User.objects.get(user=request.user)
    item_list = Item.objects.filter(user=user)
    page = request.GET.get('page', 1)
    paginator = Paginator(item_list, 5)
    try:
        item = paginator.page(page)
    except PageNotAnInteger:
        item = paginator.page(1)
    except EmptyPage:
        item = paginator.page(paginator.num_pages)
    form = AddItem()
    context = {
        'form': form,
        'items': item
    }
    if request.method == 'POST':
        form = AddItem(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = User.objects.get(user=request.user)
            obj.save()
            messages.info(request, 'Item Successfully Added for Selling')
            return redirect('item_add')
    else:
        form = AddItem()
    return render(request, 'shop/items.html', context)


def update_item(request, id):
    item = Item.objects.get(id=id)
    if request.method == 'POST':
        stock = request.POST.get('stock')
        item.instock = stock
        item.save()
        return redirect('item_add')
    return render(request, 'shop/update_stock.html', {'item': item})


def delete_item(request,id):
    item = Item.objects.get(id=id)
    if request.method == 'POST':
        item.delete()
        return redirect('item_add')
    else:
        return redirect('item_add')


def orders_seller(request):
    u = User.objects.get(user=request.user)
    order = Order.objects.filter(seller=u, ordered=True)
    return render(request, 'shop/seller_orders.html', {'orders': order})


def accept_order(request, id):
    order = Order.objects.get(id=id)
    form = AcceptOrder()
    if request.method == 'POST':
        form = AcceptOrder(request.POST)
        if form.is_valid():
            date = form.cleaned_data['expected_delivery_date']
            order.accepted = True
            order.expected_delivery_date = date
            order.save()
            messages.info(request, 'Order Accepted Successfully')
            return redirect('orders_seller')
    return render(request, 'shop/accept_order.html', {'form': form})


def complete_order(request, id):
    order = Order.objects.get(id=id)
    order.received = True
    order.received_date = timezone.now()
    if order.accepted == False:
        messages.info(request, "You Haven't Accepted the Order Yet")
        return redirect('orders_seller')
    else:
        order.save()
        messages.info(request, 'Delivery Completed Successfully')
        return redirect('orders_seller')


def earnings(request):
    u = User.objects.get(user=request.user)
    earning = Earning.objects.filter(user=u)

    sum = Earning.objects.filter(user=u).aggregate(Sum('total'))['total__sum'] or 0.00
    context = {
        'earnings': earning,
        'sum': sum
    }
    return render(request, 'shop/earnings.html', context)
