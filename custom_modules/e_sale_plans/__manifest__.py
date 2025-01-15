{
    'name': 'Sale Plans',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Sale Plans',
    'depends': ['sale_management', 'sale','crm'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/sale_plan_views.xml',
        'views/sale_order_views.xml',
    ],
}