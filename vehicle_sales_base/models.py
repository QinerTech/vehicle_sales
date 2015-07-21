# -*- coding: utf-8 -*-
import openerp
from openerp.osv import fields, osv
from openerp import SUPERUSER_ID
from lxml import etree
from lxml.builder import E
from openerp.tools.translate import _
from openerp.addons.base.res.res_users import name_boolean_group, name_selection_groups
from openerp import tools


class CountryCity(osv.Model):
    _description = "Country City"
    _name = 'res.country.city'
    _columns = {
        'state_id': fields.many2one('res.country.state', 'State',
                                    required=True),
        'name': fields.char('City Name', required=True,
                            help='City name of a country.'),

    }
    _order = 'name'


class res_partner(osv.Model):
    _inherit = "res.partner"

    _columns = {
        'city': fields.many2one("res.country.city", 'City', ondelete='restrict'),
        'phone_home': fields.char(u'家庭电话'),
        'contact': fields.selection([
            ('mobile', u'移动电话'),
            ('phone', u'工作电话'),
            ('phone_home', u'家庭电话'),
        ], string=u'主要联系方式'),
        'contact_favorite': fields.selection([
            ('visit', u'亲访'),
            ('letter', u'信函'),
            ('call', u'电话'),
            ('message', u'短信'),
            ('email', u'邮件'),
        ], string=u'希望联系方式'),
        'identification': fields.selection([
            ('identity_card', u'身份证'),
            ('passport', u'护照'),
            ('driving_license', u'驾照'),
            ('certificate_officer', u'军官证'),
            ('other', u'其他'),
        ], string=u'证件类型'),
        'identification_code': fields.char(u'证件号码'),
        'organization_code': fields.char(u'组织机构代码'),
        'tax_registration': fields.char(u'税务登记号'),
    }

    def onchange_city(self, cr, uid, ids, city, context=None):
        if city:
            city_obj = self.pool.get('res.country.city').browse(cr, uid, city, context=context)
            return {'value': {'state_id': city_obj.state_id.id}}
        return {}


class crm_lead(osv.Model):
    _inherit = "crm.lead"

    _columns = {
        'city': fields.many2one("res.country.city", 'City', ondelete='restrict'),
        'phone_home': fields.char(u'家庭电话'),
        'contact': fields.selection([
            ('mobile', u'移动电话'),
            ('phone', u'工作电话'),
            ('phone_home', u'家庭电话'),
        ], string=u'主要联系方式'),
        'contact_favorite': fields.selection([
            ('visit', u'亲访'),
            ('letter', u'信函'),
            ('call', u'电话'),
            ('message', u'短信'),
            ('email', u'邮件'),
        ], string=u'希望联系方式'),
    }

    def onchange_city(self, cr, uid, ids, city, context=None):
        if city:
            city_obj = self.pool.get('res.country.city').browse(cr, uid, city, context=context)
            return {'value': {'state_id': city_obj.state_id.id}}
        return {}

    def _lead_create_contact(self, cr, uid, lead, name, is_company, parent_id=False, context=None):
        partner = self.pool.get('res.partner')
        vals = {'name': name,
                'user_id': lead.user_id.id,
                'comment': lead.description,
                'section_id': lead.section_id.id or False,
                'parent_id': parent_id,
                'phone': lead.phone,
                'mobile': lead.mobile,
                'email': tools.email_split(lead.email_from) and tools.email_split(lead.email_from)[0] or False,
                'fax': lead.fax,
                'title': lead.title and lead.title.id or False,
                'function': lead.function,
                'street': lead.street,
                'street2': lead.street2,
                'zip': lead.zip,
                'city': lead.city,
                'country_id': lead.country_id and lead.country_id.id or False,
                'state_id': lead.state_id and lead.state_id.id or False,
                'is_company': is_company,
                'type': 'contact',
                # add additional field
                'phone_home': lead.phone_home and lead.phone_home or False,
                'contact': lead.contact and lead.contact or False,
                'contact_favorite': lead.contact_favorite and lead.contact_favorite or False,

                }
        partner = partner.create(cr, uid, vals, context=context)
        return partner


