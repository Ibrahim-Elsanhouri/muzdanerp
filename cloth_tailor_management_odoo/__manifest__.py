# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Tailor Management (Clothes)',
    'version' : '2.1.1',
    'price' : 99.0,
    'currency': 'EUR',
    'category': 'Sales/Sales',
    'license': 'Other proprietary',
    'live_test_url': 'https://youtu.be/0cKfAEsun7Y',
    'images': [
        'static/description/img.jpg',
    ],
    'description': """

This app allows you to manage tailor business or tailor shop in Odoo by using below listed features as per screenshots.
Main Features:
- Allow you to create your custom stages under configuration to manage your tailor request from customers.
- Allow you to create cloth types under configuration which can be used during measurement of customer clothes and tailor requests.
- Allow you to record customer measurements of clothes one time and you can use it on cloth requests every time when a customer asks you to make cloth.
- Allow you to create tailor requests for customers and show measurements of that customer cloth type.
- Cloth measurement history for customers to store in the system.
- Allow you to print tailor requests and customer measurement reports.
- You can also update measurements directly on request.
- Allow you to create sales quotations from cloth requests and also allow you to create project tasks from request.
- Allow your customers to view tailor requests and measurements in the portal my account of your website.
- Allow you to create a tailor request from CRM Opportunity form which will link CRM with Tailor Application.
- Two new groups (Tailor User and Manager) are introduced for the Tailor application which you can find on User form.
- For more details please check below screenshots and watch the video.

    """,
    'summary' : 'Manage tailor business or tailor shop in Odoo.',
    'author' : 'Probuse Consulting Service Pvt. Ltd.',
    'website' : 'wwww.probuse.com',
    'depends' : [
        'sale',
        'crm',
        'website',
        'project',
        'purchase',
        'uom',
        'stock',
        'product',
    ],
    'support': 'contact@probuse.com',
    'data' : [
        'security/cloth_request_security.xml',
        'security/ir.model.access.csv',
        'wizard/cloth_request_wizard_view.xml',
        'wizard/create_task_view.xml',
	    'data/ir_sequence_data.xml',
        'views/cloth_request_details_view.xml',
        'views/cloth_measurement_type_view.xml',
        'views/cloth_type_view.xml',
        'views/cloth_request_stage_views.xml',
        'views/sale_order_view.xml',
        'views/account_move_view.xml',
        'views/cloth_measurement_details_view.xml',
        'report/cloth_request_report_template.xml',
        'report/cloth_request_report.xml',
        'views/crm_lead_views.xml',
        'views/template.xml',
        'views/task_view.xml',
        'views/cloth_style.xml',
        'views/menu.xml',
        'views/purchase_order.xml',
        'views/stock_inventory.xml',
        'views/product.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
