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
{
    # Application Information
    'name' : 'Hide Advanced Search Button',
    'category' : 'Web',
    'version' : '13.0.1',
    'license': 'OPL-1',
    'summary': 'This module hide the Advance Search Options like "Filters", "Group By" and "Favorites" For the Particular Group of Users',
    'description': """
        - This module hide the Advance Search Options like "Filters", "Group By" and "Favorites" For the Particular Group of Users
    """,
    
    # Author Information
    'author': 'MadeUp Infotech',
    'maintainer': 'MadeUp Infotech',   
    'website': 'https://www.madeupinfotech.com/',
    
    # Application Price Information
    'price': 30,
    'currency': 'EUR',

    # Dependencies
    'depends': ['web'],
    'sequence': 1,

    # Views
    'data': [
        'security/groups.xml',
        'templates/assets.xml',
    ],

    # Qweb
    'qweb': [
        "static/src/xml/base.xml",
    ],
    # Application Main Image    
    'images': ['static/description/hide_advanced_search_button_mu_cover_img.png'],

    # Technical
    'installable': True,
    'application' : True,
    'auto_install': False,
    'active': False,
}
