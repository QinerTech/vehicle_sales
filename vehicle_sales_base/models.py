# -*- coding: utf-8 -*-

from openerp.osv import osv
from openerp import SUPERUSER_ID
from lxml import etree
from lxml.builder import E
from openerp.tools.translate import _
from openerp.addons.base.res.res_users import name_boolean_group, name_selection_groups


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
