#-*- coding-utf-8 -*-
{
    'name': "Base de gestion des modèles de notification",
    'summary': """
    Modèle de gestion des notification.
       """,
    'author': 'Jean Jonathan ARRA (VEONE)',
    'company': 'VEONE',
    'website': 'http://www.veone.net',
    'category': 'Tools',
    'version': '0.1',
    'license': 'AGPL-3',
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/notify_managment_view.xml',
    ],
}
