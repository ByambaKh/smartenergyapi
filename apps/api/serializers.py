from django.contrib.auth.models import User, Group
from rest_framework import serializers
from apps.data.models import *


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')

# class CustomerSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = Customer
#         fields = ('first_name', 'last_name', 'code', 'duureg_code', 'aimag_code', 'horoo_code', 'hothon_code')


class CustomerSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    code = serializers.CharField(required=False)
    address_name = serializers.CharField(required=False)
    geree_number = serializers.CharField(required=False)


    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return CustomerSerializer.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.id = validated_data.get('id', instance.title)
        instance.first_name = validated_data.get('first_name', instance.code)
        instance.last_name = validated_data.get('last_name', instance.linenos)
        instance.address_name = validated_data.get('address_name', instance.language)
        instance.save()
        return instance


class ZaaltSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    tooluur_id = serializers.IntegerField(read_only=True)
    day_balance = serializers.CharField()
    night_balance = serializers.CharField()
    rush_balance = serializers.CharField()
    last_bichilt_id = serializers.CharField()
    month = serializers.CharField()
    year = serializers.CharField()
    day_diff = serializers.CharField()
    night_diff = serializers.CharField()
    rush_diff = serializers.CharField()

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return CustomerSerializer.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.save()
        return instance


class PayServiceSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    angilal = serializers.CharField()
    payment = serializers.CharField()

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return CustomerSerializer.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.save()
        return instance

class DedstantsSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return DedstantsSerializer.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.save()
        return instance

class BairSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return BairSerializer.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.save()
        return instance

class CustomerPayServiceSerializer(serializers.Serializer):
    uil_date = serializers.DateTimeField()
    payment = serializers.CharField()
    year = serializers.CharField()
    month = serializers.CharField()
    customer_id = serializers.CharField()
    monter_id = serializers.CharField()
    tooluur_id = serializers.CharField()
    uilchilgee_id = serializers.CharField()

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return CustomerSerializer.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.save()
        return instance


class CustomerZaaltSerializer(serializers.Serializer):
    id = serializers.CharField()
    day_balance = serializers.CharField()
    night_balance = serializers.CharField()
    rush_balance = serializers.CharField()
    last_bichilt_id = serializers.CharField()
    month = serializers.CharField()
    year = serializers.CharField()
    customer_id = serializers.CharField() #new
    tooluur_number = serializers.CharField()  #new
    employee_id = serializers.CharField()
    bichilt_date = serializers.DateTimeField() #new
    customer_angilal = serializers.CharField()  # new
    is_problem = serializers.CharField()

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return CustomerSerializer.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.save()
        return instance

class TooluurSerializer(serializers.Serializer):
    id = serializers.CharField()
    tooluur_id = serializers.CharField()
    customer_code = serializers.CharField()
    tooluur_name = serializers.CharField()
    tooluur_number = serializers.CharField()
    init_day = serializers.CharField()
    init_night = serializers.CharField()
    init_rush = serializers.CharField()
    tariff = serializers.CharField()
    customer_angilal = serializers.CharField()
    dedstants_id = serializers.CharField()
    bair_id = serializers.CharField()

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return CustomerSerializer.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.save()
        return instance

class TaslaltZalgaltSerializer(serializers.Serializer):
    id = serializers.CharField()
    code = serializers.CharField()
    last_name = serializers.CharField()
    first_name = serializers.CharField()

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return TaslaltZalgaltSerializer.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.save()
        return instance

class PosSerializer(serializers.Serializer):
    customerCode = serializers.CharField()
    bankCode = serializers.CharField()
    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return PosSerializer.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.save()
        return instance

class CustomerBankSerializer(serializers.Serializer):
    customerCode = serializers.CharField()
    bankCode = serializers.CharField()

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return CustomerBankSerializer.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.save()
        return instance

class PosPaymentSerializer(serializers.Serializer):
    cusnum = serializers.CharField()
    totalpayment = serializers.CharField()
    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return PosPaymentSerializer.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.save()
        return instance



class CustomerMostSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    FName = serializers.CharField()
    LName = serializers.CharField()
    RegisterNo = serializers.CharField(required=False)
    AddressShort = serializers.CharField(required=False)
    Code = serializers.CharField(required=False)