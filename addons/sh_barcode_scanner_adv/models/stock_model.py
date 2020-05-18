# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError



class StockInventoryLine(models.Model):
    _inherit = "stock.inventory.line"
    
    sequence = fields.Integer(string='Sequence', default=0)
    sh_inven_adjt_barcode_scanner_is_last_scanned = fields.Boolean(string = "Last Scanned?")  
    
class StockInventory(models.Model):
    _name = "stock.inventory"
    _inherit = ['barcodes.barcode_events_mixin', 'stock.inventory']
    
   
    def action_start_sh_inventory_adjust_barcode_scanning(self):
        self.ensure_one()
        action_tree = self.action_start()  
        action = {
            'type': 'ir.actions.act_window',
            'views': [(self.env.ref('stock.view_inventory_form').id, 'form')],
            'view_mode': 'form',
            'res_id':self.id,
            'name': _(self.name or 'Inventory'),
            'res_model': 'stock.inventory',
            'target':'current',
        }
        action['context'] = action_tree.get('context',{})
        action['domain'] = action_tree.get('domain',[])
        return action          
    
          
    def _add_product(self, barcode):
        
        
        is_last_scanned = False
        sequence = 0
        warm_sound_code = ""
        
        if self.env.user.company_id.sudo().sh_inven_adjt_barcode_scanner_last_scanned_color:  
            is_last_scanned = True          
        
        if self.env.user.company_id.sudo().sh_inven_adjt_barcode_scanner_move_to_top:
            sequence = -1
            
        if self.env.user.company_id.sudo().sh_inven_adjt_barcode_scanner_warn_sound:
            warm_sound_code = "SH_BARCODE_SCANNER_"     
                    
        if self.env.user.company_id.sudo().sh_inven_adjt_barcode_scanner_auto_close_popup:
            warm_sound_code += "AUTO_CLOSE_AFTER_" + str(self.env.user.company_id.sudo().sh_inven_adjt_barcode_scanner_auto_close_popup) + "_MS&"   

        
        
        #step 1: state validation.
        if self and self.state != 'confirm':
            selections = self.fields_get()['state']['selection']
            value = next((v[1] for v in selections if v[0] == self.state), self.state)
            raise UserError(_("You can not scan item in %s state.") %(value))
        
        elif self:
                
            self.line_ids.update({
                'sh_inven_adjt_barcode_scanner_is_last_scanned': False,
                'sequence': 0,
                })             
            
            
            search_lines = False
            is_multi_barcode = self.env.user.has_group('sh_barcode_scanner_adv.group_sh_barcode_scanner_multi_barcode')
                        
            if self.env.user.company_id.sudo().sh_inven_adjt_barcode_scanner_type == 'barcode':
                if is_multi_barcode:        
                    search_lines = self.line_ids.filtered(lambda l: l.product_id.barcode == barcode)
                    if not search_lines:
                        for line in self.line_ids:
                            if line.product_id and line.product_id.barcode_line_ids:
                                for barcode_line in line.product_id.barcode_line_ids:
                                    if barcode_line.name == barcode:
                                        search_lines = line
                                        break
                else:
                    search_lines = self.line_ids.filtered(lambda l: l.product_id.barcode == barcode)
            
            elif self.env.user.company_id.sudo().sh_inven_adjt_barcode_scanner_type == 'int_ref':
                search_lines = self.line_ids.filtered(lambda l: l.product_id.default_code == barcode)
            
            elif self.env.user.company_id.sudo().sh_inven_adjt_barcode_scanner_type == 'both':
                if is_multi_barcode:        
                    search_lines = self.line_ids.filtered(lambda l: l.product_id.barcode == barcode or l.product_id.default_code == barcode)
                    if not search_lines:
                        for line in self.line_ids:
                            if line.product_id and line.product_id.barcode_line_ids:
                                for barcode_line in line.product_id.barcode_line_ids:
                                    if barcode_line.name == barcode:
                                        search_lines = line
                                        break
                else:                
                    search_lines = self.line_ids.filtered(lambda l: l.product_id.barcode == barcode or l.product_id.default_code == barcode)
                   
            if search_lines:
                for line in search_lines:
                    line.product_qty += 1
                    line.sh_inven_adjt_barcode_scanner_is_last_scanned = is_last_scanned,
                    line.sequence = sequence
                    break
            else:
                raise UserError(_(warm_sound_code + "Scanned Internal Reference/Barcode not exist in any product!"))      
            
    def on_barcode_scanned(self, barcode):  
        self._add_product(barcode)    
        
        

