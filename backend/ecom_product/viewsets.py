from collections import defaultdict
from decimal import Decimal, InvalidOperation
from django.forms import ValidationError
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import generics
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination
from django.db import transaction
from django.db.models import F, Case, When, Prefetch
from .models import *
from .serializers import *



class GeneralIncomePagination(PageNumberPagination):
    page_size = 10

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
    

class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(wallet)
        return Response({"wallet":serializer.data}, status=status.HTTP_201_CREATED)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"wallet": serializer.data})
    
class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(wallet__user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        amount = request.data.get('amount')
        transaction_type = request.data.get('transaction_type')
        description = request.data.get('description', '')

        # Convert amount to Decimal
        try:
            amount = Decimal(amount)  # Convert to Decimal
        except (ValueError, InvalidOperation):
            return Response({'error': "Invalid amount format"}, status=status.HTTP_400_BAD_REQUEST)

        if transaction_type == 'debited' and wallet.balance < amount:
            return Response({'error': "Insufficient Balance"}, status=status.HTTP_400_BAD_REQUEST)
        
        if transaction_type == 'credited':
            wallet.balance += amount
        elif transaction_type == 'debited':
            wallet.balance -= amount

        wallet.save()

        transaction = Transaction.objects.create(
            wallet=wallet,
            amount=amount,
            transaction_type=transaction_type,
            description=description
        )

        serializer = self.get_serializer(transaction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"transactions": serializer.data})  # Wrap the data in a dictionary
    
    
class VendorViewSet(viewsets.ModelViewSet):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        try:
            vendor = self.get_object()
            vendor.is_approved = True
            vendor.save()
            serializer = self.get_serializer(vendor)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Vendor.DoesNotExist:
            return Response({"error": "Vendor not found"}, status=status.HTTP_404_NOT_FOUND)

    def get_queryset(self):
        approved_only = self.request.query_params.get('approved', 'false').lower() == 'true'
        queryset = Vendor.objects.all()
        if approved_only:
            queryset = queryset.filter(is_approved=True)
        return queryset
    

class TenderViewSet(viewsets.ModelViewSet):
    queryset = Tender.objects.all().order_by('-created_at')
    serializer_class = TenderSerializer
    pagination_class = GeneralIncomePagination
    

class OpenTendersView(generics.ListAPIView):
    queryset = Tender.objects.filter(status='open', deadline__gt=timezone.now())
    serializer_class = TenderSerializer


class TenderBidViewSet(viewsets.ModelViewSet):
    queryset = TenderBid.objects.all()
    serializer_class = TenderBidSerializer
    pagination_class = GeneralIncomePagination

    def create(self, request, *args, **kwargs):
        vendor_email = request.data.get('vendor_email') 
        tender_id = request.data.get('tender_id')

        vendor = Vendor.objects.filter(email=vendor_email, is_approved=True).first()
        if not vendor:
            return Response({"detail": "Vendor not found or not approved."}, status=400)

        tender = Tender.objects.filter(id=tender_id).first()
        if not tender:
            return Response({"detail": "Tender not found."}, status=400)

        if TenderBid.objects.filter(vendor=vendor, tender=tender).exists():
            return Response({"detail": "You have already submitted a bid for this tender."}, status=400)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(vendor=vendor, tender=tender)
        return Response(serializer.data, status=201)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        bid = self.get_object()
        status = request.data.get('status')
        negotiation_message = request.data.get('negotiation_message', '')

        if status not in ['approved', 'rejected', 'negotiation']:
            return Response({'detail': 'Invalid status.'}, status=400)

        bid.status = status
        bid.negotiation_message = negotiation_message if status == 'negotiation' else ''
        bid.save()

        return Response(self.get_serializer(bid).data)
    

