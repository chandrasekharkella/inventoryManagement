from rest_framework import serializers
from .models import Product,User,AuthUsers
from .tests import mask_email  # Import the mask_email function

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'price', 'available', 'updated_at','created_at']

class ProductRequestSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    min_price = serializers.FloatField(required=False)
    max_price = serializers.FloatField(required=False)
    available = serializers.BooleanField(required=False)
    
class UserSerializer(serializers.ModelSerializer):
    masked_email = serializers.SerializerMethodField()
    
    class Meta:
        model = AuthUsers
        fields = ['id', 'firstName','lastName','masked_email', 'gender', 'address','address',]
        
    def get_masked_email(self, obj):
        return mask_email(obj.email)   
    
