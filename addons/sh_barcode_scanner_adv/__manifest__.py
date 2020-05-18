# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.
{
    "name": "All In One Barcode Scanner-Advance",

    'author' : 'Softhealer Technologies',
    
    'website': 'https://www.softhealer.com',
        
    "support": "support@softhealer.com",    
        
    'version': '13.0.1',
        
    "category": "Extra Tools",

    "summary": """barcode scanner app odoo, package all in one barcode, sale barcode scanner, purchase in barcode module, invoice in barcode, inventory barcode, stock barcode, bom using barcode, scrap in barcode, multi barcode of one product""",   
        
    'description': """
    
  Do your time-wasting in sales, purchases, invoices, inventory, bill of material, scrap operations by manual product selection? So here are the solutions these modules useful do quick operations of sales, purchases, invoicing and inventory, bill of material, scrap using the barcode scanner. Multi barcode feature allows you to assign multi barcodes on the product. You no need to select a product and do one by one. scan it and you do! So be very quick in all operations of odoo and cheers!

 All In One Barcode Scanner - Sales, Purchase, Invoice, Inventory, BOM, Scrap Odoo.
Operations Of Sales, Purchase Using Barcode, Invoice Using Barcode ,Inventory Using Barcode, Bill Of Material Using Barcode, Scrap Using Barcode Module, Sales Barcode Scanner,Purchase Barcode Scanner, Invoice Barcode Scanner, Inventory Barcode Scanner,Bom Barcode Scanner Odoo.
 Barcode Scanner App,Package All in one barcode scanner,  Operations Of Sales, Purchase In Barcode Module, Invoice In Barcode, Inventory In Barcode, Bom In Barcode, Scrap Using Barcode,Sales Barcode Scanner,Purchase Barcode Scanner, Invoice Barcode Scanner, Inventory Barcode Scanner,Bom Barcode Scanner, Single Product Multi Barcode  Odoo.


     
     
     """,
    
    "depends": ['purchase','sale_management','barcodes','account','stock','mrp','sale'],
    
    "data": [
        
    'security/multi_barcode.xml',
    'security/ir.model.access.csv',
    'views/product_view.xml',    
    
    "views/res_config_settings_views.xml",
    "views/sale_view.xml",
    "views/purchase_view.xml",
    "views/stock_view.xml",
    "views/account_view.xml",
    "views/mrp_view.xml",
    "views/assets.xml",
    
    
    ],    
    'images': ['static/description/background.png',],            
    
    "installable": True,    
    "application": True,    
    "autoinstall": False,
    "price": 50,
    "currency": "EUR"        
}
