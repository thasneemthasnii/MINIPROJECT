from django.contrib import messages
from django.shortcuts import render, redirect
from marketplace_app.filters import CategoryFilter, ProductFilter, UserFilter
from marketplace_app.forms import AddCategory
from marketplace_app.models import Category, Item, Feedback, Order, User, Login


def admin_home(request):
    return render(request, 'admintemp/admin_home.html')


def users_view(request):
    user = User.objects.all()
    userFilter = UserFilter(request.GET, queryset=user)
    user = userFilter.qs
    context = {
        'users': user,
        'userFilter': userFilter,
    }
    return render(request, 'admintemp/users_view.html', context)


def user_delete(request, user_id):
    n = Login.objects.filter(id=user_id)
    if request.method == 'POST':
        n.delete()
        return redirect('users_view')
    else:
        return redirect('users_view')


def category_add(request):
    form = AddCategory()
    if request.method == 'POST':
        form = AddCategory(request.POST)
        if form.is_valid():
            form.save()
            messages.info(request, 'Category Added Successfully')
            return redirect('category')
    else:
        form = AddCategory()

    return render(request, 'admintemp/category_add.html', {'form': form})


def category(request):
    c = Category.objects.all()
    categoryFilter = CategoryFilter(request.GET, queryset=c)
    c = categoryFilter.qs
    context = {
        'category': c,
        'categoryFilter': categoryFilter,
    }
    return render(request, 'admintemp/category.html', context)


def category_update(request, id):
    n = Category.objects.get(id=id)
    if request.method == 'POST':
        form = AddCategory(request.POST or None, instance=n)
        if form.is_valid():
            form.save()
            return redirect('category')
    else:
        form = AddCategory(request.POST or None, instance=n)
    return render(request, 'admintemp/category_update.html', {'form': form})


def category_delete(request, id):
    n = Category.objects.get(id=id)
    if request.method == 'POST':
        n.delete()
        return redirect('category')
    else:
        return redirect('category')


def products_from_users(request):
    product = Item.objects.filter(approval_status=0)
    productFilter = ProductFilter(request.GET, queryset=product)
    product = productFilter.qs
    context = {
        'products': product,
        'productFilter': productFilter,
    }
    return render(request, 'admintemp/products_from_users.html', context)


def approve_product(request, id):
    n = Item.objects.get(id=id)
    n.approval_status = 1
    n.save()
    messages.info(request, 'Product Approved')
    return redirect('products_from_users')


def reject_product(request, id):
    n = Item.objects.get(id=id)
    if request.method == 'POST':
        n.approval_status = 2
        n.save()
        return redirect('products_from_users')
    else:
        return redirect('products_from_users')


def approved_products(request):
    product = Item.objects.filter(approval_status=1)
    productFilter = ProductFilter(request.GET, queryset=product)
    product = productFilter.qs
    context = {
        'products': product,
        'productFilter': productFilter,
    }
    return render(request, 'admintemp/approved_products.html', context)


def feedback_admin(request):
    feedback = Feedback.objects.all()
    return render(request, 'admintemp/feedback.html', {'feedbacks': feedback})


def orders_admin(request):
    order = Order.objects.filter(ordered=True)
    return render(request, 'admintemp/orders.html', {'orders': order})


def payments(request):
    order = Order.objects.all()
    return render(request, 'admintemp/payments.html', {'orders': order})