class stock_scrap(models.Model):
    _name = "stock.scrap"
    _inherit = ['barcodes.barcode_events_mixin', 'stock.scrap']
    
    
    def on_barcode_scanned(self, barcode):            
        
        warm_sound_code = ""
#         if self.env.user.company_id.sudo().sh_scrap_barcode_scanner_warn_sound:
#             warm_sound_code = "SH_BARCODE_SCANNER_"           
#                
#         if self.env.user.company_id.sudo().sh_scrap_barcode_scanner_auto_close_popup:
#             warm_sound_code += "AUTO_CLOSE_AFTER_" + str(self.env.user.company_id.sudo().sh_scrap_barcode_scanner_auto_close_popup) + "_MS&"   
#         
        
        #step 1: state validation.
        if self and self.state != 'draft':
            selections = self.fields_get()['state']['selection']
            value = next((v[1] for v in selections if v[0] == self.state), self.state)
            warning_mess = {
                'title': _('Error!'),
                'message' : (warm_sound_code + 'You can not scan item in %s state.') %(value)
            }
            return {'warning': warning_mess}
        
        elif self.product_id:
            is_multi_barcode = self.env.user.has_group('sh_barcode_scanner_adv.group_sh_barcode_scanner_multi_barcode')
                        
            if self.env.user.company_id.sudo().sh_scrap_barcode_scanner_type == 'barcode':
                
                is_match_product = False
                if self.product_id.barcode == barcode:
                    is_match_product = True
                    
                if not is_match_product and self.product_id.barcode_line_ids and is_multi_barcode:
                    for barcode_line in self.product_id.barcode_line_ids:
                        if barcode_line.name == barcode:
                            is_match_product = True
                            break                            
                
                if is_match_product:
                    self.scrap_qty += 1
                else:
                    warning_mess = {
                        "title": _("Error!"),
                        "message" : (warm_sound_code + "You can not change product after scan started. If you want to scan new product than pls create new scrap.")
                    }
                    return {"warning": warning_mess}                    
            
            elif self.env.user.company_id.sudo().sh_scrap_barcode_scanner_type == 'int_ref':
                if self.product_id.default_code == barcode:
                    self.scrap_qty += 1
                else:
                    warning_mess = {
                        "title": _("Error!"),
                        "message" : (warm_sound_code + "You can not change product after scan started. If you want to scan new product than pls create new scrap.")
                    }
                    return {"warning": warning_mess}                      
            
            elif self.env.user.company_id.sudo().sh_scrap_barcode_scanner_type == 'both':
                
                is_match_product = False
                if self.product_id.barcode == barcode or self.product_id.default_code == barcode:
                    is_match_product = True
                    
                if not is_match_product and self.product_id.barcode_line_ids and is_multi_barcode:
                    for barcode_line in self.product_id.barcode_line_ids:
                        if barcode_line.name == barcode:
                            is_match_product = True
                            break                            
                
                if is_match_product:
                    self.scrap_qty += 1
                else:
                    warning_mess = {
                        "title": _("Error!"),
                        "message" : (warm_sound_code + "You can not change product after scan started. If you want to scan new product than pls create new scrap.")
                    }
                    return {"warning": warning_mess}  
        else:
            domain = []
            is_multi_barcode = self.env.user.has_group('sh_barcode_scanner_adv.group_sh_barcode_scanner_multi_barcode')
                        
            if self.env.user.company_id.sudo().sh_scrap_barcode_scanner_type == 'barcode':
                if is_multi_barcode:
                    domain = ['|',
                              ("barcode","=",barcode),
                              ("barcode_line_ids.name","=",barcode)
                              ]                     
                else:
                    domain = [("barcode","=",barcode)]
            
            elif self.env.user.company_id.sudo().sh_scrap_barcode_scanner_type == 'int_ref':
                domain = [("default_code","=",barcode)]
            
            elif self.env.user.company_id.sudo().sh_scrap_barcode_scanner_type == 'both':
                if is_multi_barcode:
                    domain = ["|","|",
                        ("default_code","=",barcode),
                        ("barcode","=",barcode),
                        ("barcode_line_ids.name","=",barcode)                   
                    ]                  
                else:
                    domain = ["|",
                        ("default_code","=",barcode),
                        ("barcode","=",barcode)
                    ]
                
            
            search_product = self.env["product.product"].search(domain, limit = 1)
            
            if search_product:                    
                self.product_id = search_product.id
                

            else:
                warning_mess = {
                    "title": _("Error!"),
                    "message" : (warm_sound_code + "Scanned Internal Reference/Barcode not exist in any product!")
                }
                return {"warning": warning_mess} 





