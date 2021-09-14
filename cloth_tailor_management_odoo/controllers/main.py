# -*- coding: utf-8 -*-

import base64
from odoo import http, _
from odoo.http import request
from odoo.osv.expression import OR
from odoo.addons.portal.controllers.portal import CustomerPortal as website_account

class website_account(website_account):
    def _prepare_portal_layout_values(self): #odoo11
        values = super(website_account, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        tailor_request_ids = request.env['cloth.request.details'].sudo().search([
            ('partner_id', '=', partner.id)
        ])
        tailor_measurement_ids = request.env['cloth.measurement.details'].sudo().search([
            ('partner_id', '=', partner.id)
        ])
        values.update({
        'tailor_request_count': len(tailor_request_ids.ids),
        'tailor_measurement_count': len(tailor_measurement_ids.ids)
        })
        return values

    @http.route([
        '''/my/tailor/requests'''
    ], type='http', auth="public", website=True)
    def custom_my_tailor_request(self, search=None, search_in='membership', sortby=None, **post):
        searchbar_sortings = {
            'request_date': {'label': _('Request Date'), 'order': 'request_date desc'},
            'deadline_date': {'label': _('Deadline Date'), 'order': 'deadline_date desc'},
            'stage_id': {'label': _('Status'), 'order': 'stage_id desc'},
        }
        searchbar_inputs = {
            'cloth_type': {'input': 'cloth_type', 'label': _('Search <span class="nolabel"> (in ClothType)</span>')},
            'gender': {'input': 'gender', 'label': _('Search in Gender')},
            'stage_id': {'input': 'stage_id', 'label': _('Search in Status')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }

        partner = request.env.user.partner_id
        domain = [('partner_id', '=', partner.id)]

        # default sortby order
        if not sortby:
            sortby = 'request_date'
        sort_order = searchbar_sortings[sortby]['order']

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('cloth_type', 'all'):
                search_domain = OR([search_domain, [('cloth_type_id', 'ilike', search)]])
            if search_in in ('gender', 'all'):
                search_domain = OR([search_domain, [('gender', 'ilike', search)]])
            if search_in in ('stage_id', 'all'):
                search_domain = OR([search_domain, [('stage_id', 'ilike', search)]])
            domain += search_domain

        tailor_request_ids = request.env['cloth.request.details'].sudo().search(
            domain, order=sort_order
        )
        values={
            'tailor_requests': tailor_request_ids,
            'page_name': 'tailor_request_page',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
        }
        return request.render(
            "cloth_tailor_management_odoo.display_tailor_request",
            values
        )

    @http.route(['/my/tailor/request/<int:tailor_request_id>'], type='http', auth="public", website=True)
    def custom_portal_my_tailor_request(self, tailor_request_id, **kw):
        tailor_request_id = request.env['cloth.request.details'].browse(tailor_request_id)
        values = {
            'tailor_request_id': tailor_request_id,
            'page_name': 'tailor_request_detail_page',
        }
        return request.render(
            "cloth_tailor_management_odoo.portal_custom_tailor_request_details",
            values
        )

    @http.route(['/my/tailor/request/measurement/<int:line>'], type='http', auth="public", website=True)
    def custom_portal_my_tailor_request_measurement(self, line, **kw):
        measurement_type_id = request.env['cloth.request.measurement.cloth.type'].browse(line)
        values = {
            'measurement_type_id': measurement_type_id,
            'page_name': 'cloth_request_measurement_cloth_type_page',
        }
        return request.render(
            "cloth_tailor_management_odoo.portal_custom_tailor_request_details_measurement",
            values
        )

    @http.route([
        '''/my/tailor/measurements'''
    ], type='http', auth="public", website=True)
    def custom_my_tailor_measurement(self, **post):
        partner = request.env.user.partner_id
        domain = [('partner_id', '=', partner.id)]
        tailor_measurement_ids = request.env['cloth.measurement.details'].sudo().search(
            domain
        )
        values={
            'tailor_measurements': tailor_measurement_ids,
            'page_name': 'tailor_measurement_page',
        }
        return request.render(
            "cloth_tailor_management_odoo.display_tailor_measurments",
            values
        )

    @http.route(['/my/tailor/measurement/<int:tailor_measurement_id>'], type='http', auth="public", website=True)
    def custom_portal_my_tailor_measurement(self, tailor_measurement_id, **kw):
        tailor_measurement_id = request.env['cloth.measurement.details'].browse(tailor_measurement_id)
        values = {
            'tailor_measurement_id': tailor_measurement_id,
            'page_name': 'tailor_measurement_detail_page',
        }
        return request.render(
            "cloth_tailor_management_odoo.portal_custom_tailor_measurement_details",
            values
        )

# class CustomWebsiteTailorRequest(http.Controller):