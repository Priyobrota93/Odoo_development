import hashlib
from odoo import fields, models, api
from odoo.exceptions import ValidationError

class TestPortalAccess(models.Model):
    _inherit = 'hr.employee'

    mobile_access = fields.Boolean(string='Mobile Access', default=False)
    password = fields.Char(string='Password')

    def action_change_password(self):
        # Open the change password form view
        return {
            'type': 'ir.actions.act_window',
            'name': 'Change Password',
            'res_model': 'hr.employee.change.password',
            'view_mode': 'form',
            'view_id': self.env.ref('access_mobile_hrx.view_change_password_form').id,  # Ensure this ID is correct
            'target': 'new',
            'context': {'default_employee_id': self.id}
        }

class HrEmployeeChangePassword(models.TransientModel):
    _name = 'hr.employee.change.password'
    _description = 'Change Password'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    new_password = fields.Char(string='New Password', required=True)
    confirm_password = fields.Char(string='Confirm Password', required=True)

    @api.constrains('new_password', 'confirm_password')
    def _check_passwords(self):
        for record in self:
            if record.new_password != record.confirm_password:
                raise ValidationError("The new password and confirmation password do not match.")

    def _hash_password(self, password):
        # Hash the password using hashlib with PBKDF2-SHA512
        salt = b'some_random_salt'  # You should generate a unique salt for each password
        hashed_password = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 600000)
        return hashed_password.hex()

    def action_set_password(self):
        self.ensure_one()
        employee = self.employee_id

        # Hash the new password
        password_hash = self._hash_password(self.new_password)
        employee.password = password_hash
