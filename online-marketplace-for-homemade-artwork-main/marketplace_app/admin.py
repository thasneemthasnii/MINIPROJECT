from django.contrib import admin
from marketplace_app import models


admin.site.register(models.Login)
admin.site.register(models.User)
admin.site.register(models.Category)
admin.site.register(models.Item)
admin.site.register(models.Review)
admin.site.register(models.OrderItem)
admin.site.register(models.ShippingAddress)
admin.site.register(models.Payment)
admin.site.register(models.Order)
admin.site.register(models.Feedback)
admin.site.register(models.Earning)
