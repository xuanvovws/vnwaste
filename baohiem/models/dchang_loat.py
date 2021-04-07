#18/2/21: model dchang_loat.py được copy từ model dieu_chinh.py

from odoo import api, fields, models, api, tools, _
from odoo.exceptions import UserError, ValidationError, Warning
#import python library for current datetiem()
from datetime import datetime

class DieuChinhHangLoat(models.Model):
    _name = "dchang.loat"
    _description = "Điều chỉnh hàng loạt model"
    #Thể hiện giá trị của thamchieu thay cho name (mặc định) sau khi tạo
    _rec_name = "dchl_thamchieu"

    
    dchl_sobaohiem = fields.One2many('bao.hiem', 'dchl_kn_bh', string="Sổ Bảo Hiểm")
    
    #22/2/21 --> dchl_vung: điều chỉnh hàng loạt_vùng --> kết nối tới field 'vung' (model cauhinh_vung.py) để lấy value
    dchl_vung = fields.Many2one('cauhinh.vung', string = "Vùng",
                                states={
                                'daduocxacnhan': [('readonly', True)], #data field name = readonly khi state = daduocxacdinh
                                'daduyet': [('readonly', True)], #data field name = readonly khi state = daduyet (ĐÃ DUYỆt)
                                'bihuy': [('readonly', True)] #data field name = readonly khi state = bihuy (BỊ HỦY)
                                        }
                                  )
    
    state = fields.Selection([
            ('moi', 'THÔNG TIN'),
            ('daduocxacnhan', 'ĐÃ ĐƯỢC XÁC NHẬN'),
            ('daduyet', 'ĐÃ DUYỆT'),
            ('bihuy', 'BỊ HỦY'),
            ],default='moi')
    
    dchl_thamchieu = fields.Char('Tham chiếu', 

                            states={
                                'daduocxacnhan': [('readonly', True)],
                                'daduyet': [('readonly', True)],
                                'bihuy': [('readonly', True)]
                            })
    
    #default=datetime.today() --> tự động chọn ngày hiện tại thông qua import python library phía trên
    dchl_thoigian = fields.Date('Ngày duyệt', default=datetime.today(),
                           
                           states={
                                   'daduocxacnhan':[('readonly', True)],
                                   'daduyet': [('readonly', True)],
                                   'bihuy': [('readonly', True)]
                                  })
    
    
    currency_id = fields.Many2one("res.currency", 
                                  string="Loại tiền tệ", default=lambda self:self.env.user.company_id.currency_id.id,required=True)
    dchl_bhxh = fields.Monetary('Mức đóng BHXH',
                           states={
                                   'daduocxacnhan':[('readonly', True)],
                                   'daduyet': [('readonly', True)],
                                   'bihuy': [('readonly', True)]
                                  })
    dchl_bhtn = fields.Monetary('Mức đóng BHTN',
                           states={
                                   'daduocxacnhan':[('readonly', True)],
                                   'daduyet': [('readonly', True)],
                                   'bihuy': [('readonly', True)],
                                  })

    dchl_bhxh_md_nld = fields.Float('(%) mức đóng của NLĐ', default = 8.00, readonly=True)
    dchl_bhxh_md_cty = fields.Float('(%) mức đóng của Cty', default = 17.50, readonly=True)
    dchl_bhtn_md_nld = fields.Float('(%) mức đóng của NLD', default = 1.00, readonly=True)
    dchl_bhtn_md_cty = fields.Float('(%) mức đóng của Cty', default = 1.00, readonly=True)
    dchl_bhyt_md_nld = fields.Float('(%) mức đóng của NLĐ', default= 1.50, readonly=True)
    dchl_bhyt_md_cty = fields.Float('(%) mức đóng của Cty', default= 3.00, readonly=True)
#    ngayhethan = fields.Date('Ngày hết hạn')
#    dkkhambenh = fields.Text('Nơi đăng ký khám chữa bệnh')

