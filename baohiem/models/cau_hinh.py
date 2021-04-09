#19/2/21: model cau_hinh.py copy từ model lich_su.py

from odoo import fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
# định nghĩa datetime để lấy ngày hiện tại làm mặc định
from datetime import datetime

class CauHinh(models.Model):
    _name = "cau.hinh"
    _description = "Cấu hình Bảo Hiểm model"
    
    #Tạo status bar
    state = fields.Selection([
            ('moi', 'MỚI'),
            ('xacnhan', 'ĐÃ XÁC NHẬN'),
            ('hethan', 'HẾT HẠN'),
            ],default='moi', string="Trạng thái") 

    
    currency_id = fields.Many2one("res.currency", 
                                  string="Loại tiền tệ", default=lambda self:self.env.user.company_id.currency_id.id,required=True)
    
    ten = fields.Char('Tên')
    
    tu_ngay = fields.Date('Từ ngày', default=datetime.today(), required=True)
    
    den_ngay = fields.Date('Đến ngày', default=datetime.today(), required=True)
    
    md_bhxh = fields.Monetary('Mức đóng BHXH')
    
    md_bhtn = fields.Monetary('Mức đóng BHTN')
