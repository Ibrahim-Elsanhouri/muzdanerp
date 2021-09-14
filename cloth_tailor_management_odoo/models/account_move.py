# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
	_inherit = 'account.move'

	custom_cloth_request_ids = fields.Many2one(
		'cloth.request.details',
		string="Cloth Requests"
	)

	# @api.constrains('custom_cloth_request_ids')
	# def check_cloth_request_assigned(self):
	# 	invoices_count = self.env['account.move'].search_count(
	# 		[('custom_cloth_request_ids', '=', self.custom_cloth_request_ids.id), ('type', '!=', 'entry')])
	# 	if invoices_count >= 2 and self.custom_cloth_request_ids:
	# 		raise ValidationError('You can not assign cloth request that is already attached to an Invoice!')
