# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ClothMeasurmentDetails(models.Model):
    _name = 'cloth.measurement.details'
    _rec_name = 'cloth_type_id'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    partner_id = fields.Many2one(
        'res.partner',
        string="Customer",
        required=True
    )
    measurement_ref = fields.Char('Reference', required=True)
    measurement_date = fields.Date(
        default=fields.Date.context_today,
        string="Date"
    )
    cloth_type_id = fields.Many2one(
        'cloth.type',
        string="Cloth Type",
        required=True
    )
    user_id = fields.Many2one(
        'res.users',
        string="Responsible",
        default=lambda self: self.env.user
    )
    company_id = fields.Many2one(
        'res.company',
        required=True, 
        default=lambda self: self.env.company,
        string="Company"
    )
    internal_note = fields.Text(
        'Add an internal note...',
    )
    measurement_ids = fields.One2many(
        'cloth.measurement.details.line',
        'cloth_measurement_id',
        string="Measurement Types"
    )
    style_ids = fields.One2many('cloth.style.line', 'cloth_measurement_id', string='Styles')

    def name_get(self):
        result = []
        for rec in self:
            name = rec.cloth_type_id.name
            if rec.measurement_ref:
                name = rec.cloth_type_id.name + " - " + rec.measurement_ref
            result.append((rec.id, name))
        return result

    def action_create_request_line(self):
        for rec in self:
            if rec.cloth_type_id and not rec.measurement_ids:
                for line in rec.cloth_type_id.measurement_ids:
                    new_line_id = self.env['cloth.measurement.details.line'].create({
                        'cloth_measurement_id': rec.id,
                        'uom_id': line.uom_id.id,
                        'measurement_icon': line.measurement_icon,
                        'cloth_measurement_type_id': line.id,
                    })


class ClothStyleLine(models.Model):
    _name = 'cloth.style.line'
    _description = 'Style line'

    cloth_measurement_id = fields.Many2one(
        'cloth.measurement.details',
        string="Cloth Measurement"
    )
    style_type_id = fields.Many2one('cloth.measurement.type', string='Type')
    style_id = fields.Many2one('cloth.style', string='Style')
    measurement_icon = fields.Image("Icon", max_width=128, max_height=128, store=True)
    note = fields.Char('Notes')


class ClothMeasurementDetailsLine(models.Model):
    _name = 'cloth.measurement.details.line'
    
    cloth_measurement_id = fields.Many2one(
        'cloth.measurement.details',
        string="Cloth Measurement"
    )
    cloth_measurement_type_id = fields.Many2one(
        'cloth.measurement.type',
        string="Measurement Type",
    )
    uom_id = fields.Many2one(
        'uom.uom',
        string="Unit of Measure"
    )
    measurement = fields.Float(
        string="Measurement"
    )
    # cloth_request_id = fields.Many2one(
    #     'cloth.request.details',
    #     string="Cloth Request"
    # )
    cloth_request_measurement_type_id = fields.Many2one(
        'cloth.request.measurement.cloth.type',
        string="Cloth Request"
    )
    measurement_details_line_id = fields.Many2one(
        'cloth.measurement.details.line',
        string="Measurement Line"
    )
    measurement_icon = fields.Image("Icon", max_width=128, max_height=128, store=True)

    def action_update_line_measurement(self):
        for rec in self:
            if rec.measurement_details_line_id:
                rec.measurement_details_line_id.measurement = rec.measurement
