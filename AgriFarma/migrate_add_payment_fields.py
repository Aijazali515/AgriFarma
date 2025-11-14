"""
Database Migration: Add payment fields to orders table
"""
from agrifarma import create_app
from agrifarma.extensions import db
from config import DevelopmentConfig

def migrate_orders_table():
    """Add payment_status and payment_transaction_id columns to orders table"""
    app = create_app(DevelopmentConfig)
    
    with app.app_context():
        with db.engine.connect() as conn:
            try:
                # Check if columns already exist
                result = conn.execute(db.text("PRAGMA table_info(orders)"))
                columns = {row[1] for row in result}
                
                changes_made = False
                
                # Add payment_status column if it doesn't exist
                if 'payment_status' not in columns:
                    print("Adding payment_status column to orders table...")
                    conn.execute(db.text(
                        "ALTER TABLE orders ADD COLUMN payment_status VARCHAR(16) DEFAULT 'Pending'"
                    ))
                    conn.commit()
                    print("✓ Added payment_status column")
                    changes_made = True
                else:
                    print("✓ payment_status column already exists")
                
                # Add payment_transaction_id column if it doesn't exist
                if 'payment_transaction_id' not in columns:
                    print("Adding payment_transaction_id column to orders table...")
                    conn.execute(db.text(
                        "ALTER TABLE orders ADD COLUMN payment_transaction_id VARCHAR(128)"
                    ))
                    conn.commit()
                    print("✓ Added payment_transaction_id column")
                    changes_made = True
                else:
                    print("✓ payment_transaction_id column already exists")
                
                if changes_made:
                    print("\n✅ Database migration completed successfully!")
                else:
                    print("\n✅ No migration needed - all columns already exist")
                    
            except Exception as e:
                print(f"\n❌ Migration failed: {str(e)}")
                conn.rollback()
                raise

if __name__ == "__main__":
    migrate_orders_table()