class stock_move(models.Model):
    _name = "stock.move"
    _inherit = ['barcodes.barcode_events_mixin', 'stock.move']

    sequence = fields.Integer(string='Sequence', default=0)
    sh_inventory_barcode_scanner_is_last_scanned = fields.Boolean(string = "Last Scanned?")
        
            
    def on_barcode_scanned(self, barcode):
        
        is_last_scanned = False
        sequence = 0
        warm_sound_code = ""
        
        if self.env.user.company_id.sudo().sh_inventory_barcode_scanner_last_scanned_color:  
            is_last_scanned = True          
        
        if self.env.user.company_id.sudo().sh_inventory_barcode_scanner_move_to_top:
            sequence = -1
            
        if self.env.user.company_id.sudo().sh_inventory_barcode_scanner_warn_sound:
            warm_sound_code = "SH_BARCODE_SCANNER_"       
            
        if self.env.user.company_id.sudo().sh_inventory_barcode_scanner_auto_close_popup:
            warm_sound_code += "AUTO_CLOSE_AFTER_" + str(self.env.user.company_id.sudo().sh_inventory_barcode_scanner_auto_close_popup) + "_MS&"   



            
            
                 
        
        if self.picking_id.state not in ['confirmed','assigned']:
            selections = self.picking_id.fields_get()['state']['selection']
            value = next((v[1] for v in selections if v[0] == self.picking_id.state), self.picking_id.state)
            raise UserError(_(warm_sound_code + "You can not scan item in %s state.") %(value))
                  
        elif self.move_line_ids:
            is_multi_barcode = self.env.user.has_group('sh_barcode_scanner_adv.group_sh_barcode_scanner_multi_barcode')            
            for line in self.move_line_ids:
                if self.env.user.company_id.sudo().sh_inventory_barcode_scanner_type == 'barcode':
                    
                    is_match_product = False
                    if self.product_id.barcode == barcode:
                        is_match_product = True
                        
                    if not is_match_product and self.product_id.barcode_line_ids and is_multi_barcode:
                        for barcode_line in self.product_id.barcode_line_ids:
                            if barcode_line.name == barcode:
                                is_match_product = True
                                break                            
                    
                    if is_match_product:
                        line.qty_done += 1
                        
                        self.sequence = sequence
                        self.sh_inventory_barcode_scanner_is_last_scanned = is_last_scanned
                        
                        if self.quantity_done == self.product_uom_qty + 1:                      
                            warning_mess = {
                                    'title': _('Alert!'),
                                    'message' : warm_sound_code + 'Becareful! Quantity exceed than initial demand!'
                                }
                            return {'warning': warning_mess}                                  
                        break    
                    else:
                        raise UserError(_(warm_sound_code + "Scanned Internal Reference/Barcode not exist in any product!"))                            
                    
                elif self.env.user.company_id.sudo().sh_inventory_barcode_scanner_type == 'int_ref':
                    if self.product_id.default_code == barcode:
                        line.qty_done += 1
                        
                        self.sequence = sequence
                        self.sh_inventory_barcode_scanner_is_last_scanned = is_last_scanned
                                                
                        
                        if self.quantity_done == self.product_uom_qty + 1:                      
                            warning_mess = {
                                    'title': _('Alert!'),
                                    'message' : warm_sound_code + 'Becareful! Quantity exceed than initial demand!'
                                }
                            return {'warning': warning_mess}                                   
                        break
                    else:
                        raise UserError(_(warm_sound_code + "Scanned Internal Reference/Barcode not exist in any product!"))                             
                                        
                    
                elif self.env.user.company_id.sudo().sh_inventory_barcode_scanner_type == 'both':
                    
                    is_match_product = False
                    if self.product_id.barcode == barcode or self.product_id.default_code == barcode:
                        is_match_product = True
                        
                    if not is_match_product and self.product_id.barcode_line_ids and is_multi_barcode:
                        for barcode_line in self.product_id.barcode_line_ids:
                            if barcode_line.name == barcode:
                                is_match_product = True
                                break 
                                                
                    if is_match_product:
                        line.qty_done += 1
                        
                        self.sequence = sequence
                        self.sh_inventory_barcode_scanner_is_last_scanned = is_last_scanned
                                                
                        if self.quantity_done == self.product_uom_qty + 1:                    
                            warning_mess = {
                                    'title': _('Alert!'),
                                    'message' :warm_sound_code + 'Becareful! Quantity exceed than initial demand!'
                                }
                            return {'warning': warning_mess}                                  
                        break
                    else:
                        raise UserError(_(warm_sound_code + "Scanned Internal Reference/Barcode not exist in any product!"))                              
                
        else:
            raise UserError(_(warm_sound_code + "Pls add all product items in line than rescan."))
        
        

    
            
