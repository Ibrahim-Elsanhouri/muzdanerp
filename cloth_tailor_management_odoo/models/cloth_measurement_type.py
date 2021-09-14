# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ClothMeasurmentType(models.Model):
    _name = 'cloth.measurement.type'

    cloth_type_id = fields.Many2one(
        'cloth.type',
        string="Cloth Type"
    )
    sequence_no = fields.Char(
        string="Sequence No.",
        required=True
    )
    name = fields.Char(
        string="Name",
        required=True
    )
    uom_id = fields.Many2one(
        'uom.uom',
        string="Unit of Measure",
        required=True
    )
    measurement_ids = fields.One2many(
        'cloth.measurement.type',
        'cloth_type_id',
        string="Measurement Types"
    )
    measurement_icon = fields.Image("Icon", max_width=128, max_height=128, store=True)