#########################################################################################################
#function ẩn các field trong custom filter
    def fields_get(self, fields=None):
        fields_an_di = ['dchl_bhxh_md_nld','dchl_bhxh_md_cty',
                          'dchl_bhtn_md_nld', 'dchl_bhtn_md_cty',
                         'dchl_bhyt_md_nld', 'dchl_bhyt_md_cty',
                         'dchl_bhtn', 'dchl_bhxh',
                        'dchl_vung', 'dchl_sobaohiem',
                         'currency_id', 'state',
                        'dchl_thoigian']
        res = super(DieuChinhHangLoat, self).fields_get()
        for field in fields_an_di:
            res[field]['selectable'] = False
        return res

#########################################################################################################
#Định nghĩa các button. Trong python, thụt hàng không đúng cũng báo lỗi

    @api.onchange('dchl_vung')
    def filter_theo_dchl_vung(self):
        for rec in self:
            if rec.dchl_vung:
                
                for line in rec.dchl_vung:
                    lcs_bhxh = self.env["cauhinh.vung"].search([('bhxh_lcs', '=', line.bhxh_lcs)])
            
                    if lcs_bhxh:
                        #filter và chỉ show ra các value trong field 'bhxh_bh' của one2many 'dchl_sobaohiem'
                        #khi bằng với value của field 'bhxh_lcs' trong many2one 'dchl_vung'
                        return {'domain': {'dchl_sobaohiem': [('bhxh_bh','=', lcs_bhxh.bhxh_lcs)]}}
            
    
    def xacnhan(self):
        
        for rec in self:
            #nếu field one2many dchl_sobaohiem không có chọn record qua 'Add a line' link, phát thông báo tới user
            if not rec.dchl_sobaohiem:
                raise UserError (_("Bạn chưa chọn Sổ Bảo Hiểm cần điều chỉnh.\nVui lòng chọn ở phía dưới !"))
            
            #nếu field one2many dchl_sobaohiem có chọn record qua 'Add a line' link, chuyển state sang trạng thái 'daduocxacnhan'
            rec.state = "daduocxacnhan"

        return True
           
    def chapthuan(self):
        for rec in self:            
            if rec.dchl_sobaohiem:
                
                for add_a_line in rec.dchl_sobaohiem:
                    lstd_qua_bh_dchl = {
                        'name': add_a_line.name.id,
                        'thamchieu_ls': self.dchl_thamchieu,
                        'thoigian_ls': self.dchl_thoigian,
                        'bhxh_ls': self.dchl_bhxh,
                        'bhtn_ls': self.dchl_bhtn,
                        'bhxh_nld': self.dchl_bhxh_md_nld,
                        'bhxh_cty': self.dchl_bhxh_md_cty,
                        'bhtn_nld': self.dchl_bhtn_md_nld,
                        'bhtn_cty': self.dchl_bhtn_md_cty,
                        'bhyt_nld': self.dchl_bhyt_md_nld,
                        'bhyt_cty': self.dchl_bhyt_md_cty
                        }
                    
                    list_vals = []
                    list_vals.append([0, 0, lstd_qua_bh_dchl])
                
                    add_a_line.write({
                        'bhxh_nld_bh' : self.dchl_bhxh_md_nld,
                        'bhxh_cty_bh' : self.dchl_bhxh_md_cty,
                        'bhtn_nld_bh' : self.dchl_bhtn_md_nld,
                        'bhtn_cty_bh' : self.dchl_bhtn_md_cty,
                        'bhyt_nld_bh' : self.dchl_bhyt_md_nld,
                        'bhyt_cty_bh' : self.dchl_bhyt_md_cty,
                        'bhxh_bh' : self.dchl_bhxh,
                        'bhtn_bh' : self.dchl_bhtn,
                        
                        'state': 'dangchay',
                        'trangthai_bh': 'dangchay',
                        
                        'lstd_baohiem': list_vals
                    })

            rec.state = "daduyet"
                     
        return True            

############################################################################################################################

    def bihuy(self):
        for rec in self:
            rec.state = "bihuy"
            return True
        
    def veduthao(self):
        for rec in self:
            rec.state = "moi"
            return True
