from odoo import models, fields, api


class ClothStyle(models.Model):
    _name = 'cloth.style'

    name = fields.Char('Style name', required=True)
    style_type_id = fields.Many2one('cloth.measurement.type', string='Type')
    cloth_type_id = fields.Many2one('cloth.type', required=True)
    style_icon = fields.Image("Icon", max_width=128, max_height=128, store=True)
