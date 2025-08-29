import os
import django
from faker import Faker
import random

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from ecom_product.models import Vendor, VendorProductDetails

fake = Faker()

# Function to create fake vendors
def create_fake_vendors(n=3):
    for _ in range(n):
        vendor = Vendor.objects.create(
            name=fake.company(),
            vendor_code=fake.unique.bothify(text='VEND-####'),
            firm_name=fake.company(),
            website_app_link=fake.url(),
            firm_description=fake.text(),
            contact_person_name=fake.name(),
            contact_person_designation=fake.job(),
            contact_person_mobile=fake.numerify(text='###########'),  # Ensure 11 digits
            contact_person_email=fake.email(),
            email=fake.email(),
            mobile=fake.numerify(text='###########'),  # Ensure 11 digits
            address=fake.address(),
            gst_number=fake.bothify(text='GSTIN##########'),
            is_approved=fake.boolean()
        )
        create_fake_vendor_products(vendor, 3)

# Function to create fake vendor products
def create_fake_vendor_products(vendor, n=3):
    for _ in range(n):
        VendorProductDetails.objects.create(
            vendor=vendor,
            product_brand_name=fake.company(),
            product_name=fake.word(),
            size_packing=fake.random_element(elements=('Small', 'Medium', 'Large')),
            unit_per_mks=fake.random_element(elements=('kg', 'litre', 'piece')),
            price_per_unit=fake.random_number(digits=5, fix_len=True),
            minimum_order_quantity=fake.random_int(min=1, max=100)
        )

if __name__ == '__main__':
    create_fake_vendors()