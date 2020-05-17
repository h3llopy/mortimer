# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#################################################################################
# Author      : MadeUp Infotech (<https://www.madeupinfotech.com/>)
# Copyright(c): 2016-Present MadeUp Infotech
# All Rights Reserved.
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
#################################################################################
from odoo import models
from odoo.http import request

class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'
    
    def session_info(self):        
        res = super(IrHttp,self).session_info()
        isAdvancedSearchDisabled = request.env.user.has_group('hide_advanced_search_button_mu.group_hide_advanced_search_button')
        res and res.update({'isAdvancedSearchDisabled':isAdvancedSearchDisabled})
        return res