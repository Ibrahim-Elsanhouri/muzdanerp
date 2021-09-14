from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    consumption_location_id = fields.Many2one(
        'stock.location', "Consumption Location", company_dependent=True, check_company=True,
        domain="[('usage', '=', 'inventory'), '|', ('company_id', '=', False), ('company_id', '=', allowed_company_ids[0])]",
        help="This stock location will be used, instead of the default one, as the source location for stock moves generated when you do an inventory consumption.")