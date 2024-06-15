{
    'name': 'Access_HRx',
    'author': 'CLAREx',
    'license': 'LGPL-3',
    'depends': ['hr','base'],
    'data': [
        'views/test_menu.xml',
        'views/test_portal.xml',
        'security/ir.model.access.csv',
        'data/scheduled_actions.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}