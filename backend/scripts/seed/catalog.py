"""Catalog seed: suppliers, categories, components, products, work centers, routes, BOMs."""
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory import Category, Component, Supplier
from app.models.manufacturing import (
    BillOfMaterial,
    BOMItem,
    OperationRoute,
    RouteOperation,
    WorkCenter,
)
from app.models.sales import InverterTypeEnum, Product

from scripts.seed._session import fake, random
from scripts.seed._timeline import NOW, TODAY


SUPPLIERS = [
    ("Lanka Electro Components",     "sales@lanka-electro.lk",     "https://lanka-electro.lk",     "Colombo, Sri Lanka"),
    ("Asia Power Distributors",      "orders@asiapower.com",       "https://asiapower.com",        "Singapore"),
    ("Hindustan Semiconductor",      "trade@hindsemi.in",          "https://hindsemi.in",          "Bangalore, India"),
    ("Pacific Magnetics",            "info@pacificmag.com",        "https://pacificmag.com",       "Shenzhen, China"),
    ("Ceylon Steel Enclosures",      "biz@ceylonsteel.lk",         "https://ceylonsteel.lk",       "Kandy, Sri Lanka"),
    ("Asahi Cooling Systems",        "sales@asahi-cool.co.jp",     "https://asahi-cool.co.jp",     "Osaka, Japan"),
    ("Bharat Passives",              "sales@bharatpassives.in",    "https://bharatpassives.in",    "Pune, India"),
    ("Global Display Tech",          "info@gdt.tw",                "https://gdt.tw",               "Taipei, Taiwan"),
    ("Apex Connectors",              "sales@apex-conn.com",        "https://apex-conn.com",        "Penang, Malaysia"),
    ("Trinity Wire & Cable",         "orders@trinitywire.lk",      "https://trinitywire.lk",       "Negombo, Sri Lanka"),
]


CATEGORIES = [
    ("Semiconductors",  "ICs, MOSFETs, diodes, transistors"),
    ("Passives",        "Resistors, capacitors, inductors"),
    ("Magnetics",       "Transformers, chokes, current sensors"),
    ("Enclosures",      "Cases, panels, brackets"),
    ("Thermal",         "Heat sinks, fans, thermal interface materials"),
    ("PCBs",            "Bare boards"),
    ("Connectors",      "Terminal blocks, headers, lugs"),
    ("Wire & Cable",    "Hookup wire, AC/DC cabling"),
    ("Display & UI",    "LCDs, LEDs, switches"),
    ("Fasteners",       "Screws, washers, nuts"),
]


