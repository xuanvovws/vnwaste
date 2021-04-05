#20/2/21: model ketnoi_lichsu.py copy từ model lich_su.py .
#Model này được tạo ra với TREE (LIST) View giống model lich_su.py, để model dieu_chinh.py (hoặc bao_hiem.py) kết nối bằng one2many & many2one

from odoo import fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
# định nghĩa datetime để lấy ngày hiện tại làm mặc định
from datetime import datetime

class KetNoiLichSu(models.Model):
    _name = "ketnoi.lichsu"
    _description = "Kết nối lịch sử model"

    #Dùng Many2one để lấy tên nhân viên đã có sẳn
    name = fields.Many2one('hr.employee', string="Người lao động")
    
    loai = fields.Selection([
            ('tanglaodong', 'TĂNG LAO ĐỘNG'),
            ('giamtamthoi', 'GIẢM TẠM THỜI'),
            ('ket_thuc', 'KẾT THÚC'),
            ], string="Loại")

    dc_kn_ls = fields.Many2one('dieu.chinh') #dc_kn_ls : điều chỉnh _ kết nối _ lịch sử
    
    knls_thamchieu = fields.Char('Tham chiếu')
    #thêm default=datetime.today() để lấy ngày hiện tại làm mặc định
    knls_thoigian = fields.Date('Ngày duyệt', default=datetime.today(), required=True)
    
    #thêm field currency_id = fields.Many2one... và widget="monetary" (có sẳn)
    #để khai báo bên file bao_hiem_views.xml (tree view của lịch sử thay đổi) khi muốn show biểu tượng tiền tệ
    #ở phía sau field tương ứng (M.Đ BHXH) (M.Đ BHTN)
    currency_id = fields.Many2one("res.currency", 
                                  string="Loại tiền tệ", default=lambda self:self.env.user.company_id.currency_id.id,required=True)
    
    
    #Dùng digits=(x,y) với x= tổng số có nghĩa, y= số dư phía sau
    knls_bhxh = fields.Float("Mức đóng BHXH", digits=(12,0))
    
    knls_bhtn = fields.Float('Mức đóng BHTN', digits=(12,0))
#    md_bhyt = fields.Float('Mức đóng BHYT')

    bhxh_md_nld = fields.Float('BHXH. NLĐ (%)') #bhxh_md_nld : bảo hiểm xã hội _ mức đóng _ người lao động       
    bhxh_md_cty = fields.Float('BHXH. Cty (%)')
    
    bhtn_md_nld = fields.Float('BHTN. NLĐ (%)') #bhtn_md_nld : bảo hiểm thất nghiệp _ mức đóng _ người lao động
    bhtn_md_cty = fields.Float('BHTN. Cty (%)')
    
    bhyt_md_nld = fields.Float('BHYT. NLĐ (%)') #bhyt_md_nld : bảo hiểm y tế _ mức đóng _ người lao động
    bhyt_md_cty = fields.Float('BHYT. Cty (%)')
