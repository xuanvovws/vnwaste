from odoo import fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
# định nghĩa datetime để lấy ngày hiện tại làm mặc định
from datetime import datetime

class LichSu(models.Model):
    _name = "lich.su"
    _description = "Lịch sử thay đổi model"

    #Dùng Many2one để lấy tên nhân viên đã có sẳn
    name = fields.Many2one('hr.employee', string="Người lao động")
    
    loai = fields.Selection([
            ('tanglaodong', 'Tăng Lao Động'),
            ('giamtamthoi', 'Giảm Tạm Thời'),
            ('ket_thuc', 'KẾT THÚC'),
            ], string="Loại")

    bh_kn_lstd = fields.Many2one('bao.hiem') #bh_kn_lstd : bao_hiem.py kết nối lich_su.py
    
    thamchieu_ls = fields.Char('Tham chiếu')
    #thêm default=datetime.today() để lấy ngày hiện tại làm mặc định
    thoigian_ls = fields.Date('Ngày duyệt', default=datetime.today())
    
    #thêm field currency_id = fields.Many2one... và widget="monetary" (có sẳn)
    #để khai báo bên file bao_hiem_views.xml (tree view của lịch sử thay đổi) khi muốn show biểu tượng tiền tệ
    #ở phía sau field tương ứng (M.Đ BHXH) (M.Đ BHTN)
    currency_id = fields.Many2one("res.currency", 
                                  string="Loại tiền tệ", default=lambda self:self.env.user.company_id.currency_id.id,required=True)
    

    bhxh_ls = fields.Monetary("Mức đóng BHXH")
    
    bhtn_ls = fields.Monetary('Mức đóng BHTN')
#    md_bhyt = fields.Float('Mức đóng BHYT')
    bhxh_nld = fields.Float('BHXH. NLĐ (%)')        
    bhxh_cty = fields.Float('BHXH. Cty (%)')
    
    bhtn_nld = fields.Float('BHTN. NLĐ (%)')
    bhtn_cty = fields.Float('BHTN. Cty (%)')
    
    bhyt_nld = fields.Float('BHYT. NLĐ (%)')
    bhyt_cty = fields.Float('BHYT. Cty (%)')

    #function ẩn các field trong custom filter
    def fields_get(self, fields=None):
        fields_an_di = ['bh_kn_lstd','bhxh_nld',
                          'bhxh_cty', 'bhtn_nld',
                         'bhtn_cty', 'bhyt_nld',
                         'bhyt_cty',
                         'currency_id', 'name',
                         'thamchieu_ls']
        res = super(LichSu, self).fields_get()
        for field in fields_an_di:
            res[field]['selectable'] = False
        return res
    