class res_users(osv.Model):
    _inherit = 'res.users'

    _columns = {
    }

    def action_clear_access_rights(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        user = self.browse(cr, uid, ids[0], context=context)
        admin_groups = [
            self.pool.get('ir.model.data').get_object_reference(cr, uid, 'base', 'group_user')[1],
            self.pool.get('ir.model.data').get_object_reference(cr, uid, 'base', 'group_erp_manager')[1],
            self.pool.get('ir.model.data').get_object_reference(cr, uid, 'base', 'group_system')[1]
        ]

        groups_id = []
        for g in user.groups_id:
            if uid == user.id and g.id in admin_groups:
                # don't allow to admin to clear his rights
                continue
            groups_id.append((3, g.id))
        user.write({'groups_id': groups_id})
        return True


class groups_view(osv.Model):
    _inherit = 'res.groups'

    def update_user_groups_view(self, cr, uid, context=None):
        view = self.pool['ir.model.data'].xmlid_to_object(cr, SUPERUSER_ID, 'base.user_groups_view', context=context)
        if view and view.exists() and view._name == 'ir.ui.view':
            xml1, xml2 = [], []
            xml1.append(E.separator(string=_('Application'), colspan="4"))

            xml3 = []
            xml3.append(E.separator(string=_('Vehicle Sales Roles'), colspan="4"))

            custom_group_id = None
            try:
                custom_group_id = \
                    self.pool['ir.model.data'].get_object_reference(cr, uid, 'vehicle_sales_base',
                                                                    'module_category_vehicle_sales')[1]
            except:
                pass
            for app, kind, gs in self.get_groups_by_application(cr, uid, context):
                xml = None
                custom = False
                if type == 'selection' and any([g.category_id.id == custom_group_id for g in gs]) or all(
                        [g.category_id.id == custom_group_id for g in gs]):
                    xml = xml3
                    custom = True

                # hide groups in category 'Hidden' (except to group_no_one)
                attrs = {
                    'groups': 'base.group_no_one'} if app and app.xml_id == 'base.module_category_hidden' and not custom else {}

                if kind == 'selection':
                    xml = xml or xml1
                    # application name with a selection field
                    field_name = name_selection_groups(map(int, gs))
                    xml.append(E.field(name=field_name, **attrs))
                    xml.append(E.newline())
                else:
                    xml = xml or xml2
                    # application separator with boolean fields
                    app_name = app and app.name or _('Other')
                    if not custom:
                        xml.append(E.separator(string=app_name, colspan="4", **attrs))
                    for g in gs:
                        field_name = name_boolean_group(g.id)
                        xml.append(E.field(name=field_name, **attrs))

            xml = E.field(*(xml3 + xml1 + xml2), name="groups_id", position="replace")
            xml.addprevious(etree.Comment("GENERATED AUTOMATICALLY BY GROUPS"))
            xml_content = etree.tostring(xml, pretty_print=True, xml_declaration=True, encoding="utf-8")
            view.write({'arch': xml_content})
        return True


class stock_production_lot(osv.osv):
    _inherit = 'stock.production.lot'

    _columns = {
        'vehicle_vin_sn': fields.char(u'车架号'),
        'vehicle_engine_sn': fields.char(u'发动机号'),
    }

    _defaults = {

    }


class stock_quant(osv.osv):
    _inherit = 'stock.quant'

    def _get_quants(self, cr, uid, ids, context=None):
        return self.pool.get('stock.quant').search(cr, uid, [('lot_id', 'in', ids)], context=context)

    _columns = {
        'vehicle_vin_sn': fields.related('lot_id', 'vehicle_vin_sn', type='char', string=u'车架号',
                                         store={
                                             'stock.quant': (lambda self, cr, uid, ids, ctx: ids, ['lot_id'], 20),
                                             'stock.production.lot': (_get_quants, ['vehicle_vin_sn'], 20),
                                         }),
        'vehicle_engine_sn': fields.related('lot_id', 'vehicle_engine_sn', type='char', string=u'发动机号',
                                            store={
                                                'stock.quant': (lambda self, cr, uid, ids, ctx: ids, ['lot_id'], 20),
                                                'stock.production.lot': (_get_quants, ['vehicle_engine_sn'], 20),
                                            }),
    }
