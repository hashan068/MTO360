"""
Script to check database state and manually create test table
"""
import asyncio
from sqlalchemy import text, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config.settings import settings

# Create sync engine for testing
sync_url = settings.DATABASE_URL.replace('+asyncpg', '')
engine = create_engine(sync_url)


def check_existing_tables():
    """Check what procurement tables already exist"""
    print("=" * 60)
    print("CHECKING EXISTING PROCUREMENT TABLES")
    print("=" * 60)
    
    with engine.connect() as conn:
        # Check for procurement tables
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE '%procurement%'
            OR table_name LIKE '%supplier_performance%'
            OR table_name LIKE '%contract%'
            ORDER BY table_name;
        """))
        
        tables = [row[0] for row in result]
        
        if tables:
            print(f"\nFound {len(tables)} procurement-related tables:")
            for table in tables:
                print(f"  - {table}")
        else:
            print("\n✅ No procurement tables found (clean slate)")
        
        # Check for enums
        print("\n" + "=" * 60)
        print("CHECKING EXISTING ENUMS")
        print("=" * 60)
        
        result = conn.execute(text("""
            SELECT typname 
            FROM pg_type 
            WHERE typname LIKE '%enum%'
            OR typname IN (
                'rfqstatusenum', 'quotestatusenum', 'contractstatusenum',
                'abcclassificationenum', 'forecastmethodenum', 'pricechangesourceenum'
            )
            ORDER BY typname;
        """))
        
        enums = [row[0] for row in result]
        
        if enums:
            print(f"\nFound {len(enums)} relevant enums:")
            for enum in enums:
                print(f"  - {enum}")
        else:
            print("\n✅ No procurement enums found")
        
        return tables, enums


def create_test_table():
    """Manually create supplier_performance table for testing"""
    print("\n" + "=" * 60)
    print("CREATING TEST TABLE: supplier_performance")
    print("=" * 60)
    
    with engine.connect() as conn:
        # Start transaction
        trans = conn.begin()
        
        try:
            # Drop if exists (for clean testing)
            conn.execute(text("DROP TABLE IF EXISTS supplier_performance CASCADE"))
            print("✅ Dropped existing table (if any)")
            
            # Create table
            conn.execute(text("""
                CREATE TABLE supplier_performance (
                    id SERIAL PRIMARY KEY,
                    supplier_id INTEGER NOT NULL REFERENCES suppliers(id) ON DELETE CASCADE,
                    period DATE NOT NULL,
                    on_time_delivery_rate NUMERIC(5, 2) NOT NULL DEFAULT 0.00,
                    quality_rating NUMERIC(5, 2) NOT NULL DEFAULT 100.00,
                    average_lead_time_days INTEGER NOT NULL DEFAULT 0,
                    price_competitiveness_score NUMERIC(5, 2) NOT NULL DEFAULT 100.00,
                    total_spend NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
                    overall_score NUMERIC(5, 2) NOT NULL DEFAULT 0.00,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE,
                    UNIQUE (supplier_id, period)
                );
            """))
            print("✅ Created supplier_performance table")
            
            # Create indexes
            conn.execute(text("""
                CREATE INDEX ix_supplier_performance_supplier_period 
                ON supplier_performance(supplier_id, period);
            """))
            conn.execute(text("""
                CREATE INDEX ix_supplier_performance_overall_score 
                ON supplier_performance(overall_score);
            """))
            print("✅ Created indexes")
            
            trans.commit()
            print("\n✅ SUCCESS: Test table created successfully!")
            
        except Exception as e:
            trans.rollback()
            print(f"\n❌ ERROR: {e}")
            raise


def insert_test_data():
    """Insert sample performance data"""
    print("\n" + "=" * 60)
    print("INSERTING TEST DATA")
    print("=" * 60)
    
    with engine.connect() as conn:
        trans = conn.begin()
        
        try:
            # Check if we have suppliers
            result = conn.execute(text("SELECT id, name FROM suppliers LIMIT 5"))
            suppliers = list(result)
            
            if not suppliers:
                print("⚠️  No suppliers found. Please add suppliers first.")
                trans.rollback()
                return
            
            print(f"\nFound {len(suppliers)} suppliers. Using first one for test data.")
            supplier_id = suppliers[0][0]
            supplier_name = suppliers[0][1]
            
            # Insert sample performance record
            conn.execute(text("""
                INSERT INTO supplier_performance (
                    supplier_id, period, on_time_delivery_rate, quality_rating,
                    average_lead_time_days, price_competitiveness_score,
                    total_spend, overall_score
                ) VALUES (
                    :supplier_id, '2025-11-01', 95.5, 98.0,
                    15, 92.0, 50000.00, 94.5
                )
                ON CONFLICT (supplier_id, period) DO NOTHING
            """), {"supplier_id": supplier_id})
            
            print(f"✅ Inserted test performance data for supplier: {supplier_name}")
            
            trans.commit()
            
        except Exception as e:
            trans.rollback()
            print(f"❌ ERROR: {e}")


def verify_data():
    """Verify the test data was inserted"""
    print("\n" + "=" * 60)
    print("VERIFYING DATA")
    print("=" * 60)
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT sp.*, s.name as supplier_name
            FROM supplier_performance sp
            JOIN suppliers s ON sp.supplier_id = s.id
            LIMIT 5
        """))
        
        rows = list(result)
        
        if rows:
            print(f"\n✅ Found {len(rows)} performance records:")
            for row in rows:
                print(f"\n  Supplier: {row.supplier_name}")
                print(f"  Period: {row.period}")
                print(f"  On-Time Delivery: {row.on_time_delivery_rate}%")
                print(f"  Quality Rating: {row.quality_rating}%")
                print(f"  Overall Score: {row.overall_score}%")
        else:
            print("\n⚠️  No performance data found")


if __name__ == "__main__":
    try:
        print("\n" + "=" * 60)
        print("PROCUREMENT MODULE - DATABASE CHECK & TEST")
        print("=" * 60)
        
        # Step 1: Check existing state
        tables, enums = check_existing_tables()
        
        # Step 2: Create test table
        create_test_table()
        
        # Step 3: Insert test data
        insert_test_data()
        
        # Step 4: Verify
        verify_data()
        
        print("\n" + "=" * 60)
        print("✅ ALL STEPS COMPLETED")
        print("=" * 60)
        print("\nYou can now test the API endpoints:")
        print("  - GET /api/v1/procurement/suppliers/{id}/performance")
        print("  - GET /api/v1/procurement/suppliers/rankings")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
