=====
Articles
=====

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "articles" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'articles',
    ]

2. Include the polls URLconf in your project urls.py like this::

    path('articles/', include('articles.urls')),

3. Run ``python manage.py migrate`` to create the polls models.
