from odoo import models, fields, api
from odoo.exceptions import UserError

class HrAttendanceRequest(models.Model):
    _name = "hr.attendance.request"
    _description = "HR Attendance Request"

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    request_date = fields.Datetime(string="Request Date", default=fields.Datetime.now)
    check_in = fields.Datetime(string='Check In', required=True)
    check_out = fields.Datetime(string='Check Out', required=True)
    status = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Status', default='pending')
    reason = fields.Text(string="Reason")
    attendance_id = fields.Many2one('hr.attendance', string="Attendance ID")

    @api.constrains('check_in', 'check_out')
    def _check_valid_dates(self):
        for record in self:
            if record.check_out and record.check_in and record.check_out <= record.check_in:
                raise UserError("Check-out time must be after check-in time.")

    def calculate_worked_hours(self, check_in, check_out):
        if check_in and check_out:
            delta = check_out - check_in
            return delta.total_seconds() / 3600.0
        return 0.0

    def action_pending(self):
        self.write({'status': 'pending'})

    def action_approved(self):
        self.write({'status': 'approved'})
        if not self.check_in or not self.check_out:
            raise UserError("Check-in and Check-out times must be provided.")
        attendance_vals = {
            'employee_id': self.employee_id.id,
            'check_in': self.check_in,
            'check_out': self.check_out,
            'worked_hours': self.calculate_worked_hours(self.check_in, self.check_out),
        }
        if self.attendance_id:
            self.attendance_id.write(attendance_vals)
        else:
            self.attendance_id = self.env['hr.attendance'].create(attendance_vals)

    def action_rejected(self):
        self.write({'status': 'rejected'})
