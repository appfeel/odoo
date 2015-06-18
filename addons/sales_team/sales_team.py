# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp.osv import fields, osv


class crm_team(osv.Model):
    _name = "crm.team"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Sales Team"
    _order = "complete_name"
    _period_number = 5

    def get_full_name(self, cr, uid, ids, field_name, arg, context=None):
        return dict(self.name_get(cr, uid, ids, context=context))

    def _get_default_team_id(self, cr, uid, context=None, user_id=None):
        if context is None:
            context = {}
        if user_id is None:
            user_id = uid
        team_id = context.get('default_team_id')
        if not team_id:
            team_ids = self.search(cr, uid, ['|', ('user_id', '=', user_id), ('member_ids', 'in', user_id)], limit=1, context=context)
            team_id = team_ids[0] if team_ids else False
        if not team_id:
            team_id = self.pool['ir.model.data'].xmlid_to_res_id(cr, uid, 'sales_team.team_sales_department')
        return team_id

    _columns = {
        'name': fields.char('Sales Team', size=64, required=True, translate=True),
        'complete_name': fields.function(get_full_name, type='char', size=256, readonly=True, store=True, string="Full Name"),
        'code': fields.char('Code', size=8),
        'active': fields.boolean('Active', help="If the active field is set to "\
                        "false, it will allow you to hide the sales team without removing it."),
        'company_id': fields.many2one('res.company', 'Company'),
        'user_id': fields.many2one('res.users', 'Team Leader'),
        'member_ids': fields.many2many('res.users', 'sale_member_rel', 'team_id', 'member_id', 'Team Members'),
        'reply_to': fields.char('Reply-To', size=64, help="The email address put in the 'Reply-To' of all emails sent by Odoo about cases in this sales team"),
        'parent_id': fields.many2one('crm.team', 'Parent Team'),
        'child_ids': fields.one2many('crm.team', 'parent_id', 'Child Teams'),
        'working_hours': fields.float('Working Hours', digits=(16, 2)),
        'color': fields.integer('Color Index'),
    }

    _defaults = {
        'active': 1,
    }

    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'The code of the sales team must be unique !')
    ]

    _constraints = [
        (osv.osv._check_recursion, 'Error ! You cannot create recursive Sales team.', ['parent_id'])
    ]

    def name_get(self, cr, uid, ids, context=None):
        """Overrides orm name_get method"""
        if not isinstance(ids, list):
            ids = [ids]
        res = []
        if not ids:
            return res
        reads = self.read(cr, uid, ids, ['name', 'parent_id'], context)

        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1] + ' / ' + name
            res.append((record['id'], name))
        return res


class res_partner(osv.Model):
    _inherit = 'res.partner'
    _columns = {
        'team_id': fields.many2one('crm.team', 'Sales Team', oldname='section_id'),
    }
