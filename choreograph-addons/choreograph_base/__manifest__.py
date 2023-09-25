# -*- coding: utf-8 -*-
{
	'name': 'Choreograph Base',
	'version': '16.0.0.1',
	'license': 'LGPL-3',
	'category': 'Tools',
	'summary': 'choreograph base module',
	'sequence': -96,
	'description': """This module allows to install base features will be used by all other modules""",
	'author': 'ArkeUp',
	'website': 'https://arkeup.com',
	'depends': [
		'base',
		'mail',
		'maas_website',
	],
	'data': [
		# data
		'data/ir_sequence.xml',
		# security
		# views
		"views/res_partner_views.xml",
		"views/mail_template_views.xml",
	],
	'assets': {
		'web._assets_primary_variables': [],
		'web.assets_backend': [
			'choreograph_base/static/src/xml/*.xml'
		],
		'web.assets_frontend': [],
	},
	'installable': True,
	'application': False,
}
