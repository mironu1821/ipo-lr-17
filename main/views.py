from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Product, Cart, ElemCart

def index(request):
    return render(request, 'main/index.html')

def product_list(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    manufacturer_id = request.GET.get('manufacturer', '')
    
    products = Product.objects.all()
    
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if category_id:
        products = products.filter(category_id=category_id)
    if manufacturer_id:
        products = products.filter(manufacturer_id=manufacturer_id)
        
    return render(request, 'main/product_list.html', {'products': products, 'query': query})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'main/product_detail.html', {'product': product})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, item_created = ElemCart.objects.get_or_create(cart=cart, product=product, defaults={'quantity': 1})
    
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()
        
    return redirect('catalog:cart_view')

@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(ElemCart, id=item_id, cart__user=request.user)
    try:
        new_quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        return HttpResponseBadRequest("Некорректное количество")
        
    if new_quantity > cart_item.product.stock:
        return HttpResponseBadRequest("Недостаточно товара на складе")
            
    cart_item.quantity = new_quantity
    cart_item.save()
    return redirect('catalog:cart_view')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(ElemCart, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('catalog:cart_view')

@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = ElemCart.objects.filter(cart=cart)
    total_cost = cart.total_price()
    return render(request, 'main/cart.html', {
        'cart_items': cart_items,
        'total_cost': total_cost
    })
