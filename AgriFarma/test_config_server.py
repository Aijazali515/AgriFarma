from agrifarma import create_app

# Try with string config reference instead of class
app = create_app("config.DevelopmentConfig")

if __name__ == '__main__':
    print(f"App created: {app}")
    print(f"Debug: {app.debug}")
    print(f"Testing route...")
    
    with app.test_client() as client:
        resp = client.get('/')
        print(f"Test client: {resp.status_code}")
    
    print("\nStarting server on http://127.0.0.1:5002")
    app.run(host='127.0.0.1', port=5002, debug=True, use_reloader=False)
