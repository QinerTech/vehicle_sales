# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import time
from openerp.report import report_sxw
from openerp.osv import osv


class report_common(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(report_common, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'rmb_upper': self._rmb_upper,
        })

    def _rmb_upper(self, value):
        """
        人民币大写
        来自：http://topic.csdn.net/u/20091129/20/b778a93d-9f8f-4829-9297-d05b08a23f80.html
        传入浮点类型的值返回 unicode 字符串
        """
        rmbmap = [u"零", u"壹", u"贰", u"叁", u"肆", u"伍", u"陆", u"柒", u"捌", u"玖"]
        unit = [u"分", u"角", u"元", u"拾", u"佰", u"仟", u"万", u"拾", u"佰", u"仟", u"亿",
                u"拾", u"佰", u"仟", u"万", u"拾", u"佰", u"仟", u"兆"]

        nums = map(int, list(str('%0.2f' % value).replace('.', '')))
        words = []
        zflag = 0  # 标记连续0次数，以删除万字，或适时插入零字
        start = len(nums) - 3
        for i in range(start, -3, -1):  # 使i对应实际位数，负数为角分
            if 0 != nums[start - i] or len(words) == 0:
                if zflag:
                    words.append(rmbmap[0])
                    zflag = 0
                words.append(rmbmap[nums[start - i]])
                words.append(unit[i + 2])
            elif 0 == i or (0 == i % 4 and zflag < 3):  # 控制‘万/元’
                words.append(unit[i + 2])
                zflag = 0
            else:
                zflag += 1

        if words[-1] != unit[0]:  # 结尾非‘分’补整字
            words.append(u"整")
        return ''.join(words)


class report_vehicle_contract(osv.AbstractModel):
    _name = 'report.vehicle_sales_contract_print.report_contract'
    _inherit = 'report.abstract_report'
    _template = 'vehicle_sales_contract_print.report_contract'
    _wrapped_report_class = report_common
