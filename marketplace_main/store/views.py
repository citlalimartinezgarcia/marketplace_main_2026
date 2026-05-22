# =========================================================
# store/views.py
# =========================================================

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from .forms import ProductForm
from .models import (
    Product,
    Cart,
    CartItem
)


# =========================================================
# 🏠 HOME
# =========================================================
def home(request):
    return render(request, 'home.html')


# =========================================================
# 👤 REGISTER
# =========================================================
def register(request):
    return render(request, 'register.html')


# =========================================================
# 🔐 LOGIN
# =========================================================
def login_view(request):
    return render(request, 'login.html')


# =========================================================
# 🚪 LOGOUT
# =========================================================
def logout_view(request):
    return redirect('home')


# =========================================================
# 📊 DASHBOARD
# =========================================================
@login_required
def dashboard(request):

    if not request.user.is_seller:
        return HttpResponseForbidden(
            "No tienes permisos"
        )

    products = Product.objects.filter(
        owner=request.user
    )

    return render(
        request,
        'store/dashboard.html',
        {
            'products': products
        }
    )


# =========================================================
# ➕ CREAR PRODUCTO
# =========================================================
@login_required
def product_create(request):

    if not request.user.is_seller:
        return HttpResponseForbidden(
            "Solo vendedores"
        )

    form = ProductForm(
        request.POST or None
    )

    if form.is_valid():

        product = form.save(
            commit=False
        )

        product.owner = request.user

        product.save()

        form.save_m2m()

        return redirect('dashboard')

    return render(
        request,
        'store/product_form.html',
        {
            'form': form
        }
    )


# =========================================================
# ✏️ EDITAR PRODUCTO
# =========================================================
@login_required
def product_update(request, pk):

    product = get_object_or_404(
        Product,
        pk=pk
    )

    if product.owner != request.user:
        return HttpResponseForbidden(
            "No puedes editar este producto"
        )

    form = ProductForm(
        request.POST or None,
        instance=product
    )

    if form.is_valid():

        form.save()

        return redirect('dashboard')

    return render(
        request,
        'store/product_form.html',
        {
            'form': form
        }
    )


# =========================================================
# 🗑️ ELIMINAR PRODUCTO
# =========================================================
@login_required
def product_delete(request, pk):

    product = get_object_or_404(
        Product,
        pk=pk
    )

    if product.owner != request.user:
        return HttpResponseForbidden(
            "No puedes eliminar este producto"
        )

    if request.method == 'POST':

        product.delete()

        return redirect('dashboard')

    return render(
        request,
        'store/product_confirm_delete.html',
        {
            'product': product
        }
    )


# =========================================================
# 🛒 VER CARRITO
# =========================================================
@login_required
def cart_detail(request):

    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    return render(
        request,
        'store/cart_detail.html',
        {
            'cart': cart
        }
    )


# =========================================================
# ➕ AGREGAR AL CARRITO
# =========================================================
@login_required
def add_to_cart(request, product_id):

    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    product = get_object_or_404(
        Product,
        id=product_id
    )

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:

        cart_item.quantity += 1

        cart_item.save()

    return redirect('cart_detail')


# =========================================================
# ❌ ELIMINAR ITEM
# =========================================================
@login_required
def remove_from_cart(request, item_id):

    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    item.delete()

    return redirect('cart_detail')


# =========================================================
# 🔄 ACTUALIZAR CANTIDAD
# =========================================================
@login_required
def update_cart_item(request, item_id):

    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    if request.method == 'POST':

        quantity = int(
            request.POST.get('quantity', 1)
        )

        if quantity > 0:

            item.quantity = quantity

            item.save()

        else:

            item.delete()

    return redirect('cart_detail')


# =========================================================
# store/urls.py
# =========================================================

from django.urls import path
from . import views

urlpatterns = [

    # 🏠 HOME
    path(
        '',
        views.home,
        name='home'
    ),

    # 👤 AUTH
    path(
        'register/',
        views.register,
        name='register'
    ),

    path(
        'login/',
        views.login_view,
        name='login'
    ),

    path(
        'logout/',
        views.logout_view,
        name='logout'
    ),

    # 📊 DASHBOARD
    path(
        'dashboard/',
        views.dashboard,
        name='dashboard'
    ),

    # 📦 PRODUCTOS
    path(
        'product/create/',
        views.product_create,
        name='product_create'
    ),

    path(
        'product/<uuid:pk>/update/',
        views.product_update,
        name='product_update'
    ),

    path(
        'product/<uuid:pk>/delete/',
        views.product_delete,
        name='product_delete'
    ),

    # 🛒 CARRITO
    path(
        'cart/',
        views.cart_detail,
        name='cart_detail'
    ),

    path(
        'cart/add/<uuid:product_id>/',
        views.add_to_cart,
        name='add_to_cart'
    ),

    path(
        'cart/remove/<uuid:item_id>/',
        views.remove_from_cart,
        name='remove_from_cart'
    ),

    path(
        'cart/update/<uuid:item_id>/',
        views.update_cart_item,
        name='update_cart_item'
    ),
]