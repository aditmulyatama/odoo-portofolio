{
    'name': 'Estate Rental',
    'description': 'Manage properties for sale',
    'author': 'Odoo Class',
    'depends': ['estate','account'],
    'license': 'AGPL-3',
    'version': '17.0.0.1.0',
    'website': 'https://www.odoo.yourcompany.com',
    'installable': True,
    'application': True,
    'category': 'Accounting/Estate Rental',
    'data': [
        'security/ir.model.access.csv',
        'views/estate_rental_menu.xml',
        'views/estate_rental_views.xml',
        'views/estate_property_inherited.xml',
        
    ],
}