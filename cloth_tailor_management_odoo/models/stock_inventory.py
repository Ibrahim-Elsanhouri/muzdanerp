from odoo import models, fields, api, _


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    tailor_request_id = fields.Many2one('cloth.request.details', string='Cloth Request')

    def action_open_inventory_lines(self):
        self.ensure_one()
        if self.tailor_request_id:
            action = {
                'type': 'ir.actions.act_window',
                'views': [(self.env.ref('cloth_tailor_management_odoo.stock_consumption_line_tree').id, 'tree')],
                'view_mode': 'tree',
                'name': _('Inventory Lines'),
                'res_model': 'stock.inventory.line',
            }
            context = {
                'default_is_editable': True,
                'default_inventory_id': self.id,
                'default_company_id': self.company_id.id,
            }
            # Define domains and context
            domain = [
                ('inventory_id', '=', self.id),
                ('location_id.usage', 'in', ['internal', 'transit'])
            ]
            if self.location_ids:
                context['default_location_id'] = self.location_ids[0].id
                if len(self.location_ids) == 1:
                    if not self.location_ids[0].child_ids:
                        context['readonly_location_id'] = True

            if self.product_ids:
                if len(self.product_ids) == 1:
                    context['default_product_id'] = self.product_ids[0].id

            action['context'] = context
            action['domain'] = domain
            return action
        else:
            return super(StockInventory, self).action_open_inventory_lines()


class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    qty_to_consume = fields.Float('Qty to Consume')

    def _get_virtual_location(self):
        if self.inventory_id.tailor_request_id:
            return self.product_id.with_context(force_company=self.company_id.id).consumption_location_id
        return super(StockInventoryLine, self)._get_virtual_location()

    @api.onchange('qty_to_consume')
    def _compute_product_quantity(self):
        for rec in self:
            rec.product_qty = rec.theoretical_qty - rec.qty_to_consume