# (category_key, name, uom, unit_cost, starting_qty, reorder_lvl, reorder_qty)
COMPONENT_TEMPLATES = [
    ("Semiconductors", "TI TMS320 DSP",                      "pcs",    Decimal("18.50"), 220, 80,  300),
    ("Semiconductors", "STM32F4 MCU",                        "pcs",    Decimal("12.20"), 320, 100, 400),
    ("Semiconductors", "IRFP460 N-MOSFET",                   "pcs",    Decimal("3.85"),  900, 200, 800),
    ("Semiconductors", "IRFP4710 N-MOSFET",                  "pcs",    Decimal("4.10"),  720, 200, 800),
    ("Semiconductors", "IR2110 Gate Driver",                 "pcs",    Decimal("2.40"),  640, 150, 500),
    ("Semiconductors", "1N5408 Rectifier Diode",             "pcs",    Decimal("0.08"), 5800, 1000, 5000),
    ("Semiconductors", "Schottky Diode 60V",                 "pcs",    Decimal("0.45"), 2200, 400, 2000),
    ("Semiconductors", "TVS Diode 1500W",                    "pcs",    Decimal("0.62"), 1800, 300, 1500),
    ("Semiconductors", "Optocoupler PC817",                  "pcs",    Decimal("0.30"), 3200, 500, 2000),
    ("Passives",       "Resistor 1k 1%",                     "pcs",    Decimal("0.02"), 12000, 2000, 10000),
    ("Passives",       "Resistor 10k 1%",                    "pcs",    Decimal("0.02"), 11500, 2000, 10000),
    ("Passives",       "Resistor 0.01 ohm 3W",               "pcs",    Decimal("0.18"), 2400, 400, 2000),
    ("Passives",       "Cap 470uF 200V Electrolytic",        "pcs",    Decimal("1.85"), 1900, 400, 1500),
    ("Passives",       "Cap 1uF 630V Film",                  "pcs",    Decimal("0.95"), 2700, 500, 2000),
    ("Passives",       "Cap 100nF Ceramic X7R",              "pcs",    Decimal("0.04"), 14000, 2000, 10000),
    ("Magnetics",      "Toroid Transformer 1.5kW",           "pcs",    Decimal("42.00"), 180, 30,  120),
    ("Magnetics",      "Toroid Transformer 3kW",             "pcs",    Decimal("68.00"), 140, 25,  100),
    ("Magnetics",      "Toroid Transformer 5kW",             "pcs",    Decimal("96.00"), 90,  20,  60),
    ("Magnetics",      "Common-Mode Choke",                  "pcs",    Decimal("5.50"),  600, 100, 400),
    ("Magnetics",      "Current Sensor ACS712",              "pcs",    Decimal("3.20"),  520, 100, 300),
    ("Enclosures",     "Steel Case 1kW",                     "pcs",    Decimal("22.00"), 110, 25,  80),
    ("Enclosures",     "Steel Case 2kW",                     "pcs",    Decimal("28.00"), 90,  20,  70),
    ("Enclosures",     "Steel Case 3kW",                     "pcs",    Decimal("34.00"), 85,  20,  60),
    ("Enclosures",     "Steel Case 5kW",                     "pcs",    Decimal("48.00"), 70,  15,  50),
    ("Enclosures",     "Mounting Bracket Kit",               "set",    Decimal("3.10"),  420, 80,  300),
    ("Thermal",        "Heat Sink 100mm",                    "pcs",    Decimal("4.20"),  700, 150, 500),
    ("Thermal",        "Heat Sink 150mm",                    "pcs",    Decimal("6.80"),  520, 100, 400),
    ("Thermal",        "Heat Sink 200mm",                    "pcs",    Decimal("9.40"),  380, 80,  300),
    ("Thermal",        "Cooling Fan 120mm 12V",              "pcs",    Decimal("4.50"),  640, 150, 400),
    ("Thermal",        "Thermal Paste Tube",                 "pcs",    Decimal("1.80"),  240, 60,  200),
    ("PCBs",           "Main Board PCB 4-layer",             "pcs",    Decimal("12.00"), 320, 60,  200),
    ("PCBs",           "Control Board PCB 2-layer",          "pcs",    Decimal("4.50"),  420, 80,  300),
    ("PCBs",           "Driver Board PCB",                   "pcs",    Decimal("3.20"),  500, 100, 400),
    ("Connectors",     "AC Terminal Block 6-pole",           "pcs",    Decimal("2.10"),  680, 120, 500),
    ("Connectors",     "DC Lug M8 25mm2",                    "pcs",    Decimal("0.55"), 1800, 300, 1200),
    ("Connectors",     "Battery Cable Connector",            "pcs",    Decimal("1.40"),  720, 150, 500),
    ("Connectors",     "Header 2.54mm 40-pin",               "pcs",    Decimal("0.25"), 1400, 250, 1000),
    ("Wire & Cable",   "Hookup Wire 22AWG (roll)",           "roll",   Decimal("7.50"),  60,  15,  40),
    ("Wire & Cable",   "AC Mains Cable 2.5mm2 (m)",          "m",      Decimal("0.85"), 920, 200, 800),
    ("Wire & Cable",   "Battery Cable 25mm2 (m)",            "m",      Decimal("3.20"), 480, 100, 400),
    ("Display & UI",   "LCD 16x2 with Backlight",            "pcs",    Decimal("4.80"),  340, 80,  250),
    ("Display & UI",   "Buzzer Piezo 5V",                    "pcs",    Decimal("0.60"),  720, 150, 500),
    ("Display & UI",   "Rocker Switch 16A",                  "pcs",    Decimal("0.95"),  580, 120, 400),
    ("Display & UI",   "Status LED Green 5mm",               "pcs",    Decimal("0.05"), 4200, 800, 3000),
    ("Display & UI",   "Status LED Red 5mm",                 "pcs",    Decimal("0.05"), 4100, 800, 3000),
    ("Fasteners",      "M3 Screw Pack (100)",                "pack",   Decimal("1.20"),  140, 30,  100),
    ("Fasteners",      "M4 Screw Pack (100)",                "pack",   Decimal("1.40"),  130, 30,  100),
    ("Fasteners",      "M5 Bolt Pack (50)",                  "pack",   Decimal("1.80"),  120, 30,  80),
    ("Fasteners",      "Cable Tie 200mm (100)",              "pack",   Decimal("0.90"),  220, 40,  150),
    ("Fasteners",      "Heat-Shrink Tube Assortment",        "kit",    Decimal("3.40"),   80, 20,  60),
]


