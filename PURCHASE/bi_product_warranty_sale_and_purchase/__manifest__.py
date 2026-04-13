
{
    "name": "Product Warranty Sale and Purchase",
    "version": "18.0.1.0.2",
    "summary": """ Product Warranty Sale and Purchase""",
    "description": """Product Warranty Sale and Purchase""",
    "author": "Bassam Infotech LLP",
    "company": "Bassam Infotech LLP",
    "maintainer": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "category": "Tools",
    "depends": ["base","purchase","stock","sale","bi_purchase_warranty","purchase_stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/product_warranty.xml",
        "views/product_template.xml",
        "views/product_product.xml",
        "views/stock_move.xml",
        "views/account_move.xml",
        "views/purchase_order.xml"
    ],
    "images": [],
    "license": "OPL-1",
    "installable": True,
    "application": False,
}
