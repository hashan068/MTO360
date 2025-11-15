"""
Script to seed the database with meaningful mock data
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, date, timedelta
from decimal import Decimal

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select
from app.config.database import AsyncSessionLocal, init_db
from app.models.user import User
from app.models.inventory import (
    Supplier,
    Category,
    Component,
    PurchaseRequisition,
    PurchaseOrder,
    StatusEnum,
    PriorityEnum,
    PurchaseOrderStatusEnum,
)
from app.models.sales import (
    Customer,
    Product,
    RFQ,
    RFQItem,
    Quotation,
    QuotationItem,
    SalesOrder,
    SalesOrderItem,
    RFQStatusEnum,
    QuotationStatusEnum,
    SalesOrderStatusEnum,
    InverterTypeEnum,
)
from app.models.manufacturing import (
    BillOfMaterial,
    BOMItem,
    ManufacturingOrder,
    MaterialRequisition,
    MaterialRequisitionItem,
    ManufacturingOrderStatusEnum,
    MaterialRequisitionStatusEnum,
    MaterialRequisitionItemStatusEnum,
)


async def seed_data():
    """Seed database with meaningful mock data"""
    # Initialize database (create tables if they don't exist)
    await init_db()
    
    async with AsyncSessionLocal() as session:
        # Check if data already exists
        result = await session.execute(select(Component))
        if result.scalar_one_or_none():
            print("[WARNING] Database already contains data. Skipping seed.")
            return
        
        print("Starting database seeding...")
        
        # Get or create a user for foreign keys
        result = await session.execute(select(User).limit(1))
        user = result.scalar_one_or_none()
        if not user:
            print("[ERROR] No user found. Please create a user first using create_user.py")
            return
        
        # 1. Create Categories
        print("Creating categories...")
        categories_data = [
            {"name": "Electronics", "description": "Electronic components and parts"},
            {"name": "Mechanical", "description": "Mechanical parts and hardware"},
            {"name": "Packaging", "description": "Packaging materials"},
            {"name": "Raw Materials", "description": "Raw manufacturing materials"},
            {"name": "Tools", "description": "Manufacturing tools and equipment"},
        ]
        categories = []
        for cat_data in categories_data:
            category = Category(**cat_data)
            session.add(category)
            categories.append(category)
        await session.flush()
        print(f"   [OK] Created {len(categories)} categories")
        
        # 2. Create Suppliers
        print("Creating suppliers...")
        suppliers_data = [
            {
                "name": "TechSupply Co.",
                "email": "contact@techsupply.com",
                "address": "123 Industrial Ave, Colombo 05",
                "website": "https://techsupply.com",
                "is_active": True,
                "notes": "Primary supplier for electronic components",
            },
            {
                "name": "Global Hardware Ltd",
                "email": "sales@globalhardware.lk",
                "address": "456 Commerce St, Kandy",
                "website": "https://globalhardware.lk",
                "is_active": True,
                "notes": "Reliable supplier for mechanical parts",
            },
            {
                "name": "Power Components Inc",
                "email": "info@powercomponents.com",
                "address": "789 Power Road, Galle",
                "website": "https://powercomponents.com",
                "is_active": True,
                "notes": "Specialized in power electronics",
            },
            {
                "name": "MetalWorks International",
                "email": "contact@metalworks.com",
                "address": "321 Steel Boulevard, Negombo",
                "website": "https://metalworks.com",
                "is_active": True,
                "notes": "Quality metal components supplier",
            },
            {
                "name": "Circuit Board Suppliers",
                "email": "sales@circuitboards.lk",
                "address": "654 Electronics Lane, Kurunegala",
                "website": "https://circuitboards.lk",
                "is_active": True,
                "notes": "PCB and circuit board specialists",
            },
        ]
        suppliers = []
        for sup_data in suppliers_data:
            supplier = Supplier(**sup_data)
            session.add(supplier)
            suppliers.append(supplier)
        await session.flush()
        print(f"   [OK] Created {len(suppliers)} suppliers")
        
        # 3. Create Components
        print("Creating components...")
        components_data = [
            {
                "name": "Resistor 1K Ohm",
                "description": "1K ohm carbon film resistor, 1/4W",
                "quantity": 1500,
                "reorder_level": 500,
                "reorder_quantity": 1000,
                "order_quantity": 0,
                "unit_of_measure": "pcs",
                "category_id": categories[0].id,
                "supplier_id": suppliers[0].id,
                "cost": Decimal("0.05"),
            },
            {
                "name": "Capacitor 100µF",
                "description": "100 microfarad electrolytic capacitor, 25V",
                "quantity": 800,
                "reorder_level": 300,
                "reorder_quantity": 500,
                "order_quantity": 0,
                "unit_of_measure": "pcs",
                "category_id": categories[0].id,
                "supplier_id": suppliers[0].id,
                "cost": Decimal("0.15"),
            },
            {
                "name": "LM7805 Voltage Regulator",
                "description": "5V linear voltage regulator IC",
                "quantity": 200,
                "reorder_level": 100,
                "reorder_quantity": 150,
                "order_quantity": 0,
                "unit_of_measure": "pcs",
                "category_id": categories[0].id,
                "supplier_id": suppliers[2].id,
                "cost": Decimal("0.75"),
            },
            {
                "name": "Steel Enclosure 200x150x100mm",
                "description": "Steel enclosure box for inverter mounting",
                "quantity": 50,
                "reorder_level": 20,
                "reorder_quantity": 30,
                "order_quantity": 0,
                "unit_of_measure": "pcs",
                "category_id": categories[1].id,
                "supplier_id": suppliers[3].id,
                "cost": Decimal("25.00"),
            },
            {
                "name": "Heat Sink 50x50mm",
                "description": "Aluminum heat sink for power transistors",
                "quantity": 120,
                "reorder_level": 50,
                "reorder_quantity": 80,
                "order_quantity": 0,
                "unit_of_measure": "pcs",
                "category_id": categories[1].id,
                "supplier_id": suppliers[1].id,
                "cost": Decimal("3.50"),
            },
            {
                "name": "PCB Board 10x10cm",
                "description": "Printed circuit board blank, double-sided",
                "quantity": 75,
                "reorder_level": 30,
                "reorder_quantity": 50,
                "order_quantity": 0,
                "unit_of_measure": "pcs",
                "category_id": categories[0].id,
                "supplier_id": suppliers[4].id,
                "cost": Decimal("5.00"),
            },
            {
                "name": "Transformer 12V 5A",
                "description": "Step-down transformer 230V to 12V, 5A output",
                "quantity": 35,
                "reorder_level": 15,
                "reorder_quantity": 25,
                "order_quantity": 0,
                "unit_of_measure": "pcs",
                "category_id": categories[0].id,
                "supplier_id": suppliers[2].id,
                "cost": Decimal("45.00"),
            },
            {
                "name": "MOSFET IRF540N",
                "description": "Power MOSFET N-channel, 100V 33A",
                "quantity": 180,
                "reorder_level": 80,
                "reorder_quantity": 120,
                "order_quantity": 0,
                "unit_of_measure": "pcs",
                "category_id": categories[0].id,
                "supplier_id": suppliers[0].id,
                "cost": Decimal("1.25"),
            },
            {
                "name": "LED Indicator Red",
                "description": "5mm red LED indicator light",
                "quantity": 500,
                "reorder_level": 200,
                "reorder_quantity": 300,
                "order_quantity": 0,
                "unit_of_measure": "pcs",
                "category_id": categories[0].id,
                "supplier_id": suppliers[0].id,
                "cost": Decimal("0.10"),
            },
            {
                "name": "Screws M3x10mm",
                "description": "Stainless steel screws M3 x 10mm, pack of 100",
                "quantity": 25,
                "reorder_level": 10,
                "reorder_quantity": 15,
                "order_quantity": 0,
                "unit_of_measure": "pack",
                "category_id": categories[1].id,
                "supplier_id": suppliers[1].id,
                "cost": Decimal("8.50"),
            },
            {
                "name": "Fan 12V DC 80mm",
                "description": "Cooling fan 80mm, 12V DC, 2000 RPM",
                "quantity": 60,
                "reorder_level": 25,
                "reorder_quantity": 40,
                "order_quantity": 0,
                "unit_of_measure": "pcs",
                "category_id": categories[0].id,
                "supplier_id": suppliers[1].id,
                "cost": Decimal("6.00"),
            },
            {
                "name": "Wire 16 AWG Red",
                "description": "16 AWG stranded wire, red color, 100m roll",
                "quantity": 12,
                "reorder_level": 5,
                "reorder_quantity": 8,
                "order_quantity": 0,
                "unit_of_measure": "roll",
                "category_id": categories[0].id,
                "supplier_id": suppliers[0].id,
                "cost": Decimal("35.00"),
            },
        ]
        components = []
        for comp_data in components_data:
            component = Component(**comp_data)
            session.add(component)
            components.append(component)
        await session.flush()
        print(f"   [OK] Created {len(components)} components")
        
        # 4. Create Customers
        print("Creating customers...")
        customers_data = [
            {
                "name": "ABC Electronics",
                "email": "orders@abcelectronics.com",
                "phone": "+94 11 234 5678",
                "street_address": "123 Business Park, Colombo 03",
                "city": "Colombo",
                "is_active": True,
                "notes": "Regular customer, monthly orders",
            },
            {
                "name": "Green Energy Solutions",
                "email": "purchasing@greenenergy.lk",
                "phone": "+94 81 345 6789",
                "street_address": "456 Solar Avenue, Kandy",
                "city": "Kandy",
                "is_active": True,
                "notes": "Specializes in solar power systems",
            },
            {
                "name": "Power Systems Ltd",
                "email": "info@powersystems.com",
                "phone": "+94 91 456 7890",
                "street_address": "789 Industrial Zone, Galle",
                "city": "Galle",
                "is_active": True,
                "notes": "Large volume orders, bulk pricing",
            },
            {
                "name": "TechMart Stores",
                "email": "wholesale@techmart.lk",
                "phone": "+94 31 567 8901",
                "street_address": "321 Retail District, Negombo",
                "city": "Negombo",
                "is_active": True,
                "notes": "Retail chain, multiple locations",
            },
            {
                "name": "Rural Power Initiative",
                "email": "contact@ruralpower.lk",
                "phone": "+94 37 678 9012",
                "street_address": "654 Main Street, Kurunegala",
                "city": "Kurunegala",
                "is_active": True,
                "notes": "Non-profit organization, special pricing",
            },
        ]
        customers = []
        for cust_data in customers_data:
            customer = Customer(**cust_data)
            session.add(customer)
            customers.append(customer)
        await session.flush()
        print(f"   [OK] Created {len(customers)} customers")
        
        # 5. Create Products
        print("Creating products...")
        products_data = [
            {
                "name": "PowerWave 1000W Pure Sine Inverter",
                "model_number": "PW-1000-PSW",
                "description": "1000W pure sine wave inverter, ideal for sensitive electronics and home appliances",
                "price": Decimal("450.00"),
                "inverter_type": InverterTypeEnum.PURE_SINE_WAVE,
                "power_rating": 1000,
                "frequency": Decimal("50.00"),
                "efficiency": Decimal("92.50"),
                "surge_power": 2000,
                "warranty_years": 3,
                "input_voltage": Decimal("12.00"),
                "output_voltage": Decimal("230.00"),
            },
            {
                "name": "PowerWave 2000W Pure Sine Inverter",
                "model_number": "PW-2000-PSW",
                "description": "2000W pure sine wave inverter for larger applications",
                "price": Decimal("750.00"),
                "inverter_type": InverterTypeEnum.PURE_SINE_WAVE,
                "power_rating": 2000,
                "frequency": Decimal("50.00"),
                "efficiency": Decimal("93.00"),
                "surge_power": 4000,
                "warranty_years": 3,
                "input_voltage": Decimal("24.00"),
                "output_voltage": Decimal("230.00"),
            },
            {
                "name": "PowerWave 500W Modified Sine Inverter",
                "model_number": "PW-500-MSW",
                "description": "Economical 500W modified sine wave inverter",
                "price": Decimal("180.00"),
                "inverter_type": InverterTypeEnum.MODIFIED_SINE_WAVE,
                "power_rating": 500,
                "frequency": Decimal("50.00"),
                "efficiency": Decimal("88.00"),
                "surge_power": 1000,
                "warranty_years": 2,
                "input_voltage": Decimal("12.00"),
                "output_voltage": Decimal("230.00"),
            },
            {
                "name": "PowerWave 1500W Modified Sine Inverter",
                "model_number": "PW-1500-MSW",
                "description": "1500W modified sine wave inverter, cost-effective solution",
                "price": Decimal("380.00"),
                "inverter_type": InverterTypeEnum.MODIFIED_SINE_WAVE,
                "power_rating": 1500,
                "frequency": Decimal("50.00"),
                "efficiency": Decimal("89.50"),
                "surge_power": 3000,
                "warranty_years": 2,
                "input_voltage": Decimal("12.00"),
                "output_voltage": Decimal("230.00"),
            },
            {
                "name": "PowerWave 3000W Pure Sine Inverter",
                "model_number": "PW-3000-PSW",
                "description": "High-capacity 3000W pure sine wave inverter for commercial use",
                "price": Decimal("1200.00"),
                "inverter_type": InverterTypeEnum.PURE_SINE_WAVE,
                "power_rating": 3000,
                "frequency": Decimal("50.00"),
                "efficiency": Decimal("94.00"),
                "surge_power": 6000,
                "warranty_years": 5,
                "input_voltage": Decimal("48.00"),
                "output_voltage": Decimal("230.00"),
            },
        ]
        products = []
        for prod_data in products_data:
            product = Product(**prod_data)
            session.add(product)
            products.append(product)
        await session.flush()
        print(f"   [OK] Created {len(products)} products")
        
        # 6. Create Purchase Requisitions
        print("Creating purchase requisitions...")
        purchase_requisitions = []
        for i in range(8):
            component = components[i % len(components)]
            req = PurchaseRequisition(
                user_id=user.id,
                component_id=component.id,
                quantity=(i + 1) * 50,
                status=StatusEnum.PENDING if i < 3 else (StatusEnum.APPROVED if i < 6 else StatusEnum.FULFILLED),
                notes=f"Requisition for {component.name}",
                expected_delivery_date=datetime.utcnow() + timedelta(days=7 + i * 2),
                priority=PriorityEnum.HIGH if i < 3 else (PriorityEnum.MEDIUM if i < 6 else PriorityEnum.LOW),
            )
            session.add(req)
            purchase_requisitions.append(req)
        await session.flush()
        print(f"   [OK] Created {len(purchase_requisitions)} purchase requisitions")
        
        # 7. Create Purchase Orders
        print("Creating purchase orders...")
        purchase_orders = []
        for i, req in enumerate(purchase_requisitions[:5]):
            component = components[req.component_id - 1]
            po = PurchaseOrder(
                creator_id=user.id,
                purchase_requisition_id=req.id,
                supplier_id=component.supplier_id,
                status=PurchaseOrderStatusEnum.DRAFT if i < 1 else (PurchaseOrderStatusEnum.APPROVED if i < 3 else PurchaseOrderStatusEnum.RECEIVED),
                notes=f"Purchase order for {component.name}",
                price_per_unit=component.cost,
                total_price=Decimal(str(req.quantity)) * component.cost,
            )
            session.add(po)
            purchase_orders.append(po)
        await session.flush()
        print(f"   [OK] Created {len(purchase_orders)} purchase orders")
        
        # 8. Create RFQs
        print("Creating RFQs...")
        rfqs = []
        for i in range(4):
            rfq = RFQ(
                creator_id=user.id,
                status=RFQStatusEnum.DRAFT if i < 2 else RFQStatusEnum.SENT,
                due_date=datetime.utcnow() + timedelta(days=14 + i * 7),
                description=f"RFQ #{i+1} for inverter components",
            )
            session.add(rfq)
            rfqs.append(rfq)
        await session.flush()
        
        # Create RFQ Items
        rfq_items = []
        for rfq in rfqs:
            for j, product in enumerate(products[:2]):
                item = RFQItem(
                    rfq_id=rfq.id,
                    product_id=product.id,
                    quantity=(j + 1) * 5,
                    unit_price=product.price,
                )
                session.add(item)
                rfq_items.append(item)
        await session.flush()
        print(f"   [OK] Created {len(rfqs)} RFQs with {len(rfq_items)} items")
        
        # 9. Create Quotations
        print("Creating quotations...")
        quotations = []
        for i, customer in enumerate(customers[:4]):
            quot = Quotation(
                customer_id=customer.id,
                date=date.today(),
                expiration_date=date.today() + timedelta(days=30),
                invoicing_and_shipping_address=customer.street_address,
                total_amount=Decimal("0.00"),
                status=QuotationStatusEnum.QUOTATION if i < 2 else QuotationStatusEnum.QUOTATION_SENT,
                created_by_id=user.id,
            )
            session.add(quot)
            quotations.append(quot)
        await session.flush()
        
        # Create Quotation Items
        quotation_items = []
        total_amounts = {}
        for i, quotation in enumerate(quotations):
            product = products[i % len(products)]
            quantity = (i + 1) * 2
            unit_price = product.price
            total = Decimal(str(quantity)) * unit_price
            
            item = QuotationItem(
                quotation_id=quotation.id,
                product_id=product.id,
                quantity=quantity,
                unit_price=unit_price,
            )
            session.add(item)
            quotation_items.append(item)
            total_amounts[quotation.id] = total_amounts.get(quotation.id, Decimal("0.00")) + total
        
        # Update quotation totals
        for quotation in quotations:
            if quotation.id in total_amounts:
                quotation.total_amount = total_amounts[quotation.id]
        await session.flush()
        print(f"   [OK] Created {len(quotations)} quotations with {len(quotation_items)} items")
        
        # 10. Create Sales Orders
        print("Creating sales orders...")
        sales_orders = []
        for i, customer in enumerate(customers[:3]):
            order = SalesOrder(
                customer_id=customer.id,
                total_amount=Decimal("0.00"),
                status=SalesOrderStatusEnum.PENDING if i < 1 else (SalesOrderStatusEnum.CONFIRMED if i < 2 else SalesOrderStatusEnum.IN_PRODUCTION),
            )
            session.add(order)
            sales_orders.append(order)
        await session.flush()
        
        # Create Sales Order Items
        sales_order_items = []
        order_totals = {}
        for i, order in enumerate(sales_orders):
            product = products[i % len(products)]
            quantity = (i + 1) * 3
            price = product.price
            total = Decimal(str(quantity)) * price
            
            item = SalesOrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                price=price,
            )
            session.add(item)
            sales_order_items.append(item)
            order_totals[order.id] = order_totals.get(order.id, Decimal("0.00")) + total
        
        # Update sales order totals
        for order in sales_orders:
            if order.id in order_totals:
                order.total_amount = order_totals[order.id]
        await session.flush()
        print(f"   [OK] Created {len(sales_orders)} sales orders with {len(sales_order_items)} items")
        
        # 11. Create Bill of Materials
        print("Creating bill of materials...")
        boms = []
        for i, product in enumerate(products[:3]):
            bom = BillOfMaterial(
                name=f"BOM for {product.name}",
                product_id=product.id,
            )
            session.add(bom)
            boms.append(bom)
        await session.flush()
        
        # Create BOM Items
        bom_items = []
        for bom in boms:
            # Add 4-6 components per BOM
            component_count = 4 + (bom.id % 3)
            for j in range(component_count):
                component = components[j % len(components)]
                item = BOMItem(
                    bill_of_material_id=bom.id,
                    component_id=component.id,
                    quantity=(j + 1) * 2,
                )
                session.add(item)
                bom_items.append(item)
        await session.flush()
        print(f"   [OK] Created {len(boms)} BOMs with {len(bom_items)} items")
        
        # 12. Create Manufacturing Orders
        print("Creating manufacturing orders...")
        manufacturing_orders = []
        for i, sales_order_item in enumerate(sales_order_items[:3]):
            product = products[i % len(products)]
            bom = boms[i % len(boms)] if boms else None
            
            mo = ManufacturingOrder(
                sales_order_item_id=sales_order_item.id,
                product_id=product.id,
                quantity=sales_order_item.quantity,
                bom_id=bom.id if bom else None,
                status=ManufacturingOrderStatusEnum.PENDING if i < 1 else (ManufacturingOrderStatusEnum.MR_APPROVED if i < 2 else ManufacturingOrderStatusEnum.IN_PRODUCTION),
                creator_id=user.id,
                estimated_mfg_lead_time=timedelta(days=5 + i),
                production_start_at=datetime.utcnow() + timedelta(days=i) if i >= 1 else None,
            )
            session.add(mo)
            manufacturing_orders.append(mo)
        await session.flush()
        print(f"   [OK] Created {len(manufacturing_orders)} manufacturing orders")
        
        # 13. Create Material Requisitions
        print("Creating material requisitions...")
        material_requisitions = []
        for mo in manufacturing_orders:
            mr = MaterialRequisition(
                manufacturing_order_id=mo.id,
                bom_id=mo.bom_id,
                status=MaterialRequisitionStatusEnum.PENDING if mo.id % 2 == 1 else MaterialRequisitionStatusEnum.APPROVED,
            )
            session.add(mr)
            material_requisitions.append(mr)
        await session.flush()
        
        # Create Material Requisition Items
        material_requisition_items = []
        # Create a map of manufacturing_order_id to quantity
        mo_quantity_map = {mo.id: mo.quantity for mo in manufacturing_orders}
        
        for mr in material_requisitions:
            # Get BOM items for this material requisition
            bom_id = mr.bom_id
            mo_quantity = mo_quantity_map.get(mr.manufacturing_order_id, 1)
            
            if bom_id:
                result = await session.execute(select(BOMItem).where(BOMItem.bill_of_material_id == bom_id))
                bom_items_for_mr = result.scalars().all()
                
                for bom_item in bom_items_for_mr[:4]:  # Limit to 4 items per MR
                    mri = MaterialRequisitionItem(
                        material_requisition_id=mr.id,
                        component_id=bom_item.component_id,
                        quantity=bom_item.quantity * mo_quantity,
                        status=MaterialRequisitionItemStatusEnum.PENDING if mr.id % 2 == 1 else MaterialRequisitionItemStatusEnum.APPROVED,
                    )
                    session.add(mri)
                    material_requisition_items.append(mri)
        await session.flush()
        print(f"   [OK] Created {len(material_requisitions)} material requisitions with {len(material_requisition_items)} items")
        
        # Commit all changes
        await session.commit()
        print("\n[SUCCESS] Database seeding completed successfully!")
        print(f"\nSummary:")
        print(f"   • {len(categories)} Categories")
        print(f"   • {len(suppliers)} Suppliers")
        print(f"   • {len(components)} Components")
        print(f"   • {len(customers)} Customers")
        print(f"   • {len(products)} Products")
        print(f"   • {len(purchase_requisitions)} Purchase Requisitions")
        print(f"   • {len(purchase_orders)} Purchase Orders")
        print(f"   • {len(rfqs)} RFQs")
        print(f"   • {len(quotations)} Quotations")
        print(f"   • {len(sales_orders)} Sales Orders")
        print(f"   • {len(boms)} Bill of Materials")
        print(f"   • {len(manufacturing_orders)} Manufacturing Orders")
        print(f"   • {len(material_requisitions)} Material Requisitions")


async def main():
    """Main function"""
    try:
        await seed_data()
    except Exception as e:
        print(f"\n[ERROR] Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

