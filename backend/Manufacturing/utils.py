# utils.py
from .models import BillOfMaterial

def get_bom_id_for_product(product_id):
    try:
        bom = BillOfMaterial.objects.get(product_id=product_id)
        return bom.id
    except BillOfMaterial.DoesNotExist:
        return None