# (key, name, model_number, power_w, type, price, surge_w, warranty, in_v, out_v, eff, freq)
PRODUCT_TEMPLATES = [
    ("psw_1000",  "PowerWave Pure 1000",    "PW-PSW-1000", 1000, InverterTypeEnum.PURE_SINE_WAVE,     Decimal("285.00"), 2000, 2, Decimal("12.00"),  Decimal("230.00"), Decimal("94.00"), Decimal("50.00")),
    ("psw_1500",  "PowerWave Pure 1500",    "PW-PSW-1500", 1500, InverterTypeEnum.PURE_SINE_WAVE,     Decimal("385.00"), 3000, 2, Decimal("24.00"),  Decimal("230.00"), Decimal("94.00"), Decimal("50.00")),
    ("psw_2000",  "PowerWave Pure 2000",    "PW-PSW-2000", 2000, InverterTypeEnum.PURE_SINE_WAVE,     Decimal("485.00"), 4000, 3, Decimal("24.00"),  Decimal("230.00"), Decimal("94.00"), Decimal("50.00")),
    ("psw_3000",  "PowerWave Pure 3000",    "PW-PSW-3000", 3000, InverterTypeEnum.PURE_SINE_WAVE,     Decimal("685.00"), 6000, 3, Decimal("48.00"),  Decimal("230.00"), Decimal("95.00"), Decimal("50.00")),
    ("psw_4000",  "PowerWave Pure 4000",    "PW-PSW-4000", 4000, InverterTypeEnum.PURE_SINE_WAVE,     Decimal("885.00"), 8000, 3, Decimal("48.00"),  Decimal("230.00"), Decimal("95.00"), Decimal("50.00")),
    ("psw_5000",  "PowerWave Pure 5000",    "PW-PSW-5000", 5000, InverterTypeEnum.PURE_SINE_WAVE,    Decimal("1085.00"), 10000,3, Decimal("48.00"),  Decimal("230.00"), Decimal("95.00"), Decimal("50.00")),
    ("psw_6000",  "PowerWave Pure 6000",    "PW-PSW-6000", 6000, InverterTypeEnum.PURE_SINE_WAVE,    Decimal("1295.00"), 12000,3, Decimal("48.00"),  Decimal("230.00"), Decimal("95.00"), Decimal("50.00")),
    ("msw_1000",  "PowerWave Mod 1000",     "PW-MSW-1000", 1000, InverterTypeEnum.MODIFIED_SINE_WAVE, Decimal("185.00"), 2000, 1, Decimal("12.00"),  Decimal("230.00"), Decimal("90.00"), Decimal("50.00")),
    ("msw_1500",  "PowerWave Mod 1500",     "PW-MSW-1500", 1500, InverterTypeEnum.MODIFIED_SINE_WAVE, Decimal("245.00"), 3000, 1, Decimal("24.00"),  Decimal("230.00"), Decimal("90.00"), Decimal("50.00")),
    ("msw_2000",  "PowerWave Mod 2000",     "PW-MSW-2000", 2000, InverterTypeEnum.MODIFIED_SINE_WAVE, Decimal("325.00"), 4000, 2, Decimal("24.00"),  Decimal("230.00"), Decimal("90.00"), Decimal("50.00")),
    ("msw_3000",  "PowerWave Mod 3000",     "PW-MSW-3000", 3000, InverterTypeEnum.MODIFIED_SINE_WAVE, Decimal("465.00"), 6000, 2, Decimal("48.00"),  Decimal("230.00"), Decimal("91.00"), Decimal("50.00")),
    ("msw_5000",  "PowerWave Mod 5000",     "PW-MSW-5000", 5000, InverterTypeEnum.MODIFIED_SINE_WAVE, Decimal("765.00"),10000, 2, Decimal("48.00"),  Decimal("230.00"), Decimal("91.00"), Decimal("50.00")),
    ("psw_1000h", "PowerWave Pure 1000 Hybrid", "PW-HYB-1000", 1000, InverterTypeEnum.PURE_SINE_WAVE,  Decimal("465.00"), 2000, 3, Decimal("12.00"),  Decimal("230.00"), Decimal("94.00"), Decimal("50.00")),
    ("psw_3000h", "PowerWave Pure 3000 Hybrid", "PW-HYB-3000", 3000, InverterTypeEnum.PURE_SINE_WAVE,  Decimal("985.00"), 6000, 3, Decimal("48.00"),  Decimal("230.00"), Decimal("95.00"), Decimal("50.00")),
    ("psw_5000h", "PowerWave Pure 5000 Hybrid", "PW-HYB-5000", 5000, InverterTypeEnum.PURE_SINE_WAVE, Decimal("1485.00"),10000, 3, Decimal("48.00"),  Decimal("230.00"), Decimal("95.00"), Decimal("50.00")),
]


