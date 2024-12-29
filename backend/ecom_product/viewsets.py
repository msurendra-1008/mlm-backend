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
        items_data = request.data
        response_data = []

        for item in items_data:
            try:
                product = Product.objects.get(id=item['id'])
                cart_quantity = item.get('cartQuantity',1)

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
                
                # Get or create cart item
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=product,
                )

                # Update quantity
                if created:
                    cart_item.quantity = cart_quantity
                else:
                    cart_item.quantity += cart_quantity
                cart_item.save()

                # Add to response data
                response_data.append({
                    'product_name': product.name,
                    'quantity': cart_item.quantity,
                    'status': 'added to cart'
                })
            except Product.DoesNotExist:
                return Response(
                    {'error': f'Product with id {item["id"]} not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        cart_serializer = self.get_serializer(cart)
        return Response({
            'message': 'Items added to cart successfully',
            'item_status': response_data,
            'cart_data': cart_serializer.data
        }, status=status.HTTP_200_OK)
