{
    'name': 'Access_HRx',
    'author': 'CLAREx',
    'license': 'LGPL-3',
    'depends': ['hr','hr_attendance','base','hr_expense'],
    'data': [
        'views/hr_menuitem.xml',
        'views/hr_mobile_access_portal.xml',
        'views/hr_input_form_view.xml',
        # 'views/attendance_request_access.xml',
        'views/attendance_request_view.xml',
        'views/attendance_request.xml',
        'security/ir.model.access.csv',
        'data/scheduled_actions.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}