WORK_CENTERS = [
    ("SMT-01", "SMT Pick & Place",   Decimal("16.0"), "Reflow line A"),
    ("THT-01", "Through-Hole Assembly", Decimal("16.0"), "TH bench bank"),
    ("MAG-01", "Magnetics Winding", Decimal("8.0"),  "Toroid winding"),
    ("ASM-01", "Final Assembly",    Decimal("16.0"), "Main assembly bay"),
    ("TST-01", "Test & Burn-in",    Decimal("24.0"), "Burn-in chamber + scope rack"),
    ("PKG-01", "Packaging",         Decimal("8.0"),  "Boxing & labeling"),
]


# (route_key, product_key, name, ops list of (seq, name, work_center_code, std_minutes, setup))
ROUTES = [
    ("route_psw_small", ["psw_1000", "psw_1500", "msw_1000", "msw_1500"], "PSW Small Frame Assembly", [
        (1, "PCB SMT Population",   "SMT-01", 14, 8),
        (2, "Through-Hole Assembly","THT-01", 22, 5),
        (3, "Toroid Winding",       "MAG-01", 30, 0),
        (4, "Final Assembly",       "ASM-01", 40, 5),
        (5, "Test & Burn-in",       "TST-01", 90, 0),
        (6, "Packaging",            "PKG-01", 10, 0),
    ]),
    ("route_psw_mid", ["psw_2000", "psw_3000", "msw_2000", "msw_3000"], "PSW Mid Frame Assembly", [
        (1, "PCB SMT Population",   "SMT-01", 18, 8),
        (2, "Through-Hole Assembly","THT-01", 28, 5),
        (3, "Toroid Winding",       "MAG-01", 45, 0),
        (4, "Final Assembly",       "ASM-01", 55, 5),
        (5, "Test & Burn-in",       "TST-01", 120, 0),
        (6, "Packaging",            "PKG-01", 12, 0),
    ]),
    ("route_psw_large", ["psw_4000", "psw_5000", "psw_6000", "msw_5000"], "PSW Large Frame Assembly", [
        (1, "PCB SMT Population",   "SMT-01", 24, 8),
        (2, "Through-Hole Assembly","THT-01", 36, 5),
        (3, "Toroid Winding",       "MAG-01", 60, 0),
        (4, "Final Assembly",       "ASM-01", 75, 5),
        (5, "Test & Burn-in",       "TST-01", 180, 0),
        (6, "Packaging",            "PKG-01", 15, 0),
    ]),
    ("route_hybrid", ["psw_1000h", "psw_3000h", "psw_5000h"], "PSW Hybrid Assembly", [
        (1, "PCB SMT Population",      "SMT-01", 22, 10),
        (2, "Through-Hole Assembly",   "THT-01", 32, 5),
        (3, "Toroid Winding",          "MAG-01", 60, 0),
        (4, "Charger Module Sub-assy", "THT-01", 25, 5),
        (5, "Final Assembly",          "ASM-01", 80, 5),
        (6, "Test & Burn-in",          "TST-01", 200, 0),
        (7, "Packaging",               "PKG-01", 15, 0),
    ]),
]


