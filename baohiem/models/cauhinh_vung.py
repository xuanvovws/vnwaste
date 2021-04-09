#20/2/21: model cauhinh.py copy từ model lich_su.py

from odoo import fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
# định nghĩa datetime để lấy ngày hiện tại làm mặc định
from datetime import datetime

class CauHinhVung(models.Model):
    _name = "cauhinh.vung"
    _description = "Cấu hình mức tối thiểu đóng theo Vùng model"
    #Thể hiện giá trị của thamchieu thay cho name (mặc định) sau khi tạo. Model này ko dùng name !
    #để field 'dchl_vung' (model dchang_loat.py) kết nối được tới field 'vung'--> cần phải có _rec_name
    _rec_name = "vung"

    #Tạo status bar
    state = fields.Selection([
            ('khoitao', 'KHỞI TẠO'),
            ('xacnhan', 'XÁC NHẬN'),
            ],default='khoitao', string = "Tỉnh/Thành")
    
    vung = fields.Char('Vùng', required="true",
                      states={
                                'xacnhan': [('readonly', True)]
                            })
    
    ma_vung = fields.Char('Mã', required="true",
                      states={
                                'xacnhan': [('readonly', True)]
                            })
    
    _sql_constraints = [
            ('ma_vung', 'unique (ma_vung)', 'Mã này đã được đăng ký!'),
        ]
    
    bhxh_lcs = fields.Monetary() #bhxh_lcs: bảo hiểm xã hội - lương cơ sở
    
    bhtn_lcs = fields.Monetary() #bhtn_lcs: bảo hiểm thất nghiệp - lương cơ sở
    
    tlcs_xh = fields.Float(default=20) #tlcs: tháng lương cơ sở
    
    tlcs_tn = fields.Float()
    
    bhxhxn = fields.Monetary()
    
    bhtnxn = fields.Monetary()
    
    currency_id = fields.Many2one("res.currency", 
                                  string="Loại tiền tệ", default=lambda self:self.env.user.company_id.currency_id.id,required=True)

    
    active = fields.Boolean("Active", default=True)
    
    def xacnhan_vung(self):

        for rec in self:
            rec.bhxhxn = rec.bhxh_lcs * rec.tlcs_xh
            rec.bhtnxn = rec.bhtn_lcs * rec.tlcs_tn
            
            rec.state = "xacnhan"
                
            return True
        
    #function ẩn các field trong custom filter
    def fields_get(self, fields=None):
        fields_an_di = ['bhtn_lcs','bhxh_lcs',
                          'bhtnxn', 'vung',
                         'ma_vung', 'bhxhxn',
                         'tlcs_xh', 'tlcs_tn',
                         'currency_id', 'state']
        res = super(CauHinhVung, self).fields_get()
        for field in fields_an_di:
            res[field]['selectable'] = False
        return res