class stock_picking(models.Model):
    _name = "stock.picking"
    _inherit = ['barcodes.barcode_events_mixin', 'stock.picking']   
    
      
            
    def on_barcode_scanned(self, barcode):
        
        is_last_scanned = False
        sequence = 0
        warm_sound_code = ""
        
        if self.env.user.company_id.sudo().sh_inventory_barcode_scanner_last_scanned_color:  
            is_last_scanned = True          
        
        if self.env.user.company_id.sudo().sh_inventory_barcode_scanner_move_to_top:
            sequence = -1
            
        if self.env.user.company_id.sudo().sh_inventory_barcode_scanner_warn_sound:
            warm_sound_code = "SH_BARCODE_SCANNER_"
            
        if self.env.user.company_id.sudo().sh_inventory_barcode_scanner_auto_close_popup:
            warm_sound_code += "AUTO_CLOSE_AFTER_" + str(self.env.user.company_id.sudo().sh_inventory_barcode_scanner_auto_close_popup) + "_MS&"   

            
                    
        
        if self and self.state not in ['assigned','draft','confirmed']:
            selections = self.fields_get()['state']['selection']
            value = next((v[1] for v in selections if v[0] == self.state), self.state)
            raise UserError(_(warm_sound_code + "You can not scan item in %s state.") %(value))                
            
        
        elif self:
            
            
            self.move_ids_without_package.update({
                'sh_inventory_barcode_scanner_is_last_scanned': False,
                'sequence': 0,
                }) 
                        
            
            search_mls = False
            domain = []
            
            is_multi_barcode = self.env.user.has_group('sh_barcode_scanner_adv.group_sh_barcode_scanner_multi_barcode')
                        
            if self.env.user.company_id.sudo().sh_inventory_barcode_scanner_type == 'barcode':
                if is_multi_barcode:        
                    search_mls = self.move_ids_without_package.filtered(lambda ml: ml.product_id.barcode == barcode)
                    if not search_mls:
                        for line in self.move_ids_without_package:
                            if line.product_id and line.product_id.barcode_line_ids:
                                for barcode_line in line.product_id.barcode_line_ids:
                                    if barcode_line.name == barcode:
                                        search_mls = line
                                        break
                        
                        
                        
                    domain = ['|',
                              ("barcode","=",barcode),
                              ("barcode_line_ids.name","=",barcode)
                              ]                 
                
                else:
                    search_mls = self.move_ids_without_package.filtered(lambda ml: ml.product_id.barcode == barcode)
                    domain = [("barcode","=",barcode)]
            
            elif self.env.user.company_id.sudo().sh_inventory_barcode_scanner_type == 'int_ref':
                search_mls = self.move_ids_without_package.filtered(lambda ml: ml.product_id.default_code == barcode)
                domain = [("default_code","=",barcode)]                
                
            elif self.env.user.company_id.sudo().sh_inventory_barcode_scanner_type == 'both':
                if is_multi_barcode:        
                    search_mls = self.move_ids_without_package.filtered(lambda ml: ml.product_id.barcode == barcode or ml.product_id.default_code == barcode)
                    if not search_mls:
                        for line in self.move_ids_without_package:
                            if line.product_id and line.product_id.barcode_line_ids:
                                for barcode_line in line.product_id.barcode_line_ids:
                                    if barcode_line.name == barcode:
                                        search_mls = line
                                        break
                        
                    domain = ["|","|",
                        ("default_code","=",barcode),
                        ("barcode","=",barcode),
                        ("barcode_line_ids.name","=",barcode)                   
                    ]              
                else:
                    search_mls = self.move_ids_without_package.filtered(lambda ml: ml.product_id.barcode == barcode or ml.product_id.default_code == barcode)
                    domain = ["|",
                        ("default_code","=",barcode),
                        ("barcode","=",barcode)
                    ]  
                                                
                                            
            if search_mls:
                for move_line in search_mls:
                    
                    if move_line.show_details_visible:
                        raise UserError(_(warm_sound_code + "You can not scan product item for lot/serial directly here, Pls click detail button (at end each line) and than rescan your product item."))                                       
                                      
                    if self.state == 'draft':
                        move_line.product_uom_qty += 1
                        move_line.sh_inventory_barcode_scanner_is_last_scanned = is_last_scanned
                        move_line.sequence = sequence                              
                        
                    else:
                        move_line.quantity_done = move_line.quantity_done + 1
                        move_line.sh_inventory_barcode_scanner_is_last_scanned = is_last_scanned
                        move_line.sequence = sequence                        
    #                     move_line.update({'quantity_done':move_line.quantity_done + 1})
                                                                    
                        if move_line.quantity_done == move_line.product_uom_qty + 1:                    
                            warning_mess = {
                                    'title': _('Alert!'),
                                    'message' :warm_sound_code + 'Becareful! Quantity exceed than initial demand!'
                                }
                            return {'warning': warning_mess} 
                    
                    break
                                    
            elif self.state == 'draft':
                if self.env.user.company_id.sudo().sh_inventory_barcode_scanner_is_add_product:
                    if not self.picking_type_id:
                        raise UserError(_(warm_sound_code + "You must first select a Operation Type."))                        
                        
                    search_product = self.env["product.product"].search(domain, limit = 1)
                    if search_product:                                         
                         
                        order_line_val = {
                           "name": search_product.name,
                           "product_id": search_product.id,
                            "product_uom_qty": 1,
                           "price_unit": search_product.lst_price,
#                            "quantity_done" : 1,
                           "location_id" : self.location_id.id,
                           "location_dest_id": self.location_dest_id.id,
                           'date_expected' : str(fields.date.today()),
                           'sh_inventory_barcode_scanner_is_last_scanned':is_last_scanned,
                           'sequence':sequence,
                           
                        }      
                        if search_product.uom_id:
                            order_line_val.update({
                                "product_uom": search_product.uom_id.id,                            
                            })    
                            
                        old_lines = self.move_ids_without_package
                        new_order_line = self.move_ids_without_package.create(order_line_val)
                        self.move_ids_without_package = old_lines + new_order_line
                        new_order_line.onchange_product_id()                          
                                            
                    else: 
                        raise UserError(_(warm_sound_code + "Scanned Internal Reference/Barcode not exist in any product!"))                                          
                                           
                else:
                    raise UserError(_(warm_sound_code + "Scanned Internal Reference/Barcode not exist in any product!"))     
            else:
                raise UserError(_(warm_sound_code + "Scanned Internal Reference/Barcode not exist in any product!"))                     
                