# BOM templates: per product family (route key), list of (component_template_name, qty)
BOM_BY_FAMILY = {
    "route_psw_small": [
        ("STM32F4 MCU", 1), ("IR2110 Gate Driver", 2), ("IRFP460 N-MOSFET", 4),
        ("Toroid Transformer 1.5kW", 1), ("Cap 470uF 200V Electrolytic", 4), ("Cap 1uF 630V Film", 6),
        ("Resistor 1k 1%", 20), ("Resistor 10k 1%", 20), ("Cap 100nF Ceramic X7R", 30),
        ("Main Board PCB 4-layer", 1), ("Control Board PCB 2-layer", 1), ("Driver Board PCB", 1),
        ("Steel Case 1kW", 1), ("Heat Sink 100mm", 2), ("Cooling Fan 120mm 12V", 1),
        ("LCD 16x2 with Backlight", 1), ("Rocker Switch 16A", 2), ("AC Terminal Block 6-pole", 1),
        ("DC Lug M8 25mm2", 4), ("M3 Screw Pack (100)", 1), ("Cable Tie 200mm (100)", 1),
        ("Hookup Wire 22AWG (roll)", 1), ("AC Mains Cable 2.5mm2 (m)", 2), ("Status LED Green 5mm", 2),
    ],
    "route_psw_mid": [
        ("TI TMS320 DSP", 1), ("IR2110 Gate Driver", 4), ("IRFP460 N-MOSFET", 8),
        ("Toroid Transformer 3kW", 1), ("Cap 470uF 200V Electrolytic", 6), ("Cap 1uF 630V Film", 8),
        ("Resistor 1k 1%", 30), ("Resistor 10k 1%", 30), ("Cap 100nF Ceramic X7R", 40),
        ("Main Board PCB 4-layer", 1), ("Control Board PCB 2-layer", 1), ("Driver Board PCB", 2),
        ("Steel Case 2kW", 1), ("Heat Sink 150mm", 2), ("Cooling Fan 120mm 12V", 2),
        ("LCD 16x2 with Backlight", 1), ("Rocker Switch 16A", 2), ("AC Terminal Block 6-pole", 1),
        ("DC Lug M8 25mm2", 6), ("M4 Screw Pack (100)", 1), ("Common-Mode Choke", 2),
        ("Current Sensor ACS712", 1), ("Hookup Wire 22AWG (roll)", 1), ("Status LED Red 5mm", 2),
    ],
    "route_psw_large": [
        ("TI TMS320 DSP", 1), ("IR2110 Gate Driver", 8), ("IRFP4710 N-MOSFET", 16),
        ("Toroid Transformer 5kW", 1), ("Cap 470uF 200V Electrolytic", 10), ("Cap 1uF 630V Film", 12),
        ("Resistor 1k 1%", 40), ("Resistor 10k 1%", 40), ("Resistor 0.01 ohm 3W", 6),
        ("Main Board PCB 4-layer", 2), ("Control Board PCB 2-layer", 1), ("Driver Board PCB", 4),
        ("Steel Case 5kW", 1), ("Heat Sink 200mm", 4), ("Cooling Fan 120mm 12V", 4),
        ("LCD 16x2 with Backlight", 1), ("Common-Mode Choke", 4), ("Current Sensor ACS712", 2),
        ("DC Lug M8 25mm2", 8), ("M5 Bolt Pack (50)", 1), ("Battery Cable 25mm2 (m)", 4),
    ],
    "route_hybrid": [
        ("TI TMS320 DSP", 1), ("STM32F4 MCU", 1), ("IR2110 Gate Driver", 6), ("IRFP460 N-MOSFET", 12),
        ("Toroid Transformer 3kW", 1), ("Cap 470uF 200V Electrolytic", 12), ("Cap 1uF 630V Film", 10),
        ("Schottky Diode 60V", 8), ("TVS Diode 1500W", 4), ("1N5408 Rectifier Diode", 12),
        ("Main Board PCB 4-layer", 1), ("Control Board PCB 2-layer", 1), ("Driver Board PCB", 2),
        ("Steel Case 3kW", 1), ("Heat Sink 200mm", 3), ("Cooling Fan 120mm 12V", 3),
        ("LCD 16x2 with Backlight", 1), ("Battery Cable Connector", 4), ("Battery Cable 25mm2 (m)", 6),
        ("Current Sensor ACS712", 2), ("Optocoupler PC817", 6), ("Status LED Green 5mm", 3),
    ],
}


