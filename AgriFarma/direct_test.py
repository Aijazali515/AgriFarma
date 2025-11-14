"""Direct Flask test with full error reporting.
Run: python direct_test.py
"""
import sys
import traceback
from agrifarma import create_app
from config import DevelopmentConfig

print("Creating app...")
try:
    app = create_app(DevelopmentConfig)
    print("✅ App created successfully")
    print(f"Debug mode: {app.debug}")
    print(f"Config: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    print("\nTesting homepage route...")
    with app.test_client() as client:
        response = client.get('/')
        print(f"Test client status: {response.status_code}")
        
    print("\nTesting with real request context...")
    with app.app_context():
        with app.test_request_context('/'):
            from flask import render_template
            from agrifarma.routes.main import index
            try:
                result = index()
                print(f"✅ Route function executed successfully")
            except Exception as e:
                print(f"❌ Error in route function:")
                print(traceback.format_exc())
                
except Exception as e:
    print(f"❌ Error creating app:")
    print(traceback.format_exc())
    sys.exit(1)
