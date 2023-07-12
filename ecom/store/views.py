from django.shortcuts import render, redirect
from .models import *
from django.http import JsonResponse
import json
import datetime
# from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth.models import Group
from django.views.decorators.csrf import csrf_exempt
from .decorators import unauthenticated_user
from .utils import cookieCart, cartData, guestOrder


@unauthenticated_user
def registerPage(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            customer = Customer()
            customer.name = user.username
            customer.email = user.email
            customer.user = user
            Customer.save(customer)
            username = form.cleaned_data.get('username')

            # group = Group.objects.get(name='staff')
            # user.groups.add(group)

            # group = Group.objects.get(name='staff')
            # user.groups.add(group)

            messages.success(request, 'Account was created for ' + username)

            return redirect('login')

    context = {'form': form}
    return render(request, 'store/register.html', context)


@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('store')
        else:
            messages.info(request, 'Username OR password is incorrect')

    context = {}
    return render(request, 'store/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')


# @login_required(login_url='login')
# @allowed_users(allowed_roles=['admin'])
def store(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    # if request.user.is_authenticated:
    #     customer = request.user.customer
    #     order, created = Order.objects.get_or_create(customer=customer, complete=False)
    #     items = order.orderitem_set.all()
    #     cartItems = order.get_cart_items
    # else:
    #     cookieData = cookieCart(request)
    #     cartItems = cookieData['cartItems']

    # customer = None
    # order, created = Order.objects.get_or_create(customer=customer, complete=False)
    # items = order.orderitem_set.all()
    # cartItems = order.get_cart_items

    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)


# @login_required(login_url='login')
# @allowed_users(allowed_roles=['admin'])
def cart(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    # if request.user.is_authenticated:
    #     customer = request.user.customer
    #     order, created = Order.objects.get_or_create(customer=customer, complete=False)
    #     items = order.orderitem_set.all()
    #     cartItems = order.get_cart_items
    # else:
    #     cookieData = cookieCart(request)
    #     cartItems = cookieData['cartItems']
    #     order = cookieData['order']
    #     items = cookieData['items']

    # Create empty cart for now for non-logged in user
    # customer = None
    # order, created = Order.objects.get_or_create(customer=customer, complete=False)
    # items = order.orderitem_set.all()
    # cartItems = order.get_cart_items

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)


# @login_required(login_url='login')
# @allowed_users(allowed_roles=['admin'])
def checkout(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    # if request.user.is_authenticated:
    #     customer = request.user.customer
    #     order, created = Order.objects.get_or_create(customer=customer, complete=False)
    #     items = order.orderitem_set.all()
    #     cartItems = order.get_cart_items
    # else:
    #     cookieData = cookieCart(request)
    #     cartItems = cookieData['cartItems']
    #     order = cookieData['order']
    #     items = cookieData['items']

    # Create empty cart for now for non-logged in user
    # items = []
    # order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
    # cartItems = order['get_cart_items']

    # customer = None
    # order, created = Order.objects.get_or_create(customer=customer, complete=False)
    # items = order.orderitem_set.all()
    # cartItems = order.get_cart_items
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)


# @login_required(login_url='login')
# @allowed_users(allowed_roles=['admin'])
def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', productId)
    # if request.user.is_authenticated:
    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()
    # else:
    # customer = None
    # product = Product.objects.get(id=productId)
    # order, created = Order.objects.get_or_create(customer=customer, complete=False)
    #
    # orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
    #
    # if action == 'add':
    #     orderItem.quantity = (orderItem.quantity + 1)
    # elif action == 'remove':
    #     orderItem.quantity = (orderItem.quantity - 1)
    #
    # orderItem.save()
    #
    # if orderItem.quantity <= 0:
    #     orderItem.delete()

    return JsonResponse('Item was added', safe=False)


# @allowed_users(allowed_roles=['admin'])
def view(request):
    context = {}
    return render(request, 'store/view.html', context)


@csrf_exempt
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse('Payment submitted..', safe=False)


def userPage(request):
    context = {}
    return render(request, 'store/user.html', context)
