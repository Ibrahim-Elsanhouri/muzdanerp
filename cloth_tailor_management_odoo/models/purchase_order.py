from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    tailor_request_id = fields.Many2one(
        'cloth.request.details',
        string="Cloth Requests",
    )

    def action_view_invoice(self):
        result = super(PurchaseOrder, self).action_view_invoice()
        if self.tailor_request_id:
            result['context']['default_custom_cloth_request_ids'] = self.tailor_request_id.id
        return result
