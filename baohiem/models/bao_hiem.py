from odoo import fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
# định nghĩa datetime để lấy ngày hiện tại làm mặc định
from datetime import datetime

class BaoHiem(models.Model):
    _name = "bao.hiem"
    _description = "Bảo Hiểm model"
    
    #Dùng Many2one để lấy tên nhân viên đã có sẳn
    name = fields.Many2one('hr.employee', string="Người lao động", required=True,
                              states={
                                'dangchay': [('readonly', True)],
                                'giamtamthoi': [('readonly', True)],
                                'ketthuc': [('readonly', True)]
                            })

    lstd_baohiem = fields.One2many('lich.su', 'bh_kn_lstd', string="Lịch Sử Thay Đổi") #Lịch Sử Thay Đổi: Tên của form view khi show dạng popup
    
    dchl_kn_bh = fields.Many2one('dchang.loat')
    
    #Tạo status bar
    state = fields.Selection([
            ('batdau', 'Mới'),
            ('dangchay', 'Đang Chạy'),
            ('giamtamthoi', 'Giảm Tạm Thời'),
            ('ketthuc', 'Kết Thúc'),
            ],default='batdau')
    
    trangthai_bh = fields.Selection([
            ('moi_bh', 'Mới'), #đặt trùng tên biến: 'moi' bên model dieu_chinh.py --> gây lỗi khi dùng CSS để thêm color ở state:'MỚI'
        
            ('dangchay', 'Đang chạy'),
            ('giamtamthoi', 'Giảm Tạm Thời'),
            ('ketthuc', 'Kết Thúc'),
            ],default='moi_bh', string="Trạng thái") #để ẩn tên label: 'Trạng thái' --> string= " "
    
    thamchieu_bh = fields.Char('Số sổ Bảo Hiểm', required=True,
                           states={
                                'dangchay': [('readonly', True)],
                                'giamtamthoi': [('readonly', True)],
                                'ketthuc': [('readonly', True)]
                            })
    #thêm default=datetime.today() để lấy ngày hiện tại làm mặc định
    thoigian_bh = fields.Date('Khoảng thời gian', default=datetime.today(), required=True,
                          states={
                                'dangchay': [('readonly', True)],
                                'giamtamthoi': [('readonly', True)],
                                'ketthuc': [('readonly', True)]
                            })
    
    #thêm field currency_id = fields.Many2one... và widget="monetary" (có sẳn)
    #để khai báo bên file bao_hiem_views.xml khi muốn show biểu tượng tiền tệ
    #ở phía sau field tương ứng (Mức đóng BHXH) (Mức đóng BHTN)
    currency_id = fields.Many2one("res.currency", 
                                  string="Loại tiền tệ", default=lambda self:self.env.user.company_id.currency_id.id,required=True)
    
    #Dùng readonly=True, để tạo field nhưng không cho điền vào field
    bhxh_bh = fields.Monetary('Mức đóng BHXH', readonly=True,
                          states={
                                'dangchay': [('readonly', True)],
                                'giamtamthoi': [('readonly', True)],
                                'ketthuc': [('readonly', True)]
                            })
    bhtn_bh = fields.Monetary('Mức đóng BHTN', readonly=True,
                           states={
                                'dangchay': [('readonly', True)],
                                'giamtamthoi': [('readonly', True)],
                                'ketthuc': [('readonly', True)]
                            })
#    bhyt = fields.Monetary('Mức đóng BHYT', readonly=True)

    bhxh_nld_bh = fields.Float('(%) mức đóng của NLĐ', readonly=True)
    bhxh_cty_bh = fields.Float('(%) mức đóng của Cty', readonly=True)
    
    bhtn_nld_bh = fields.Float('(%) mức đóng của NLD', readonly=True)
    bhtn_cty_bh = fields.Float('(%) mức đóng của Cty', readonly=True)
    
    bhyt_nld_bh = fields.Float('(%) mức đóng của NLĐ', readonly=True)
    bhyt_cty_bh = fields.Float('(%) mức đóng của Cty', readonly=True)
    
    ngayhethan_bh = fields.Date('Ngày hết hạn')
    dkkhambenh_bh = fields.Text('Nơi đăng ký khám chữa bệnh')
