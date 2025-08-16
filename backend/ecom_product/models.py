from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _




class Vendor(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15)
    address = models.TextField()
    product = models.TextField(blank=True, null=True)
    gst_number = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Tender(models.Model):
    tender_product_no = models.PositiveIntegerField(unique=True,blank=True, null=True)
    title = models.CharField(max_length=255)
    product_image = models.ImageField(upload_to = "tender_product/image/",blank=True, null=True)
    description = models.TextField()
    deadline = models.DateTimeField()
    location = models.CharField(max_length=255)
    budget = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0, blank=True, null=True)  # <-- Added field
    status = models.CharField(
        max_length=20,
        choices=[("draft", "Draft"), ("open", "Open"), ("review", "Under Review"), ("awarded", "Awarded"), ("cancelled", "Cancelled")],
        default="open"
    )
    tender_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} (Product No: {self.tender_product_no})"

class TenderBid(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('negotiation', 'Negotiation'),
    ]

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="bids")
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name="bids")
    bid_amount = models.DecimalField(max_digits=12, decimal_places=2)
    bid_description = models.TextField(blank=True, null=True)
    quantity = models.PositiveIntegerField(default=0, blank=True, null=True)  # <-- Added field
    submitted_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    negotiation_message = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('vendor', 'tender')

    def __str__(self):
        return f"{self.vendor.name} - {self.tender.title}"


class RawProductList(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    tender = models.ForeignKey("Tender", on_delete=models.CASCADE, related_name="raw_lists")
    vendor = models.ForeignKey("Vendor", on_delete=models.CASCADE, related_name="raw_lists")
    tender_bid = models.ForeignKey("TenderBid", on_delete=models.CASCADE, related_name="raw_lists")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"RawList ({self.status}) for {self.vendor.name} - {self.tender.title}"


class RawProductListBatch(models.Model):
    raw_list = models.ForeignKey(RawProductList, on_delete=models.CASCADE, related_name="batches")
    delivery_date = models.DateField()
    quantity = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Batch {self.id} - Qty: {self.quantity} on {self.delivery_date}"


class ReceivedOrder(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="received_orders")
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name="received_orders")
    raw_list = models.ForeignKey(RawProductList, on_delete=models.CASCADE, related_name="received_orders")
    received_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    inspection_status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('inspected', 'Inspected')], default='pending')
    received_quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Order for {self.tender.title} from {self.vendor.name}"


class FaultyItem(models.Model):
    received_order = models.ForeignKey(ReceivedOrder, on_delete=models.CASCADE, related_name="faulty_items")
    description = models.TextField()
    reported_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    faulty_quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Faulty item in order {self.received_order.id}"


class AcceptedProduct(models.Model):
    received_order = models.ForeignKey(ReceivedOrder, on_delete=models.CASCADE, related_name="accepted_products")
    description = models.TextField()
    accepted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    accepted_quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Accepted product in order {self.received_order.id}"


class ProductCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    upc = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    cart_quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)

    # status = models.CharField(max_length=20, null=True, blank=True)
    user_address = models.CharField(max_length=10, null=True, blank=True)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    # is_payment = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')
    created_at = models.DateTimeField(auto_now_add=True)

# class ProductReview(models.Model):
#     product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     description = models.TextField()
#     rating = models.PositiveSmallIntegerField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

class UserAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='addresses', on_delete=models.CASCADE)
    house_no = models.CharField(max_length=50)
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    state = models.CharField(max_length=50,null=True, blank=True)
    country = models.CharField(max_length=100, default="India")
    updated_at = models.DateTimeField(auto_now=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.house_no}, {self.street}, {self.city}, {self.postal_code}, {self.country}"

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.mobile}"

class CartItem(models.Model):
    STATUS_CHOICES = [
        ('ordered', 'Ordered'),
        ('cancelled', 'Cancelled'),
        ('processing', 'Processing'),
    ]
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ManyToManyField(Product, related_name='cart_item')
    quantity = models.PositiveIntegerField(default=1)
    user_address = models.ForeignKey(UserAddress, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="processing")
    transaction_id = models.CharField(max_length=100, null=True, blank=True, help_text="Payment made by RazorPay")
    is_payment = models.BooleanField(default=False)

    def __str__(self):
        product_names = ", ".join([product.name for product in self.product.all()])
        return f"{self.quantity} x [{product_names}] - {self.status}"

# class Order(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     billing_address = models.ForeignKey(UserAddress, related_name='billing_orders', on_delete=models.SET_NULL, null=True)
#     shipping_address = models.ForeignKey(UserAddress, related_name='shipping_orders', on_delete=models.SET_NULL, null=True)


# class OrderItem(models.Model):
#     order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField()
#     ordered_price = models.DecimalField(max_digits=10, decimal_places=2)


# class Payment(models.Model):
#     order = models.OneToOneField(Order, on_delete=models.CASCADE)
#     status = models.CharField(max_length=50)
#     updated_at = models.DateTimeField(auto_now=True)

class Payment(models.Model):
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]

    cart_item = models.ForeignKey(CartItem, on_delete=models.CASCADE, related_name='payments')
    payment_id = models.CharField(max_length=100, unique=True)
    order_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS)
    payment_response = models.JSONField(null=True, blank=True)  # Store complete payment response
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.payment_id} for CartItem {self.cart_item.id}"

    def save(self, *args, **kwargs):
        if self.status == 'success':
            self.cart_item.status = 'ordered'
            self.cart_item.is_payment = True
            self.cart_item.save()
        elif self.status == 'failed':
            self.cart_item.status = 'cancelled'
            self.cart_item.save()
        super().save(*args, **kwargs)


class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default="0.00")

    def __str__(self):
        return f"Wallet for {self.user.mobile} - Balance: {self.balance}"


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('credited', 'Credited'),
        ('debited', 'Debited'),
    ]

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.transaction_type.capitalize()} of {self.amount} on {self.created_at}"
    
