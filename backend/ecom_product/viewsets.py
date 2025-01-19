from django.forms import ValidationError
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.db import transaction
from django.db.models import F, Case, When, Prefetch
from .models import *
from .serializers import *

class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        category_list = serializer.data
        return Response({'category_list':category_list})

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        product_list = serializer.data
        return Response({"product_list": product_list})

class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer

class UserAddressViewSet(viewsets.ModelViewSet):
    queryset = UserAddress.objects.all()
    serializer_class = UserAddressSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserAddress.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        user_addresses = self.get_queryset()
        serializers = self.get_serializer(user_addresses, many=True)
        return Response({
            "user_addresses": serializers.data
        }, status=status.HTTP_200_OK)

# class CartViewSet(viewsets.ModelViewSet):
#     queryset = Cart.objects.all()
#     serializer_class = CartSerializer

# class CartItemViewSet(viewsets.ModelViewSet):
#     queryset = CartItem.objects.all()
#     serializer_class = CartItemSerializer

# class CartViewSet(viewsets.ModelViewSet):
#     queryset = Cart.objects.all()
#     serializer_class = CartSerializer

#     @action(detail=True, methods=['post'])
#     def add_item(self, request, pk=None):
#         cart = self.get_object()
#         product_id = request.data.get('product_id')
#         quantity = int(request.data.get('quantity', 1))

#         try:
#             product = Product.objects.get(id=product_id)
#         except Product.DoesNotExist:
#             return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        
#         #TODO check if the image is not available then raise error while adding product in cart.
#         cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
#         cart_item.quantity += quantity
#         cart_item.save()

#         serializer = self.get_serializer(cart)
#         return Response(serializer.data)
    
#     @action(detail=True, methods=['post'])
#     def remove_item(self, request, pk=None):
#         cart = self.get_object()
#         product_id = request.data.get('product_id')
#         quantity = int(request.data.get('quantity', 1))

#         try:
#             cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
#         except CartItem.DoesNotExist:
#             return Response({'error': "item not in cart"}, status=status.HTTP_404_NOT_FOUND)
        
#         if quantity >= cart_item.quantity:
#             cart_item.delete()
#         else:
#             cart_item.quantity -= quantity
#             cart_item.save()

#         serializer = self.get_serializer(cart)
#         return Response(serializer.data)
    
#     @action(detail=True, methods=['get'])
#     def cart_item(self, request, pk=None):
#         cart = self.get_object()
#         cart_items = cart.items.all()
#         serializer = CartItemSerializer(cart_items, many=True)
#         return Response({'cart_items': serializer.data})
    
