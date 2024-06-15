from odoo import fields, models,api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class PortalAccess(models.Model):
    _inherit = 'hr.employee'

    mobile_access = fields.Boolean(string='Mobile Access',default=False)

    invitation_mail = fields.Char(string='Invitation Email') 
 
    @api.model
    def action_open_view_employee_list_my(self):
        action = self.env.ref('hr.open_view_employee_list_my').read()[0]
        action['domain'] = [('mobile_access', '=', True)]
        return action


    

    # def send_invitation_mail(self):
 
    #     main_user_email = self.env.user.email
    #     template = self.env.ref('auth_signup.set_password_email')

    #     for employee in self:
    #         if not employee.work_email:
    #             raise UserError(f"The employee {employee.name} does not have a work email.")
            
    #         template.sudo().with_context(
    #             lang=employee.user_id.lang or 'en_US',
    #             default_email_from=main_user_email,
    #             email_to=employee.work_email,
    #             partner_to=employee.address_id.id if employee.address_id else None
    #         ).send_mail(employee.id, force_send=True)




    # def send_invitation_mail(self):
    #         for employee in self:
    #             if employee.work_email and employee.invitation_email:
    #                 template = self.env.ref('auth_signup.set_password_email')
    #                 template.send_mail(employee.id, force_send=True)
    #             else:
    #                 raise UserError("Work email and invitation email are required.")



    def send_invitation_mail(self):
        for employee in self:
            from_email = self.env.user.email
            if not from_email:
                raise UserError(f"The employee {employee.name} does not have a work email.")
            
            to_email = employee.work_email
            if not to_email:
                raise UserError(f"The employee {employee.name} does not have a work email.")
            
            template = self.env.ref('auth_signup.set_password_email')
            if not template:
                raise UserError("The email template 'auth_signup.set_password_email' could not be found.")
            try:
                _logger.info(f"Attempting to send email from {from_email} to {to_email} for employee {employee.name}")
                template.sudo().with_context(
                    default_email_from=from_email,
                    email_to=to_email,
                    partner_to=employee.address_id.id if employee.address_id else None
                ).send_mail(employee.id, force_send=True)
                
                _logger.info(f"Invitation email successfully sent to {to_email} for employee {employee.name}")
            except Exception as e:
                _logger.error(f"Failed to send invitation email from {from_email} to {to_email} for employee {employee.name}: {str(e)}")
                raise UserError(f"Failed to send invitation email from {from_email} to {to_email} for employee {employee.name}. Please check the email configuration and try again.")


    # @api.model
    # def send_invitations_to_employees(self, employee_ids):
    #     employees_to_invite = self.env['hr.employee'].search([('id', 'in', employee_ids)])
    #     employees_to_invite.send_invitation_mail()

