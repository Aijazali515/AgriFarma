from agrifarma import create_app

app = create_app('config.DevelopmentConfig')
with app.test_client() as c:
    for path in ['/api/v1/products','/api/v1/blog_posts','/api/v1/forum_threads','/api/v1/consultants','/api/v1/search?q=a']:
        r = c.get(path)
        print(path, r.status_code)
print('blueprints:', list(app.blueprints.keys()))
