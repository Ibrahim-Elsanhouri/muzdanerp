# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)

class ClothRequestTaskWizard(models.TransientModel):
    _name = "cloth.request.task.wizard"

    @api.model
    def default_get(self, fields):
        res = super(ClothRequestTaskWizard, self).default_get(fields)
        model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        if active_id and model == 'cloth.request.details':
            record = self.env[model].browse(active_id)
            res.update({
                'partner_id': record.partner_id.id,
                'company_id': record.company_id.id,
                'request_id': record.id,
                'deadline_date': record.deadline_date,
                'description': record.internal_note,
                'name':record.name
            })
        return res

    name = fields.Char(
        string="Name"
    )
    partner_id = fields.Many2one(
        'res.partner',
        string="Customer",
    )
    company_id = fields.Many2one(
        'res.company', 
        'Company', 
        default=lambda self: self.env.company
    )
    request_id = fields.Many2one(
        'cloth.request.details',
        string="Cloth Request"
    )
    user_id = fields.Many2one(
        'res.users',
        required=True,
        string="Assigned to"
    )
    project_id = fields.Many2one(
        'project.project',
        string="Project"
    )
    deadline_date = fields.Date(
        string="Deadline"
    )
    description = fields.Html(
        string='Description'
    )

    def create_cloth_request_task(self):
        vals = {
            'partner_id': self.partner_id.id,
            'company_id': self.company_id.id or self.env.company.id,
            'cloth_request_id': self.request_id.id,
            'user_id': self.user_id.id,
            'project_id': self.project_id.id,
            'date_deadline': self.deadline_date,
            'description': self.description,
            'name': self.name
        }
        task_id = self.env['project.task'].sudo().create(vals)
        action = self.env.ref("project.action_view_task").read()[0]
        action['views'] = [(self.env.ref('project.view_task_form2').id, 'form')]
        action['res_id'] = task_id.id
        return action