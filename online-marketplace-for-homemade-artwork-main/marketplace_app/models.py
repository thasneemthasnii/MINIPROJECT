from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Sum


class Login(AbstractUser):
    is_user = models.BooleanField(default=False)


class User(models.Model):
    user = models.OneToOneField(Login, on_delete=models.CASCADE, primary_key=True, related_name='user')
    name = models.CharField(max_length=200)
    contact_no = models.CharField(max_length=200)
    email = models.EmailField()
    address = models.TextField(max_length=300)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=300)

    def __str__(self):
        return self.name


class Item(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, )
    product_name = models.CharField(max_length=200)
    price = models.FloatField()
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING)
    description = models.TextField()
    quantity_sold = models.IntegerField(default=0)
    instock = models.IntegerField(default=0)
    image = models.ImageField(upload_to='items')
    added_on = models.DateTimeField(auto_now_add=True)
    approval_status = models.IntegerField(default=0)

    def get_rating(self):
        total = sum(int(review['rating']) for review in self.reviews.values())

        if self.reviews.count() > 0:
            return total / self.reviews.count()
        else:
            return 0


class Review(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='reviews', )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', )
    rating = models.IntegerField()
    review = models.TextField(max_length=100)
    date_added = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, )
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='order_item')

    def get_total_item_price(self):
        total = self.quantity * self.item.price
        return total


class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.TextField(max_length=200, null=False)
    city = models.CharField(max_length=200, null=False)
    district = models.CharField(max_length=200, null=False)
    state = models.CharField(max_length=200, null=False)
    pincode = models.CharField(max_length=200, null=False)


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.CharField(max_length=30)
    card_no = models.CharField(max_length=30, )
    card_cvv = models.CharField(max_length=30)
    expiry_month = models.CharField(max_length=20)
    expiry_year = models.CharField(max_length=20)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    ordered_date = models.DateTimeField(null=True)
    ordered = models.BooleanField(default=False)
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField(default=0)
    accepted = models.BooleanField(default=False)
    expected_delivery_date = models.DateField(null=True, blank=True)
    received_date = models.DateField(null=True, blank=True)
    received = models.BooleanField(default=False)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller')

    def get_total(self):
        total = 0
        for i in Order.objects.all():
            total = sum(order_item.quantity * order_item.item.price for order_item in self.items.all())
        return total


class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    subject = models.CharField(max_length=100)
    feedback = models.CharField(max_length=200)


class Earning(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total = models.FloatField()
