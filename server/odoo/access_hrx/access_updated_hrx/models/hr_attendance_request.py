from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime

class HrAttendanceRequest(models.Model):
    _name = "hr.attendance.request"
    _description = "HR Attendance Request"

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    attn_req_id = fields.Integer(string="Attendance Request ID", required=True, unique=True)
    request_date = fields.Datetime(string="Request Date")
    check_in = fields.Datetime(string='Check In')
    check_out = fields.Datetime(string='Check Out')
    status = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Status', default='pending')
    reason = fields.Text(string="Reason")
    create_date = fields.Datetime(string='Creation Date', default=fields.Datetime.now)
    write_date = fields.Datetime(string='Last Modification Date', default=fields.Datetime.now)
    attendance_id = fields.Many2one('hr.attendance', string="Attendance ID")

    def calculate_worked_hours(self, check_in, check_out):
        if check_in and check_out:
            delta = check_out - check_in
            return delta.total_seconds() / 3600.0  # Convert seconds to hours
        return 0.0

    @api.model
    def action_hr_attendance_request_view(self):
        action = self.env.ref('access_updated_hrx.action_hr_attendance_request_view').read()[0]
        action['domain'] = [('attn_req_id', '!=', False)]
        return action

    def action_pending(self):
        self.write({'status': 'pending'})

    def action_approved(self):
        self.write({'status': 'approved'})
        existing_attendance = self.env['hr.attendance'].search([('id', '=', self.attendance_id.id)], limit=1)
        if existing_attendance:
            existing_attendance.write({
                'employee_id': self.employee_id.id,
                'check_in': self.check_in,
                'check_out': self.check_out,
                'create_date': self.create_date,
                'write_date': self.write_date,
                'worked_hours': self.calculate_worked_hours(self.check_in, self.check_out),
                'attn_req_id': self.attn_req_id,
            })
        else:
            self.env['hr.attendance'].create({
                'employee_id': self.employee_id.id,
                'check_in': self.check_in,
                'check_out': self.check_out,
                'create_date': self.create_date,
                'write_date': self.write_date,
                'worked_hours': self.calculate_worked_hours(self.check_in, self.check_out),
                'attn_req_id': self.attn_req_id,
            })

    def action_rejected(self):
        self.write({'status': 'rejected'})
