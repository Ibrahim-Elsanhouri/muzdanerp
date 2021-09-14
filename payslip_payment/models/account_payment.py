from odoo import models, fields, api, _


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def _compute_payslip(self):
        self.payslip_id = self.env['hr.payslip'].search([('payment_ids', 'in', self.ids)])

    payslip_id = fields.Many2one('hr.payslip', compute='_compute_payslip')

    def button_view_payslip(self):
        return {
            'name': _('Payment'),
            'view_mode': 'tree,form',
            'res_model': 'hr.payslip',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('payment_ids', 'in', self.ids)],
        }
