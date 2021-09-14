# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    custom_cloth_request_ids = fields.Many2one(
        'cloth.request.details',
        string="Cloth Requests",
    )

    def _create_invoices(self, grouped=False, final=False):
        res = super(SaleOrder, self)._create_invoices(grouped, final)
        for rec in self:
            if rec.custom_cloth_request_ids:
                res.write({'custom_cloth_request_ids': rec.custom_cloth_request_ids.id})
        return res

    @api.constrains('custom_cloth_request_ids')
    def check_cloth_request_assigned(self):
        sale_order_count = self.env['sale.order'].search_count([('custom_cloth_request_ids', '=', self.custom_cloth_request_ids.id)])
        if sale_order_count >= 2 and self.custom_cloth_request_ids:
            raise ValidationError('You can not assign cloth request that is already attached to a sale order!')