# class CartItemViewSet(viewsets.ModelViewSet):
#     queryset = CartItem.objects.all()
#     serializer_class = CartItemSerializer


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # permission_classes = [IsAuthenticated] 

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        cart_order_list = serializer.data
        return Response({"cart_order_list": cart_order_list})
    
    @action(detail=False, methods=['GET'])
    def my_orders(self, request):
        """
        Get cart orders for the authenticated user
        """
        # Fetch all cart items for the current user
        user_carts = Cart.objects.filter(user=request.user).prefetch_related('items__product').order_by('-created_at')

        orders = []
        # Loop through carts and their items
        for cart in user_carts:
            order = {
                'cart_id': cart.id,
                'created_at': cart.created_at,
                'items': [],
            }

            for cart_item in cart.items.all():  # Access related CartItem objects
                cart_item_data = {
                    'order_item_id': cart_item.id,
                    'total_quantity': cart_item.quantity,
                    'products': [],
                }

                # Add details of products in the cart item
                for product in cart_item.product.all():  # Access related Product objects
                    product_images = product.images.all()
                    product_image_urls = [request.build_absolute_uri(image.image.url) for image in product_images]
                    cart_item_data['products'].append({
                        'product_id': product.id,
                        'product_name': product.name,
                        'description': product.description,
                        'price': product.price,
                        'quantity': cart_item.quantity,
                        'product_images': product_image_urls,
                    })

                # Add cart item to the order
                order['items'].append(cart_item_data)

            # Add the order to the orders list
            orders.append(order)

        return Response({
            'orders': orders
        }, status=status.HTTP_200_OK)


    @action(detail=False, methods=['post'])
    def add_to_create(self, request):
        """Optimized version of add_to_create"""
        if not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        items_data = request.data.get('items', [])
        transaction_id = request.data.get('transaction_id')
        address_id = request.data.get('address_id')

        # Early validation
        if not transaction_id:
            return Response({'error': 'Transaction ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not items_data:
            return Response({'error': 'No items provided'}, status=status.HTTP_400_BAD_REQUEST)

        # Get all required data in bulk
        try:
            # Get or create cart in a single query
            cart = Cart.objects.select_related('user').get_or_create(user=request.user)[0]

            # Improved address validation
            try:
                if address_id:
                    # Convert string address_id to integer
                    address_id = int(address_id)
                    user_address = UserAddress.objects.get(
                        id=address_id
                    )
                else:
                    user_address = UserAddress.objects.filter(
                        user=request.user,
                        is_default=True
                    ).first()

                if not user_address:
                    return Response({
                        'error': 'No valid address found. Please provide a valid address or set a default address.'
                    }, status=status.HTTP_400_BAD_REQUEST)

            except (ValueError, TypeError):
                return Response({
                    'error': 'Invalid address ID format'
                }, status=status.HTTP_400_BAD_REQUEST)
            except UserAddress.DoesNotExist:
                return Response({
                    'error': 'Address not found'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get all product IDs from items_data
            product_ids = [item['id'] for item in items_data]
            
            # Fetch all products and their images in a single query
            products = (Product.objects
                      .filter(id__in=product_ids)
                      .prefetch_related('images')
                      .select_related('category'))

            # Create a dictionary for quick product lookup
            products_dict = {str(p.id): p for p in products}

            # Validate products and quantities
            total_quantity = 0
            product_updates = []
            missing_products = []
            invalid_products = []

            for item in items_data:
                product_id = str(item['id'])
                cart_quantity = int(item.get('cart_quantity', 1))
                
                if product_id not in products_dict:
                    missing_products.append(product_id)
                    continue

                product = products_dict[product_id]
                
                if not product.images.exists():
                    invalid_products.append(f"Product {product.name} has no images")
                elif product.quantity < cart_quantity:
                    invalid_products.append(f"Insufficient stock for {product.name}")
                else:
                    total_quantity += cart_quantity
                    product_updates.append((product, cart_quantity))

            if missing_products or invalid_products:
                return Response({
                    'error': 'Validation failed',
                    'missing_products': missing_products,
                    'invalid_products': invalid_products
                }, status=status.HTTP_400_BAD_REQUEST)

            # Create CartItem and update products in a transaction
            with transaction.atomic():
                # Create cart item
                cart_item = CartItem.objects.create(
                    cart=cart,
                    quantity=total_quantity,
                    transaction_id=transaction_id,
                    user_address=user_address
                )

                # Add products to cart item
                cart_item.product.add(*[p for p, _ in product_updates])

                # Update product quantities in bulk
                product_quantity_cases = []
                for product, cart_quantity in product_updates:
                    product_quantity_cases.append(
                        When(id=product.id, then=F('quantity') - cart_quantity)
                    )

                Product.objects.filter(id__in=[p.id for p, _ in product_updates]).update(
                    quantity=Case(
                        *product_quantity_cases,
                        default=F('quantity'),
                        output_field=models.PositiveIntegerField()  # Explicitly set output field type
                    )
                )

            # Prepare response data
            response_data = [{
                'product_name': products_dict[str(item['id'])].name,
                'quantity': item.get('cart_quantity', 1),
                'status': 'added to cart'
            } for item in items_data]

            # Get only the newly created cart item data
            cart_item_serializer = CartItemSerializer(cart_item)

            total_price = sum(
                product.price * cart_item.quantity 
                for product in cart_item.product.all()
            )

            return Response({
                'message': 'Items added to cart successfully',
                'item_status': response_data,
                'order_data': {
                    'order_id': cart_item.id,
                    'transaction_id': cart_item.transaction_id,
                    'total_quantity': cart_item.quantity,
                    'total_price': str(total_price),
                    'products': [{
                        'id': product.id,
                        'name': product.name,
                        'price': str(product.price),
                        'image_url': product.images.first().image.url if product.images.exists() else None
                    } for product in cart_item.product.all()],
                    'delivery_address': {
                        'id': user_address.id,
                        'house_no': user_address.house_no,
                        'street': user_address.street,
                        'city': user_address.city,
                        'postal_code': user_address.postal_code,
                        'state': user_address.state,
                        'country': user_address.country
                    },
                    'status': cart_item.status,
                    'created_at': cart_item.cart.created_at
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)




class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Extract payment details from request data
        cart_item_id = request.data.get('cart_item')
        payment_id = request.data.get('payment_id')
        order_amount = request.data.get('order_amount')
        payment_status = request.data.get('status', 'success')  # Default to success if not provided

        # Validate required fields
        if not cart_item_id:
            return Response(
                {"error": "Cart item ID is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        if not payment_id:
            return Response(
                {"error": "Payment ID is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        if not order_amount:
            return Response(
                {"error": "Order amount is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get cart item
        cart_item = CartItem.objects.select_related('cart__user').get(
            id=cart_item_id,
            cart__user=request.user
        )

        # Create payment record
        payment = Payment.objects.create(
            cart_item=cart_item,
            payment_id=payment_id,
            status=payment_status,
            order_amount=order_amount,
            payment_response=request.data
        )

        serializer = self.get_serializer(payment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)