async def seed(session: AsyncSession, refs: dict) -> dict:
    # Suppliers
    suppliers: list[Supplier] = []
    for name, email, website, address in SUPPLIERS:
        s = Supplier(name=name, email=email, website=website, address=address, is_active=True, date_added=NOW)
        session.add(s)
        suppliers.append(s)

    # Categories
    categories: dict[str, Category] = {}
    for name, desc in CATEGORIES:
        c = Category(name=name, description=desc)
        session.add(c)
        categories[name] = c
    await session.flush()

    # Components
    components: dict[str, Component] = {}
    for cat_key, name, uom, cost, qty, reorder, reorder_qty in COMPONENT_TEMPLATES:
        supplier = suppliers[hash(name) % len(suppliers)]
        c = Component(
            name=name,
            description=f"{name} — sourced from {supplier.name}",
            quantity=qty,
            category_id=categories[cat_key].id,
            reorder_level=reorder,
            reorder_quantity=reorder_qty,
            order_quantity=reorder_qty,
            unit_of_measure=uom,
            supplier_id=supplier.id,
            cost=cost,
        )
        session.add(c)
        components[name] = c
    await session.flush()

    # Products
    products: dict[str, Product] = {}
    for key, name, model, watts, inv_type, price, surge, warranty, in_v, out_v, eff, freq in PRODUCT_TEMPLATES:
        p = Product(
            name=name,
            model_number=model,
            description=f"{name} {watts}W {inv_type.value} inverter — {warranty}yr warranty",
            price=price,
            inverter_type=inv_type,
            power_rating=watts,
            frequency=freq,
            efficiency=eff,
            surge_power=surge,
            warranty_years=warranty,
            input_voltage=in_v,
            output_voltage=out_v,
        )
        session.add(p)
        products[key] = p
    await session.flush()

    # Work centers
    work_centers: dict[str, WorkCenter] = {}
    for code, name, cap, location in WORK_CENTERS:
        wc = WorkCenter(
            code=code, name=name, capacity_hours_per_day=cap,
            description=f"{name} ({code})", location=location, is_active=True,
        )
        session.add(wc)
        work_centers[code] = wc
    await session.flush()

    # BOMs (one per product family)
    boms: dict[str, BillOfMaterial] = {}
    for route_key, product_keys, _name, _ops in ROUTES:
        anchor_product = products[product_keys[0]]
        bom = BillOfMaterial(name=f"BOM — {anchor_product.name} family", product_id=anchor_product.id)
        session.add(bom)
        boms[route_key] = bom
    await session.flush()

    # BOM Items (driven by family)
    for route_key, lines in BOM_BY_FAMILY.items():
        bom = boms[route_key]
        for comp_name, qty in lines:
            session.add(BOMItem(
                bill_of_material_id=bom.id,
                component_id=components[comp_name].id,
                quantity=qty,
            ))
    await session.flush()

    # Operation Routes + RouteOperations (one route per family, linked to anchor product + BOM)
    routes: dict[str, OperationRoute] = {}
    family_of_product: dict[str, str] = {}
    for route_key, product_keys, route_name, ops in ROUTES:
        anchor = products[product_keys[0]]
        route = OperationRoute(
            name=route_name,
            product_id=anchor.id,
            bom_id=boms[route_key].id,
            is_active=True,
        )
        session.add(route)
        routes[route_key] = route
        for pk in product_keys:
            family_of_product[pk] = route_key
    await session.flush()

    route_ops_by_family: dict[str, list[RouteOperation]] = {}
    for route_key, _pks, _name, ops in ROUTES:
        route = routes[route_key]
        added: list[RouteOperation] = []
        for seq, op_name, wc_code, minutes, setup in ops:
            ro = RouteOperation(
                route_id=route.id,
                sequence=seq,
                name=op_name,
                description=f"{op_name} step in {route.name}",
                work_center_id=work_centers[wc_code].id,
                standard_time_minutes=minutes,
                setup_time_minutes=setup,
            )
            session.add(ro)
            added.append(ro)
        route_ops_by_family[route_key] = added
    await session.flush()

    print(
        f"  catalog: {len(suppliers)} suppliers, {len(categories)} categories, "
        f"{len(components)} components, {len(products)} products, "
        f"{len(work_centers)} work centers, {len(boms)} BOMs, {len(routes)} routes"
    )

    return {
        "suppliers": suppliers,
        "categories": categories,
        "components": components,
        "products": products,
        "work_centers": work_centers,
        "boms": boms,
        "routes": routes,
        "route_ops_by_family": route_ops_by_family,
        "family_of_product": family_of_product,
    }