#    nguoilaodong_image = fields.Binary("Nguoilaodong Image", attachment=True, help="Nguoilaodong Image")


    #Theo quy trình, 1 user chỉ có thể đăng ký 1 Sổ BHXH duy nhất.
    #code này sẽ thông báo khi user chọn trùng tên trong hr.employee.
    #Chú ý: code này chỉ apply được khi bắt đầu sử dụng với model RỖNG
    #_sql_constraints = [
    #        ('name', 'unique (name)', 'Người lao động này đã được đăng ký !'),
    #    ]
    
    #Số Sổ Bảo Hiểm là duy nhất.
    _sql_constraints = [
            ('thamchieu_bh', 'unique (thamchieu_bh)', 'Số sổ Bảo Hiểm này đã được đăng ký !'),
        ]
    
    
    def open_form_dieuchinh(self):

        return {
           'view_mode': 'form',
        #mở form view của model dieu_chinh.py nên chọn model là: 'res_model': 'dieu.chinh'
           'res_model': 'dieu.chinh',
        #self.env.ref('baohiem.giam_tam_...'): baohiem: tên module
           'view_id': self.env.ref('baohiem.tld_dc_form_view').id,
        #Dùng context để pass value từ field của form view model bao_hiem.py sang field của form view model dieu_chinh.py
        #Many2one (để lấy value của hr.employee) là dạng (integer) ---> là dạng id
        #Nên phải thêm id sau self.name ---> self.name.id. (Nếu chỉ 'default_name': self.name --> lỗi)
           'context': {'default_name': self.name.id},
           'target': 'current',
           'type': 'ir.actions.act_window',
           }

    def ve_tang_lao_dong_bh(self):
        for rec in self:
            if rec.state:
                rec.state = "batdau"
                rec.trangthai_bh = "moi_bh"
        return True
    
    def ve_xac_nhan_dc(self):
        return {
            'view_mode': 'form',
            'res_model': 'dieu.chinh',
            'context': {'default_name': self.name.id},
            'target': 'current',
            'type': 'ir.actions.act_window',
            }

    def open_popup_form_dc_gtt(self):
        return {
            'name': "Giảm Tạm Thời :",
            'view_mode': 'form',
            'res_model': 'dieu.chinh',
            #self.env.ref('baohiem.giam_tam_...'): baohiem: tên module
            'view_id': self.env.ref('baohiem.giam_tam_thoi_form_view').id,
            'context': {'default_name': self.name.id,
            # đưa giá trị rỗng (' ') vào field thamchieu qua context để show trong field name ('Tham Chiếu')
            # bên tree view của model lich_su.py, thay thế cho giá trị 'False' (set mặc định)
            # khi user không điền giá trị vào field 'thamchieu' (do không bắt buộc)
                        'default_thamchieu': ' '
                       },
            'target': 'new',
            'type': 'ir.actions.act_window',
            }
    
    def open_popup_form_dc_kt(self):
        return {
            'name': 'Kết Thúc',
            'view_mode': 'form',
            'res_model': 'dieu.chinh',
            #self.env.ref('baohiem.giam_tam_...'): baohiem: tên module
            'view_id': self.env.ref('baohiem.ket_thuc_form_view').id,
            'context': {'default_name': self.name.id,
                        'default_thamchieu': ' '
                       },
            'target': 'new',
            'type': 'ir.actions.act_window',
            }

    #function ẩn các field trong custom filter
    def fields_get(self, fields=None):
        fields_to_hide = ['dchl_kn_bh', 'bhxh_nld_bh',
                         'bhxh_cty_bh', 'bhtn_nld_bh',
                         'bhtn_cty_bh', 'bhyt_nld_bh',
                         'bhyt_cty_bh', 'lstd_baohiem',
                         'currency_id', 'state',
                         'ngayhethan_bh', 'dkkhambenh_bh',
                         'name','thamchieu_bh',
                         'trangthai_bh']
        res = super(BaoHiem, self).fields_get()
        for field in fields_to_hide:
            res[field]['selectable'] = False
        return res
    
