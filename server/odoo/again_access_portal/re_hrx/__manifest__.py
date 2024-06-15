{
    'name': 'Re_HRx',
    'author': 'CLAREx',
    'license': 'LGPL-3',
    'depends': ['hr','base','mail','auth_signup'],
    'data': [
        'views/menu.xml',
        'views/portal_access.xml',
        'security/ir.model.access.csv',
        'data/scheduled_actions.xml',


    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}