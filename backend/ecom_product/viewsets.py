from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
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
        # Ensure the user is authenticated
        if not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        # Get or create cart for the current user
        cart, created = Cart.objects.get_or_create(user=request.user)

        # Get the items data from request
        items_data = request.data.get('items', [])
        address_id = request.data.get('address_id')
        transaction_id = request.data.get('transation_id')
        # is_payment = request.data.get('is_payment')

        # validate or fetch default address
        try:
            if address_id:
                user_address = UserAddress.objects.get(id=address_id, user=request.user)
            else:
                user_address = UserAddress.objects.filter(user=request.user, is_default=True)
                if not user_address:
                    return Response({
                        'error': 'No deefault address available for this user.'
                    }, status=status.HTTP_400_BAD_REQUEST)
        except UserAddress.DoesNotExist:
            return Response({'error': 'Invalid adress ID'}, status=status.HTTP_400_BAD_REQUEST)
        

        response_data = []

        for item in items_data:
            quantity = 0
            cart_product = []

            for item in item['product']:
                try:
                    product = Product.objects.get(id=item['id'])
                    cart_quantity = item.get('cart_quantity', 1)

                    # check if product has image
                    if not product.images.exists():
                        return Response(
                            {'error': f'Product {product.name} must have atleast one image'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    
                    # check if product has enough quantity
                    if product.quantity < cart_quantity:
                        return Response(
                            {'error': f'Not enough quantity available for {product.name}'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    
                    cart_product.append(product)
                    quantity += cart_quantity

                    # decrease the product quntity
                    product.quantity -= cart_quantity
                    product.save()

                except Product.DoesNotExist:
                    return Response(
                        {'error': f'Product with id {item["id"]} not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            if not transaction_id:
                return Response({'error': 'No payment and transaction id provided'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Create CartItem with multiple products
            cart_item = CartItem.objects.create(
                cart=cart,
                quantity=quantity
            )
            cart_item.products.set(cart_product)  # Associate multiple products with the cart item

            # Save cart item and respond with the details
            cart_item.save()

            response_data.append({
                'products': [product.name for product in cart_product],
                'quantity': quantity,
                'status': 'added to cart'
            })

        cart_serializer = self.get_serializer(cart)

        return Response({
            'message': 'Items added to cart successfully',
            'item_status': response_data,
            'cart_data': cart_serializer.data
        }, status=status.HTTP_200_OK)
