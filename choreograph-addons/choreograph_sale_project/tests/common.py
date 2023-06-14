# -*- encoding: utf-8 -*-

from odoo.tests.common import TransactionCase


class TestSaleCommon(TransactionCase):
    """Setup with sale test configuration."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # create client
        cls.client = cls.env['res.partner'].create({
            'name': 'Client test',
        })

        # create articles
        cls.article1 = cls.env['product.template'].create({
            'name': 'Article task in project',
            'detailed_type': 'service',
            'service_tracking': 'task_in_project',
        })
        cls.article2 = cls.env['product.template'].create({
            'name': 'Article project only',
            'detailed_type': 'service',
            'service_tracking': 'project_only',
        })

        # create sale order
        cls.sale_order = cls.env['sale.order'].create({
            'partner_id': cls.client.id,
        })

        cls.env['sale.order.line'].create({
            'name': cls.article2.name,
            'product_uom_qty': 1,
            'product_uom': cls.article2.uom_id.id,
            'price_unit': cls.article2.list_price,
            'tax_id': False,
            'order_id': cls.sale_order.id,
            'product_id': cls.article2.product_variant_id.id,
        })
        cls.env['sale.order.line'].create({
            'name': cls.article1.name,
            'product_uom_qty': 1,
            'product_uom': cls.article1.uom_id.id,
            'price_unit': cls.article1.list_price,
            'tax_id': False,
            'order_id': cls.sale_order.id,
            'product_id': cls.article1.product_variant_id.id,
        })
