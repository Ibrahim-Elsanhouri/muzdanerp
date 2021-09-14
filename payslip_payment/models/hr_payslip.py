# -*- coding: utf-8 -*-
import logging
import pytz
import time
import babel

from odoo import _, api, fields, models, tools, _
from odoo.tools import float_compare, float_is_zero

_logger = logging.getLogger(__name__)


class HrPayslip(models.Model):
    _name = 'hr.payslip'
    _inherit = ['hr.payslip', 'mail.thread']

    state = fields.Selection([
        ('draft', 'Draft'),
        ('verify', 'Waiting'),
        ('done', 'Done'),
        ('paid', 'Paid'),
        ('cancel', 'Rejected'),
    ], string='Status', index=True, readonly=True, copy=False, default='draft',
        help="""* When the payslip is created the status is \'Draft\'
                \n* If the payslip is under verification, the status is \'Waiting\'.
                \n* If the payslip is confirmed then status is set to \'Done\'.
                \n* When user cancel payslip the status is \'Rejected\'.""", track_visibility='onchange')
    total_amount = fields.Float(string='Total Amount', compute='compute_total_amount', store=True)
    amount_paid = fields.Float(string='Amount Paid', compute='compute_paid_amount', store=True)
    amount_due = fields.Float(string='Amount Due', compute='compute_paid_amount', store=True)
    payment_ids = fields.Many2many('account.payment', string='Payment')
    payment_count = fields.Integer('Payments', compute='_compute_payslip_payments_count')

    def _compute_payslip_payments_count(self):
        self.payment_count = len(self.payment_ids)

    def button_view_payslip_payments(self):
        return {
            'name': _('Payment'),
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.payment_ids.ids)],
        }

    @api.depends('payment_ids', 'payment_ids.state', 'payment_ids.amount')
    def compute_paid_amount(self):
        for slip in self:
            if slip.payment_ids:
                slip.amount_paid = sum([payment.amount for payment in slip.payment_ids.filtered(lambda p: p.state in ('posted', 'reconciled'))])
                slip.amount_due = slip.total_amount - slip.amount_paid
                if slip.amount_due == 0:
                    slip.state = 'paid'
                else:
                    slip.state = 'done'

    @api.depends('line_ids')
    def compute_total_amount(self):
        for slip in self:
            total_amount_new = 0.0
            for line in slip.line_ids:
                if line.salary_rule_id.code == 'NET':
                    total_amount_new += line.total
            slip.total_amount = total_amount_new
            slip.amount_due = slip.total_amount - slip.amount_paid

    def set_to_paid(self):
        self.write({'state': 'paid'})


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('paid', 'Paid'),
        ('close', 'Close'),
    ], string='Status', index=True, readonly=True, copy=False, default='draft')
    total_amount = fields.Float(string='Total Amount', compute='compute_total_amount')
    payment_ids = fields.Many2many('account.payment', string='Payment', compute='_compute_payslip_payments')
    payment_count = fields.Integer('Payments', compute='_compute_payslip_payments')

    def _compute_payslip_payments(self):
        self.payment_ids = self.slip_ids.mapped('payment_ids').ids
        self.payment_count = len(self.payment_ids)

    def button_view_payslip_payments(self):
        return {
            'name': _('Payments'),
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.payment_ids.ids)],
        }

    def compute_total_amount(self):
        for batch in self:
            batch.total_amount = sum([slip.total_amount for slip in batch.slip_ids])

    def batch_wise_payslip_confirm(self):
        for record in self.slip_ids:
            if record.state == 'draft':
                record.action_payslip_done()
        self.state='done'


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    payslip_id = fields.Many2one('hr.payslip', string='Expense', copy=False, help="Expense where the move line come from")

    def reconcile(self, writeoff_acc_id=False, writeoff_journal_id=False):
        res = super(AccountMoveLine, self).reconcile(writeoff_acc_id=writeoff_acc_id, writeoff_journal_id=writeoff_journal_id)
        account_move_ids = [l.move_id.id for l in self if float_compare(l._get_matched_percentage().get(l.move_id.id), 1.0, precision_digits=5) == 0]
        if account_move_ids:
            payslip = self.env['hr.payslip'].search([
                ('move_id', 'in', account_move_ids), ('state', '=', 'done')
            ])
            payslip.set_to_paid()
        return res