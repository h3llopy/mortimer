# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, fields, api, _
from odoo.exceptions import Warning,UserError


class sale_order_line(models.Model):
    _inherit = "sale.order.line"
    
    sh_sale_barcode_scanner_is_last_scanned = fields.Boolean(string = "Last Scanned?")

class sale_order(models.Model):
    _name = "sale.order"
    _inherit = ["barcodes.barcode_events_mixin", "sale.order"]   
       
    
    def _add_product(self, barcode):        
        

                            
        is_last_scanned = False
        sequence = 0
        warm_sound_code = ""   
        
        if self.env.user.company_id.sudo().sh_sale_barcode_scanner_last_scanned_color:  
            is_last_scanned = True          
        
        if self.env.user.company_id.sudo().sh_sale_barcode_scanner_move_to_top:
            sequence = -1
            
        if self.env.user.company_id.sudo().sh_sale_barcode_scanner_warn_sound:
            warm_sound_code = "SH_BARCODE_SCANNER_"      

        if self.env.user.company_id.sudo().sh_sale_barcode_scanner_auto_close_popup:
            warm_sound_code += "AUTO_CLOSE_AFTER_" + str(self.env.user.company_id.sudo().sh_sale_barcode_scanner_auto_close_popup) + "_MS&"   
        
        #step 1 make sure order in proper state.
        if self and self.state in ["cancel","done"]:
            selections = self.fields_get()["state"]["selection"]
            value = next((v[1] for v in selections if v[0] == self.state), self.state)
            raise UserError(_(warm_sound_code + "You can not scan item in %s state.") %(value))
                
        #step 2 increaset product qty by 1 if product not in order line than create new order line.
        elif self:
                             
            self.order_line.update({
                'sh_sale_barcode_scanner_is_last_scanned': False,
                'sequence': 0,
                })   
                     
            
            search_lines = False
            domain = []
            is_multi_barcode = self.env.user.has_group('sh_barcode_scanner_adv.group_sh_barcode_scanner_multi_barcode')
                            
            if self.env.user.company_id.sudo().sh_sale_barcode_scanner_type == "barcode":            
                if is_multi_barcode:        
                    search_lines = self.order_line.filtered(lambda ol: ol.product_id.barcode == barcode)
                    if not search_lines:
                        for line in self.order_line:
                            if line.product_id and line.product_id.barcode_line_ids:
                                for barcode_line in line.product_id.barcode_line_ids:
                                    if barcode_line.name == barcode:
                                        search_lines = line
                                        break
                        
                        
                        
                    domain = ['|',
                              ("barcode","=",barcode),
                              ("barcode_line_ids.name","=",barcode)
                              ] 
                    
                else:
                    search_lines = self.order_line.filtered(lambda ol: ol.product_id.barcode == barcode)
                    domain = [("barcode","=",barcode)]
             
            elif self.env.user.company_id.sudo().sh_sale_barcode_scanner_type == "int_ref":            
                search_lines = self.order_line.filtered(lambda ol: ol.product_id.default_code == barcode)   
                domain = [("default_code","=",barcode)]
                 
            elif self.env.user.company_id.sudo().sh_sale_barcode_scanner_type == "both":            
                if is_multi_barcode:        
                    search_lines = self.order_line.filtered(lambda ol: ol.product_id.barcode == barcode or ol.product_id.default_code == barcode)  
                    if not search_lines:
                        for line in self.order_line:
                            if line.product_id and line.product_id.barcode_line_ids:
                                for barcode_line in line.product_id.barcode_line_ids:
                                    if barcode_line.name == barcode:
                                        search_lines = line
                                        break    
                                    
                    domain = ["|","|",
                        ("default_code","=",barcode),
                        ("barcode","=",barcode),
                        ("barcode_line_ids.name","=",barcode)                   
                    ]                                                  
            
            if search_lines:
                for line in search_lines:
                    line.product_uom_qty += 1
                    line.sh_sale_barcode_scanner_is_last_scanned = is_last_scanned
                    line.sequence = sequence                    
                    line.product_id_change()
                    line._onchange_discount()
                    
                    break
            else:
                search_product = self.env["product.product"].search(domain, limit = 1)
                if search_product:
                    vals = {
                        'product_id': search_product.id,
                        'name': search_product.name,
                        'product_uom': search_product.uom_id.id,
                        'product_uom_qty': 1,
                        'price_unit': search_product.lst_price,
                        'sh_sale_barcode_scanner_is_last_scanned': is_last_scanned,
                        'sequence' : sequence,             
                    }
                    if search_product.uom_id:
                        vals.update({
                            "product_uom": search_product.uom_id.id,                            
                        })                      

                     
                    new_order_line = self.order_line.new(vals)                                                                    
                    self.order_line += new_order_line
                    new_order_line.product_id_change()
                    new_order_line._onchange_discount() 
                    
                    # ==========================================================================
                    # To Apply Discount
                    # ==========================================================================
                    if (new_order_line and new_order_line.product_id and new_order_line.product_uom and
                            self.partner_id and self.pricelist_id and
                            self.pricelist_id.discount_policy == 'without_discount' and
                            self.env.user.has_group('product.group_discount_per_so_line')):
                                       
                        new_order_line.discount = 0.0
                        product = new_order_line.product_id.with_context(
                            lang=self.partner_id.lang,
                            partner=self.partner_id,
                            quantity=new_order_line.product_uom_qty,
                            date=self.date_order,
                            pricelist=self.pricelist_id.id,
                            uom=new_order_line.product_uom.id,
                            fiscal_position=self.env.context.get('fiscal_position')
                        )
                
                        product_context = dict(self.env.context, partner_id=self.partner_id.id, date=self.date_order, uom=new_order_line.product_uom.id)
                
                        price, rule_id = self.pricelist_id.with_context(product_context).get_product_price_rule(new_order_line.product_id, new_order_line.product_uom_qty or 1.0, self.partner_id)
                        new_list_price, currency = new_order_line.with_context(product_context)._get_real_price_currency(product, rule_id, new_order_line.product_uom_qty, new_order_line.product_uom, self.pricelist_id.id)
                
                        if new_list_price != 0:
                            if self.pricelist_id.currency_id != currency:
                                # we need new_list_price in the same currency as price, which is in the SO's pricelist's currency
                                new_list_price = currency._convert(
                                    new_list_price, self.pricelist_id.currency_id,
                                    self.company_id or self.env.company, self.date_order or fields.Date.today())
                            discount = (new_list_price - price) / new_list_price * 100
                            if (discount > 0 and new_list_price > 0) or (discount < 0 and new_list_price < 0):
                                new_order_line.discount = discount
                            
                    # ==========================================================================
                    # To Apply Discount
                    # ==========================================================================
                                                                  
                    
                else:                   
                    raise UserError(_(warm_sound_code + "Scanned Internal Reference/Barcode not exist in any product!"))                          
                
            
            
                
    def on_barcode_scanned(self, barcode):
        self._add_product(barcode)

      

            
                