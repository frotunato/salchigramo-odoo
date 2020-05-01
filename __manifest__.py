# -*- coding: utf-8 -*-
{
'name': "Salchigramo",

'summary': """
    Módulo que permite asociar a elementos del inventario anuncios en Twitter, Facebook e Instagram.
""",

'description': """
    Módulo desarrollado para la asignatura SIE en el que se permite la publicación de anuncios en RRSS.
""",

'author': "SIE Terry 2020",
'website': "https://github.com/frotunato/salchigramo",

    'category': 'Marketing',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        ],
    # only loaded in demonstration mode
    'demo': [
    'demo/demo.xml',
    ],
    }