class TenderBidPreRequsitViewSet(viewsets.ViewSet):
    
    @action(detail=False, methods=['get'], url_path='awarded-status')
    def awarded_tenders(self, request):
        awarded_tenders = Tender.objects.filter(status="awarded")
        serializer = TenderSerializer(awarded_tenders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='approved_bids')
    def approved_bids(self, request, pk=None):
        try:
            tender = Tender.objects.get(id=pk)
        except Tender.DoesNotExist:
            return Response({"error": "Tender not found."}, status=status.HTTP_404_NOT_FOUND)

        if tender.status != "awarded":
            return Response({"error": "Tender is not awarded."}, status=status.HTTP_400_BAD_REQUEST)

        approved_bids = TenderBid.objects.filter(tender=tender, status="approved")
        serializer = TenderBidSerializer(approved_bids, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RawProductListViewSet(viewsets.ModelViewSet):
    queryset = RawProductList.objects.all().order_by('-created_at')
    serializer_class = RawProductListSerializer
    pagination_class = GeneralIncomePagination

    def get_queryset(self):
        queryset = super().get_queryset()
        tender_bid = self.request.query_params.get('tender_bid')
        if tender_bid:
            queryset = queryset.filter(tender_bid_id=tender_bid)
        return queryset

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        raw_list = self.get_object()
        raw_list.status = 'approved'
        raw_list.save()
        return Response({'message': 'Raw list approved'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        raw_list = self.get_object()
        raw_list.status = 'rejected'
        raw_list.save()
        return Response({'message': 'Raw list rejected'}, status=status.HTTP_200_OK)

    # @action(detail=False, methods=['get'], url_path='approved-lists')
    # def approved_lists(self, request):
    #     approved_lists = RawProductList.objects.filter(status='approved')
    #     serializer = RawProductListSerializer(approved_lists, many=True)
    #     return Response(serializer.data)
    @action(detail=False, methods=['get'], url_path='approved-lists')
    def approved_lists(self, request):
        approved_lists = RawProductList.objects.filter(status='approved')
        grouped = defaultdict(lambda: {
            "tender_bid": None,
            "tender": None,
            "tender_title": None,
            "tender_product_no": None,  # Add this
            "vendor": None,
            "batch_lists": [],
            "approved_batches_count": 0
        })

        for raw_list in approved_lists:
            tender_bid_id = raw_list.tender_bid_id
            if grouped[tender_bid_id]["tender_bid"] is None:
                grouped[tender_bid_id]["tender_bid"] = tender_bid_id
                grouped[tender_bid_id]["tender"] = raw_list.tender_id
                grouped[tender_bid_id]["vendor"] = raw_list.vendor_id
                grouped[tender_bid_id]["tender_title"] = raw_list.tender.title
                grouped[tender_bid_id]["tender_product_no"] = raw_list.tender.tender_product_no  # Add this

            # Serialize the RawProductList (reuse your serializer)
            serializer = RawProductListSerializer(raw_list)
            grouped[tender_bid_id]["batch_lists"].append(serializer.data)
            # Add the number of batches for this list
            grouped[tender_bid_id]["approved_batches_count"] += raw_list.batches.count()
        grouped_list = list(grouped.values())

        # Apply pagination
        page = self.paginate_queryset(grouped_list)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(grouped_list)

    @action(detail=False, methods=['get'], url_path='by-tenderbid/(?P<tenderbid_id>[^/]+)')
    def by_tenderbid(self, request, tenderbid_id=None):
        # Filter RawProductList by tender_bid and status approved
        raw_lists = RawProductList.objects.filter(tender_bid_id=tenderbid_id, status='approved')
        serializer = RawProductListSerializer(raw_lists, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='batches-list-by-tenderbid/(?P<tenderbid_id>[^/]+)')
    def batches_list_by_tenderbid(self, request, tenderbid_id=None):
        # Get all approved RawProductList for this tenderbid
        '''
        For send email making list of all batches and then send email to vendor

        {
            "tender": 9,
            "tender_title": "milk PRODUCT",
            "vendor": 3,
            "vendor_name": "Test User1",
            "tender_bid": 7,
            "batches_list": [
                {
                    "id": 1,
                    "delivery_date": "2025-08-14",
                    "quantity": 100
                },
                {
                    "id": 2,
                    "delivery_date": "2025-08-16",
                    "quantity": 200
                },
                {
                    "id": 3,
                    "delivery_date": "2025-08-18",
                    "quantity": 200
                }
            ]
        }
        
        '''
        raw_lists = RawProductList.objects.filter(tender_bid_id=tenderbid_id, status='approved')
        if not raw_lists.exists():
            return Response({"detail": "No approved lists found for this tenderbid."}, status=404)

        # Get shared info from the first RawProductList (since all have the same tender, vendor, tender_bid)
        first = raw_lists.first()
        tender_id = first.tender_id
        vendor_id = first.vendor_id
        tender_bid_id = first.tender_bid_id
        tender_title = first.tender.title
        vendor_name = first.vendor.name

        # Collect all batches
        batches = []
        for raw_list in raw_lists:
            for batch in raw_list.batches.all():
                batches.append({
                    "id": batch.id,
                    "delivery_date": batch.delivery_date,
                    "quantity": batch.quantity
                })

        result = {
            "tender": tender_id,
            "tender_title": tender_title,
            "vendor": vendor_id,
            "vendor_name": vendor_name,
            "tender_bid": tender_bid_id,
            "batches_list": batches
        }
        return Response(result)

    @action(detail=False, methods=['post'], url_path='send-batches-email/(?P<tenderbid_id>[^/]+)')
    def send_batches_email(self, request, tenderbid_id=None):
        raw_lists = RawProductList.objects.filter(tender_bid_id=tenderbid_id, status='approved')
        if not raw_lists.exists():
            return Response({"detail": "No approved lists found for this tenderbid."}, status=404)

        first = raw_lists.first()
        vendor_email = first.vendor.email
        vendor_name = first.vendor.name
        tender_title = first.tender.title
        tender_bid_id = first.tender_bid_id

        # Collect all unsent batches
        batches = []
        batch_ids = []
        for raw_list in raw_lists:
            for batch in raw_list.batches.filter(sent_to_vendor=False):
                batches.append(batch)
                batch_ids.append(batch.id)

        if not batches:
            return Response({"detail": "No unsent batches to email."}, status=400)

        # Compose email
        subject = f"Batch Packing Details for Tender: {tender_title}"
        batch_lines = [
            f"- Batch ID: {batch.id}, Delivery Date: {batch.delivery_date}, Quantity: {batch.quantity}"
            for batch in batches
        ]
        batch_details = "\n".join(batch_lines)
        message = (
            f"Dear {vendor_name},\n\n"
            f"We are pleased to inform you that the following batches for your tender bid (ID: {tender_bid_id}) have been approved and are ready for packing:\n\n"
            f"{batch_details}\n\n"
            "Please proceed with the necessary arrangements for these batches.\n\n"
            "If you have any questions or require further information, feel free to contact us.\n\n"
            "Best regards,\n"
            "Your Company Name\n"
            "Contact: support@yourcompany.com"
        )

        # Send email (replace with your actual email sending logic)
        from django.core.mail import send_mail
        send_mail(subject, message, 'your_email@example.com', [vendor_email])

        # Mark batches as sent
        RawProductListBatch.objects.filter(id__in=batch_ids).update(sent_to_vendor=True)

        return Response({
            "detail": "Email sent successfully.",
            "batches_sent": batch_ids
        })

    @action(detail=False, methods=['get'], url_path='batches-pdf-by-tenderbid/(?P<tenderbid_id>[^/]+)')
    def batches_pdf_by_tenderbid(self, request, tenderbid_id=None):
        from django.http import HttpResponse
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib import colors
        from reportlab.platypus import Table, TableStyle
        import io

        raw_lists = RawProductList.objects.filter(tender_bid_id=tenderbid_id, status='approved')
        if not raw_lists.exists():
            return Response({"detail": "No approved lists found for this tenderbid."}, status=404)

        first = raw_lists.first()
        vendor_name = first.vendor.name
        tender_title = first.tender.title
        tender_bid_id = first.tender_bid_id

        # Collect all batches (no sent_to_vendor filter)
        batches = []
        total_quantity = 0
        for raw_list in raw_lists:
            for batch in raw_list.batches.all():
                batches.append(batch)
                total_quantity += batch.quantity

        if not batches:
            return Response({"detail": "No batches to include in PDF."}, status=400)

        # Create PDF in memory
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        y = height - 50
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y, f"Batch Packing Details for Tender: {tender_title}")
        y -= 30
        p.setFont("Helvetica", 12)
        p.drawString(50, y, f"Vendor: {vendor_name}")
        y -= 20
        p.drawString(50, y, f"Tender Bid ID: {tender_bid_id}")
        y -= 30

        # Prepare table data
        table_data = [["Batch ID", "Delivery Date", "Quantity"]]
        for batch in batches:
            table_data.append([str(batch.id), str(batch.delivery_date), str(batch.quantity)])
        # Add total row
        table_data.append(["", "Total", str(total_quantity)])

        # Create table
        table = Table(table_data, colWidths=[100, 150, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ]))

        # Render table
        table.wrapOn(p, width, height)
        table_height = 20 * (len(table_data))
        table.drawOn(p, 50, y - table_height)
        p.showPage()
        p.save()
        buffer.seek(0)

        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="batches_tenderbid_{tender_bid_id}.pdf"'
        return response


class ReceivedOrderViewSet(viewsets.ModelViewSet):
    queryset = ReceivedOrder.objects.all().order_by('received_at')
    serializer_class = ReceivedOrderSerializer
    pagination_class = GeneralIncomePagination

    @action(detail=True, methods=['post'], url_path='inspect')
    def inspect_order(self, request, pk=None):
        order = self.get_object()
        inspection_status = request.data.get('inspection_status')
        if inspection_status not in ['inspected']:
            return Response({'detail': 'Invalid inspection status.'}, status=400)
        order.inspection_status = inspection_status
        order.save()
        return Response(self.get_serializer(order).data)

    @action(detail=False, methods=['get'], url_path='filter-batches')
    def filter_batches(self, request):
        vendor_id = request.query_params.get('vendor_id')
        tender_id = request.query_params.get('tender_id')
        
        if vendor_id and tender_id:
            batches = RawProductListBatch.objects.filter(
                raw_list__vendor_id=vendor_id,
                raw_list__tender_id=tender_id
            )
            serializer = RawProductListBatchSerializer(batches, many=True)
            return Response(serializer.data)
        
        return Response({"detail": "Vendor and Tender IDs are required."}, status=400)


class FaultyItemViewSet(viewsets.ModelViewSet):
    queryset = FaultyItem.objects.all().order_by('reported_at')
    serializer_class = FaultyItemSerializer
    pagination_class = GeneralIncomePagination


class AcceptedProductViewSet(viewsets.ModelViewSet):
    queryset = AcceptedProduct.objects.all().order_by('accepted_at')
    serializer_class = AcceptedProductSerializer
    pagination_class = GeneralIncomePagination