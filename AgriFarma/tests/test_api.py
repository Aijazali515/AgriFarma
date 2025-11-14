# -*- coding: utf-8 -*-
from agrifarma import create_app

def test_api_products_smoke():
    app = create_app('config.DevelopmentConfig')
    with app.test_client() as c:
        r = c.get('/api/v1/products?per_page=1')
        assert r.status_code == 200
        j = r.get_json()
        assert 'items' in j and 'total' in j


def test_api_blog_posts_smoke():
    app = create_app('config.DevelopmentConfig')
    with app.test_client() as c:
        r = c.get('/api/v1/blog_posts?per_page=1')
        assert r.status_code == 200
        j = r.get_json()
        assert 'items' in j and 'total' in j


def test_api_forum_threads_smoke():
    app = create_app('config.DevelopmentConfig')
    with app.test_client() as c:
        r = c.get('/api/v1/forum_threads?per_page=1')
        assert r.status_code == 200
        j = r.get_json()
        assert 'items' in j and 'total' in j


def test_api_consultants_smoke():
    app = create_app('config.DevelopmentConfig')
    with app.test_client() as c:
        r = c.get('/api/v1/consultants?per_page=1')
        assert r.status_code == 200
        j = r.get_json()
        assert 'items' in j and 'total' in j


def test_api_search_smoke():
    app = create_app('config.DevelopmentConfig')
    with app.test_client() as c:
        r = c.get('/api/v1/search?q=wheat')
        assert r.status_code == 200
        j = r.get_json()
        assert 'query' in j and 'totals' in j
