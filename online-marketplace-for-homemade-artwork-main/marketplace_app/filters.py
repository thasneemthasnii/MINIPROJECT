import django_filters
from django import forms
from django_filters import CharFilter, filters

from marketplace_app.models import Category, User


class CategoryFilter(django_filters.FilterSet):
    name = CharFilter(field_name='name', label="", lookup_expr='icontains', widget=forms.TextInput(attrs={
        'placeholder': 'Search Category', 'class': 'form-control'}))

    class Meta:
        model = Category
        fields = ('name',)


class ProductFilter(django_filters.FilterSet):
    product_name = CharFilter(field_name='product_name', label="", lookup_expr='icontains',
                              widget=forms.TextInput(attrs={
                                  'placeholder': 'Search Product', 'class': 'form-control'}))

    class Meta:
        model = Category
        fields = ('product_name',)

class UserFilter(django_filters.FilterSet):
    name = CharFilter(field_name='name', label="", lookup_expr='icontains',
                              widget=forms.TextInput(attrs={
                                  'placeholder': 'Search Users', 'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('name',)