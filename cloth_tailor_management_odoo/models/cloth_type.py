# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ClothType(models.Model):
    _name = 'cloth.type'

    name = fields.Char(
        string="Name",
        required=True
    )
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')],
        string="Gender",
        default='male'
    )
    measurement_ids = fields.One2many(
        'cloth.measurement.type',
        'cloth_type_id',
        string="Measurement Types"
    )
