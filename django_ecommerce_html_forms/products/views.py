from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound

from products.models import Product, Category, ProductImage


def products(request):
    # Get all products from the DB using the Product model
    products = Product.objects.all()

    # Get up to 4 `featured=true` Products to be displayed on top
    featured_products = products.filter(featured=True)[:4]

    return render(
        request,
        'products.html',
        context={'products': products, 'featured_products': featured_products}
    )


def create_product(request):
    # Get all categories from the DB
    categories = Category.objects.all()
    if request.method == 'GET':
        # Render 'create_product.html' template sending categories as context
        return render(request, 'create_product.html')  # static_form is just used as an example
    elif request.method == 'POST':
        # Validate that all fields below are given in request.POST dictionary,
        # and that they don't have empty values.

        # If any errors, build an errors dictionary with the following format
        # and render 'create_product.html' sending errors and categories as context

        # errors = {'name': 'This field is required.'}
        fields = ['name', 'sku', 'price']
        errors = {}
        # <YOUR CODE HERE>
        
        for field in fields:
            if not request.POST.get(field):
                errors[field] = 'This field is required.'
        
        if errors:
            return render(request,'create_product.html',context={
                'categories':categories,
                'errors':errors,

            })
            

        # If no errors so far, validate each field one by one and use the same
        # errors dictionary created above in case that any validation fails

        # name validation: can't be longer that 100 characters

        # Validate name
        name = request.POST.get('name')
        if len(name) > 100:
            errors['name'] = "Name can't be longer than 100 characters."

        # Validate sku
        sku = request.POST.get('sku')
        if len(sku) != 8:
            errors['sku'] = "SKU must contain 8 alphanumeric characters."

        # Validate price
        price = request.POST.get('price')
        if float(price) < 0 or float(price) > 9999.99 :
            errors['price'] = "Price can't be negative or greater than $9999.9"

        if errors:
            return render(
                request,
                'create_product.html',
                context={
                    'categories': categories,
                    'errors': errors,
                    'payload': request.POST
                }
)
        # If execution reaches this point, there aren't any errors.
        # Get category from DB based on category name given in payload.
        # Create product with data given in payload and proper category
        category = Category.objects.get(name=request.POST.get('category'))
        product = Product.objects.create(name=request.POST.get('name'),sku=request.POST.get('sku'),price=float(request.POST.get('price')),description=request.POST.get('description', ''),category=category)       

        # Up to three images URLs can come in payload with keys 'image-1', 'image-2', etc.
        # For each one, create a ProductImage object with proper URL and product
        
        images = []
        for i in range(3):
            image = request.POST.get('image_{}'.format(i + 1))
            if image:
                images.append(image)

        for image in images:
            ProductImage.objects.create(
                product=product,
                url=image
                )

        # Redirect to 'products' view
        return redirect('products')


def edit_product(request, product_id):
    product = Product.objects.get(id=product_id)
    categories = Category.objects.all()
    
    try:
        images = [image.url for image in product.productimage_set.all()]
    except:
        pass

    if request.method == 'GET':
        return render(
            request,
            'edit_product.html',
            context={
                'product': product,
                'categories': categories,
                'images': images
            }
)
    elif request.method == 'POST':
        # Validate following fields that come in request.POST in the very same
        # way that you've done it in create_product view
        fields = ['name', 'sku', 'price']
        errors = {}
        
        for field in fields:
            if not request.POST.get(field):
                errors[field] = 'This field is required.'
        
        if errors:
            return render(request,'edit_product.html',context={
                'categories':categories,
                'errors':errors,
                'images': images
            })

        # Validate name
        name = request.POST.get('name')
        if len(name) > 100:
            errors['name'] = "Name can't be longer than 100 characters."

        # Validate sku
        sku = request.POST.get('sku')
        if len(sku) != 8:
            errors['sku'] = "SKU must contain 8 alphanumeric characters."

        # Validate price
        price = request.POST.get('price')
        if float(price) < 0 or float(price) > 9999.99 :
            errors['price'] = "Price can't be negative or greater than $9999.9"

        # If execution reaches this point, there aren't any errors.
        # Update product name, sku, price and description from the data that
        # come in request.POST dictionary.
        # Consider that ALL data is given as string, so you might format it
        # properly in some cases.
        product.name = name
        product.sku = sku
        product.price = float(price)
        product.description = request.POST.get('description')
        product.save()

        # Get proper category from the DB based on the category name given in
        # payload. Update product category.


        # For updating the product images URLs, there are a couple of things that
        # you must consider:
        # 1) Create a ProductImage object for each URL that came in payload and
        #    is not already created for this product.


        new_images = []
        for i in range(3):
            image = request.POST.get('image-{}'.format(i + 1))
            if image:
                new_images.append(image)

        old_images = [image.url for image in product.productimage_set.all()]

        # delete images that didn't come in current payload
        images_to_delete = []
        for image in old_images:
            if image not in new_images:
                images_to_delete.append(image)
        ProductImage.objects.filter(url__in=images_to_delete).delete()

        # create images that came in payload and are not created yet
        for image in new_images:
            if image not in old_images:
                ProductImage.objects.create(
                    product=product,
                    url=image
)

        # Redirect to 'products' view
        return redirect('products')


def delete_product(request, product_id):
    product = Product.objects.get(id=product_id)
    if request.method == 'GET':
        return render(request, 'delete_product.html', context={'product': product})
    elif request.method == "POST":
        product.delete()
    return redirect('products')


def toggle_featured(request, product_id):
    # Get product with given product_id
    product = Product.objects.get(id=product_id)

    # Toggle product featured flag
    if product.featured is True:
        product.featured = False
    else:
        product.featured = True
    product.save()

    # Redirect to 'products' view
    return redirect('products')
