{
    "name": "SubWise",
    "version": "1.0",
    "depends": ["base", "web", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "views/product_views.xml",
        "views/plan_views.xml",
        "views/subscription_views.xml",
        "views/discount_views.xml",
        "views/payment_views.xml",
        "views/dashboard_views.xml",
        "views/menu_views.xml",
    ],
    "demo": ["data/demo_data.xml"],
    "assets": {
        "web.assets_backend": [
            "subwise/static/src/css/dashboard.css",
            "subwise/static/src/js/dashboard.js",
        ],
    },
    "application": True,
    "license": "LGPL-3",
}