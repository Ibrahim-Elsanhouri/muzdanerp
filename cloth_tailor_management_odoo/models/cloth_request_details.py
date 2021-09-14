# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, SUPERUSER_ID


class ClothRequestDetails(models.Model):
    _name = 'cloth.request.details'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    
    def _default_stage_id(self):
        stage_id = self.env['cloth.request.stage'].search([], order='sequence', limit=1).id
        return stage_id

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stages = self.env['cloth.request.stage'].search(domain, order=order)
        search_domain = [('id', 'in', stages.ids)]
        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    name = fields.Char(
        string='Cloth Request Reference', 
        required=True, 
        copy=False, 
        readonly=True, 
        index=True, 
        default=lambda self: _('New')
    )
    partner_id = fields.Many2one(
        'res.partner',
        string="Customer",
        required=True
    )
    request_date = fields.Date(
        string="Request Date",
        default=fields.Date.context_today,
        required=True
    )
    deadline_date = fields.Date(
        string="Deadline Date",
    )
    company_id = fields.Many2one(
        'res.company', 
        'Company', 
        required=True, 
        index=True, 
        default=lambda self: self.env.company
    )
    user_id = fields.Many2one(
        'res.users',
        string="Responsible",
        default=lambda self: self.env.user
    )
    internal_note = fields.Text(
        'Add an internal note...',
    )
    special_note = fields.Text(
        'Add an special note...',
    )
    stage_id = fields.Many2one(
        'cloth.request.stage', 
        string='Stage', 
        tracking=True, 
        index=True, 
        copy=False,
        group_expand='_read_group_stage_ids',
        default=lambda self: self._default_stage_id()
    )
    lead_id = fields.Many2one(
        'crm.lead',
        readonly=True,
        string="Lead"
    )
    invoices_due_amount = fields.Float('Amount Due', compute='_compute_amount_due')
    measurement_count = fields.Float('Amount Due', compute='_compute_measurements_count')
    tasks_count = fields.Float('Amount Due', compute='_compute_tasks_count')
    sale_orders_count = fields.Float('Amount Due', compute='_compute_sale_orders_count')
    purchase_orders_count = fields.Float('Amount Due', compute='_compute_purchase_orders_count')
    consumption_request_count = fields.Float('Amount Due', compute='_compute_consumption_request_count')
    measurement_ids = fields.Many2many('cloth.request.measurement.cloth.type', compute='_compute_measurement_type_ids')

    def _compute_consumption_request_count(self):
        self.consumption_request_count = self.env['stock.inventory'].search_count([('tailor_request_id', '=', self.id)])

    def _compute_purchase_orders_count(self):
        self.purchase_orders_count = self.env['purchase.order'].search_count([('tailor_request_id', '=', self.id)])

    def _compute_sale_orders_count(self):
        self.sale_orders_count = self.env['sale.order'].search_count([('custom_cloth_request_ids', '=', self.id)])

    def _compute_measurement_type_ids(self):
        measurements = self.env['cloth.request.measurement.cloth.type'].search([('cloth_request_id', '=', self.id)])
        self.measurement_ids = measurements.ids

    def _compute_tasks_count(self):
        tasks = self.env['project.task'].search([('cloth_request_id', '=', self.id)])
        self.tasks_count = len(tasks)

    def _compute_measurements_count(self):
        measurements = self.env['cloth.request.measurement.cloth.type'].search([('cloth_request_id', '=', self.id)])
        self.measurement_count = len(measurements)

    def action_sale_quotations_new(self):
        if not self.partner_id:
            return self.env.ref("cloth_tailor_management_odoo.cloth_request_quotation_partner_action").read()[0]
        else:
            return self.action_new_quotation()

    def action_create_sale_invoice(self):
        action = self.env.ref("account.action_move_out_invoice_type").read()[0]
        form_view = [(self.env.ref('account.view_move_form').id, 'form')]
        if 'views' in action:
            action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
        else:
            action['views'] = form_view
        action['context'] = {
            'default_type': 'out_invoice',
            'default_narration': self.internal_note,
            'default_currency_id': self.company_id.currency_id.id,
            'default_invoice_user_id': self.user_id and self.user_id.id,
            'default_partner_id': self.partner_id.id,
            'default_invoice_partner_bank_id': self.company_id.partner_id.bank_ids[:1].id,
            'default_fiscal_position_id': self.partner_id.property_account_position_id.id,
            'default_invoice_origin': self.name,
            'default_custom_cloth_request_ids': self.id,
            'default_invoice_line_ids': [],
        }
        return action

    # def action_new_quotation(self):
    #     action = self.env.ref("cloth_tailor_management_odoo.custom_sale_action_quotations_new").read()[0]
    #     action['context'] = {
    #         'search_default_partner_id': self.partner_id.id,
    #         'default_partner_id': self.partner_id.id,
    #         'default_origin': self.name,
    #         'default_company_id': self.company_id.id or self.env.company.id,
    #         'default_custom_cloth_request_ids': self.id,
    #     }
    #     return action

    def action_purchase_request_new(self):
        orders = self.env['purchase.order'].sudo().search([('tailor_request_id', '=', self.id)])
        action = self.env.ref('purchase.purchase_rfq').read()[0]
        action['context'] = {
            'default_origin': self.mapped('name'),
            'default_user_id': self.user_id.id,
            'default_tailor_request_id': self.id,
        }
        if len(orders) > 1:
            action['domain'] = [('id', 'in', orders.ids)]
        elif len(orders) == 1:
            action['domain'] = [('id', 'in', orders.ids)]
        else:
            form_view = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = orders.id
        return action

    def action_create_consumption_request(self):
        orders = self.env['stock.inventory'].search([('tailor_request_id', '=', self.id)])
        action = self.env.ref('cloth_tailor_management_odoo.action_consumption_request_form').read()[0]
        action['context'] = {
            'default_name': self.mapped('name'),
            'default_tailor_request_id': self.id,
        }
        if len(orders) > 1:
            action['domain'] = [('id', 'in', orders.ids)]
        elif len(orders) == 1:
            action['domain'] = [('id', 'in', orders.ids)]
        else:
            form_view = [(self.env.ref('cloth_tailor_management_odoo.view_consumption_request_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = orders.id
        return action

    def _compute_amount_due(self):
        invoices = self.env['account.move'].sudo().search([('custom_cloth_request_ids', '=', self.id)])
        self.invoices_due_amount = sum(invoices.mapped('amount_residual_signed'))

    def action_view_invoice(self):
        invoices = self.env['account.move'].sudo().search([('custom_cloth_request_ids', '=', self.id)])
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {
            'default_type': 'out_invoice',
        }
        if len(self) == 1:
            context.update({
                'default_partner_id': self.partner_id.id,
                'default_invoice_origin': self.mapped('name'),
                'default_user_id': self.user_id.id,
            })
        action['context'] = context
        return action

    # def action_view_sale_order(self):
    #     orders = self.env['sale.order'].sudo().search([('custom_cloth_request_ids', '=', self.id)])
    #     action = self.env.ref('sale.action_quotations_with_onboarding').read()[0]
    #     if len(orders) > 1:
    #         action['domain'] = [('id', 'in', orders.ids)]
    #     elif len(orders) == 1:
    #         form_view = [(self.env.ref('sale.view_order_form').id, 'form')]
    #         if 'views' in action:
    #             action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
    #         else:
    #             action['views'] = form_view
    #         action['res_id'] = orders.id
    #     else:
    #         action = {'type': 'ir.actions.act_window_close'}
    #
    #     if len(self) == 1:
    #         context = {
    #             'default_partner_id': self.partner_id.id,
    #             'default_origin': self.mapped('name'),
    #             'default_user_id': self.user_id.id,
    #         }
    #     action['context'] = context
    #     return action

    def action_view_purchase_order(self):
        orders = self.env['purchase.order'].sudo().search([('tailor_request_id', '=', self.id)])
        action = self.env.ref('purchase.purchase_rfq').read()[0]
        if len(orders) > 1:
            action['domain'] = [('id', 'in', orders.ids)]
        elif len(orders) == 1:
            form_view = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = orders.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        if len(self) == 1:
            context = {
                'default_partner_id': self.partner_id.id,
                'default_origin': self.mapped('name'),
                'default_user_id': self.user_id.id,
            }
        action['context'] = context
        return action

    def action_view_consumption_req(self):
        orders = self.env['stock.inventory'].sudo().search([('tailor_request_id', '=', self.id)])
        action = self.env.ref('cloth_tailor_management_odoo.action_consumption_request_form').read()[0]
        if len(orders) > 1:
            action['domain'] = [('id', 'in', orders.ids)]
        elif len(orders) == 1:
            form_view = [(self.env.ref('cloth_tailor_management_odoo.view_consumption_request_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = orders.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        if len(self) == 1:
            context = {
            'default_name': self.mapped('name'),
            'default_tailor_request_id': self.id,
            }
        action['context'] = context
        return action

    def action_view_measurement(self):
        measurements = self.env['cloth.request.measurement.cloth.type'].search([('cloth_request_id', '=', self.id)])
        action = self.env.ref('cloth_tailor_management_odoo.action_cloth_request_measurement').read()[0]
        action['context'] = {
            'default_partner_id': self.partner_id.id,
            'default_company_id': self.company_id.id,
            'default_cloth_request_id': self.id,
        }
        if len(measurements) > 1:
            action['domain'] = [('id', 'in', measurements.ids)]
        else:
            form_view = [(self.env.ref('cloth_tailor_management_odoo.cloth_request_measurement_form_view').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = measurements.id

        return action

    def action_view_tasks(self):
        tasks = self.env['project.task'].sudo().search([('cloth_request_id', '=', self.id)])
        action = self.env.ref('project.action_view_task').read()[0]
        if len(tasks) > 1:
            action['domain'] = [('id', 'in', tasks.ids)]
        elif len(tasks) == 1:
            form_view = [(self.env.ref('project.view_task_form2').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = tasks.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        action['context'] = {}
        return action

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('cloth.request.details') or _('New')
        records = super(ClothRequestDetails, self).create(vals)
        return records

    def write(self, vals):
        if vals.get('stage_id', False):
            new_stage = self.env['cloth.request.stage'].browse(vals.get('stage_id', False))
            if self.stage_id.sequence < new_stage.sequence:
                tasks = self.env['project.task'].search([
                    ('cloth_request_id', '=', self.id), ('cloth_req_stage_id', '=', self.stage_id.id)
                ])
                closed_stage = self.env['project.task.type'].search([('project_ids', 'in', self.stage_id.project_id.ids), ('closed', '=', True)], limit=1)
                tasks.write({'stage_id': closed_stage.id})
            elif self.stage_id.sequence > new_stage.sequence:
                tasks = self.env['project.task'].search([
                    ('cloth_request_id', '=', self.id), ('cloth_req_stage_id', '=', new_stage.id)
                ])
                closed_stage = self.env['project.task.type'].search([('project_ids', 'in', self.stage_id.project_id.ids)], order='sequence', limit=1)
                tasks.write({'stage_id': closed_stage.id})
        return super(ClothRequestDetails, self).write(vals)

    def name_get(self):
        result = []
        for rec in self:
            name = rec.name
            if rec.partner_id and rec.name:
                name = rec.name + " - " + rec.partner_id.name
            result.append((rec.id, name))
        return result


class ClothRequestMeasurementClothType(models.Model):
    _name = 'cloth.request.measurement.cloth.type'
    _rec_name = 'cloth_type_id'

    cloth_request_id = fields.Many2one(
        'cloth.request.details',
        string="Cloth Request"
    )
    partner_id = fields.Many2one('res.partner', related='cloth_request_id.partner_id')
    gender = fields.Selection([
            ('male', 'Male'),
            ('female', 'Female')
    ], string="Gender", default='male')
    cloth_type_id = fields.Many2one(
        'cloth.measurement.details',
        domain="[('partner_id', '=', partner_id)]",
        string="Cloth Type",
    )
    quantity = fields.Float(
        string="Quantity"
    )
    uom_id = fields.Many2one(
        'uom.uom',
        string="Unit of Measure"
    )
    fabric_remarks = fields.Char(
        string="Fabric"
    )
    fabric_color = fields.Char(
        string="Fabric Color"
    )
    measurement_ids = fields.One2many(
        'cloth.measurement.details.line',
        'cloth_request_measurement_type_id',
        string="Measurement Types"
    )
    company_id = fields.Many2one(
        'res.company',
        'Company',
        required=True,
        index=True,
        default=lambda self: self.env.company
    )
    measurement_icon = fields.Image("Icon", max_width=128, max_height=128, store=True)
    style_ids = fields.One2many('cloth.req.style.line', 'cloth_req_measurement_id', string='Styles')

    def action_get_measurement_line(self):
        for rec in self:
            if rec.cloth_type_id and not rec.style_ids:
                for style_line in rec.cloth_type_id.style_ids:
                    self.env['cloth.req.style.line'].create({
                        'cloth_req_measurement_id': rec.id,
                        'style_type_id': style_line.id,
                        'style_id': style_line.style_id.id,
                        'measurement_icon': style_line.measurement_icon,
                        'note': style_line.note,
                    })
            if rec.cloth_type_id and not rec.measurement_ids:
                for line in rec.cloth_type_id.measurement_ids:
                    new_line_id = self.env['cloth.measurement.details.line'].create({
                        'cloth_request_measurement_type_id': rec.id,
                        'measurement_details_line_id': line.id,
                        'measurement': line.measurement,
                        'uom_id': line.uom_id.id,
                        'measurement_icon': line.measurement_icon,
                        'cloth_measurement_type_id': line.cloth_measurement_type_id.id
                    })

    def action_update_all_measurement(self):
        for line in self.measurement_ids:
            line.action_update_line_measurement()

    @api.model
    def create(self, vals):
        records = super(ClothRequestMeasurementClothType, self).create(vals)
        for rec in records:
            stage_ids = self.env['cloth.request.stage'].search([])
            for stage_id in stage_ids:
                is_create_task = stage_id.create_task
                if is_create_task and stage_id.project_id:
                    self.env['project.task'].create({
                        'name': stage_id.name,
                        'project_id': stage_id.project_id.id,
                        'cloth_request_id': rec.cloth_request_id.id,
                        'cloth_type_id': rec.cloth_type_id.id,
                        'cloth_req_stage_id': stage_id.id,
                    })
        return records


class ClothReqStyleLine(models.Model):
    _name = 'cloth.req.style.line'
    _description = 'Style line'

    cloth_req_measurement_id = fields.Many2one(
        'cloth.request.measurement.cloth.type',
        string="Cloth Measurement"
    )
    style_type_id = fields.Many2one('cloth.measurement.type', string='Type')
    style_id = fields.Many2one('cloth.style', string='Style')
    measurement_icon = fields.Image("Icon", max_width=128, max_height=128, store=True)
    note = fields.Char('Notes')
