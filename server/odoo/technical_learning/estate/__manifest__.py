{
    'name': 'Real Estate Managment',
    'summary': 'Real estate',
    'author': 'CLAREx',
    'license': 'LGPL-3',
    'depends': ['crm',"hr", "base"],
    'data': [
        #security
        "security/ir.model.access.csv",
        #views
        "views/estate_property_views.xml",
        "views/estate_menus.xml",
        
        #menus
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}