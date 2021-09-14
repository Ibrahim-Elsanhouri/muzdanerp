# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Stage(models.Model):
    _name = "cloth.request.stage"
    _description = "Cloth Request Stages"
    _rec_name = 'name'
    _order = "sequence, name, id"

    name = fields.Char('Stage Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")
    fold = fields.Boolean('Folded', help='This stage is folded in the kanban view when there are no records in that stage to display.')
    active = fields.Boolean(default=True)
    create_task = fields.Boolean('Create Task?', default=False)
    project_id = fields.Many2one('project.project', 'Project')
