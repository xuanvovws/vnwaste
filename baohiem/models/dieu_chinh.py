from odoo import fields, models, api, tools, _
from odoo.exceptions import UserError, ValidationError, Warning
#import python library for current datetiem()
from datetime import datetime

class DieuChinh(models.Model):
    _name = "dieu.chinh"
    _description = "Điều chỉnh model"
    #Thể hiện giá trị của thamchieu thay cho name (mặc định) sau khi tạo
    _rec_name = "thamchieu"

    #Dùng Many2one để lấy tên nhân viên đã có sẳn
    name = fields.Many2one('hr.employee', string="Sổ bảo hiểm", required=True,
                           states={
                                'daduocxacnhan': [('readonly', True)], #data field name = readonly khi state = daduocxacdinh
                                'daduyet': [('readonly', True)], #data field name = readonly khi state = daduyet (ĐÃ DUYỆt)
                                'bihuy': [('readonly', True)] #data field name = readonly khi state = bihuy (BỊ HỦY)
                            }
                          )

    knls_dieuchinh = fields.One2many('ketnoi.lichsu', 'dc_kn_ls', string="Lịch Sử Thông Tin")#Lịch Sử Thông Tin: Tên của form view khi show dạng popup
    
    #Tạo status bar
    state = fields.Selection([
            ('moi', 'THÔNG TIN'),
            ('daduocxacnhan', 'ĐÃ ĐƯỢC XÁC NHẬN'),
            ('daduyet', 'ĐÃ DUYỆT'),
            ('bihuy', 'BỊ HỦY'),
            ],default='moi')
    
    thamchieu = fields.Char('Tham chiếu', 
#                            default=' ', #set default = rỗng khi user không điền vào field thamchieu (do form ko bắt buộc), lúc đó  field 'thamchieu' sẽ show ra là trống (thay cho giá trị 'False' theo mặc định)
                            
                            #data field thamchieu sẽ = readonly khi state thay đổi trạng thái
                            states={
                                'daduocxacnhan': [('readonly', True)], #data field thamchieu = readonly khi state = daduocxacdinh
                                'daduyet': [('readonly', True)], #data field thamchieu = readonly khi state = daduyet (ĐÃ DUYỆt)
                                'bihuy': [('readonly', True)] #data field thamchieu = readonly khi state = bihuy (BỊ HỦY)
                            })

    
    #default=datetime.today() --> tự động chọn ngày hiện tại thông qua import python library phía trên
    thoigian = fields.Date('Ngày duyệt', default=datetime.today(),

                           states={
                                   'daduocxacnhan':[('readonly', True)],
                                   'daduyet': [('readonly', True)],
                                   'bihuy': [('readonly', True)]
                                  })
    
    
    #Dùng Monetary để thể hiện chức năng của field là tiền tệ
    #Khi dùng field.Monetary , bắt buộc phải khai báo thêm field với tên biến là (currency_id)
    #Nếu muốn thêm biểu tượng tiền tệ ở sau field (bhxh, bhtn,... ) thì cần thêm: default=lambda self:self.env.user... ở currency_id
    #Sau đó (hoặc trước đó), từ UI, vào Settings --> Users & Companies --> Companies --> Chọn lại tiền tệ (currency)
    currency_id = fields.Many2one("res.currency", 
                                  string="Loại tiền tệ", default=lambda self:self.env.user.company_id.currency_id.id,required=True)
    
    bhxh = fields.Monetary('Mức đóng BHXH',                          
                           states={
                                   'daduocxacnhan':[('readonly', True)],
                                   'daduyet': [('readonly', True)],
                                   'bihuy': [('readonly', True)]
                                  })
    
    bhtn = fields.Monetary('Mức đóng BHTN',
                           states={
                                   'daduocxacnhan':[('readonly', True)],
                                   'daduyet': [('readonly', True)],
                                   'bihuy': [('readonly', True)],
                                  })

    
    #Dùng readonly=True, để tạo field nhưng không cho điền vào field
    #Chuyển dấu phân cách nhóm số từ dấu (.) sang (,) hoặc ngược lại:
    #--> Vào Odoo bật chế độ developer mode --> Settings --> Translation --> Language --> chọn kiểu xong --> Active & Translate
    #Hoặc chỉnh trong widget = autofillseparate
    
    #Set các giá trị default cho các field (biến)
    bhxh_mucdongnld = fields.Float('(%) mức đóng của NLĐ', default = 8.00, readonly=True)
    bhxh_mucdongcty = fields.Float('(%) mức đóng của Cty', default = 17.50, readonly=True)
    bhtn_mucdongnld = fields.Float('(%) mức đóng của NLD', default = 1.00, readonly=True)
    bhtn_mucdongcty = fields.Float('(%) mức đóng của Cty', default = 1.00, readonly=True)
    bhyt_mucdongnld = fields.Float('(%) mức đóng của NLĐ', default = 1.50, readonly=True)
    bhyt_mucdongcty = fields.Float('(%) mức đóng của Cty', default = 3.00, readonly=True)
#    ngayhethan = fields.Date('Ngày hết hạn')
#    dkkhambenh = fields.Text('Nơi đăng ký khám chữa bệnh')

################################################################################################################################
#function ẩn các field trong custom filter
    def fields_get(self, fields=None):
        fields_an_di = ['bhxh_mucdongnld','bhxh_mucdongcty',
                          'bhtn_mucdongnld', 'bhtn_mucdongcty',
                         'bhyt_mucdongnld', 'bhyt_mucdongcty',
                         'bhtn', 'bhxh',
                        'thoigian', 'knls_dieuchinh',
                         'currency_id', 'state',
                       'name',]
        res = super(DieuChinh, self).fields_get()
        for field in fields_an_di:
            res[field]['selectable'] = False
        return res
################################################################################################################################
#Định nghĩa các button. Trong python, thụt hàng không đúng cũng báo lỗi

    def xacnhan(self):
        for rec in self:
            #search trong model bao_hiem.py, field 'name' = với field 'name' của model dieu_chinh.py
            ten = self.env["bao.hiem"].search([('name','=', rec.name.id)])

            #Theo quy trình, 1 user mới phải đăng ký ở Sổ Bảo Hiểm (bao_hiem.py) trước. Sau đó mới sử dụng tới tab Điều Chỉnh (dieu_chinh.py)
            #Để tránh tình trạng user chưa đăng ký, mà đã khai báo bên tab Điều Chỉnh (dieu_chinh.py). Xét điều kiện:
            
            if rec.name != ten.name: #Nếu tên user ở model (dieu_chinh.py) == tên user ở model (bao_hiem.py)
                rec.unlink() #xóa record trước khi hiện thông báo A
                
                return {
                    'name': 'Thông Báo',
                    'view_mode': 'form',
                    'res_model': 'dc.tba',
                    'target': 'new',
                    'type': 'ir.actions.act_window',
                }
                
            rec.state = "daduocxacnhan" #Nếu tên == (bằng) ==> chuyển state
                
        return True
################################################################################################################################
  
    def chapthuan(self):
        for rec in self:
            bh = self.env["bao.hiem"].search([('name','=',rec.name.id)])
            if bh:
                #gửi các giá trị default của model dieu_chinh.py cho các field của model bao_hiem.py khi state chuyển trạng thái
                bh['bhxh_nld_bh'] = self.bhxh_mucdongnld
                bh['bhxh_cty_bh'] = self.bhxh_mucdongcty
                bh['bhtn_nld_bh'] = self.bhtn_mucdongnld
                bh['bhtn_cty_bh'] = self.bhtn_mucdongcty
                bh['bhyt_nld_bh'] = self.bhyt_mucdongnld
                bh['bhyt_cty_bh'] = self.bhyt_mucdongcty
                #gửi các giá trị mới nhất của field: 'bhxh', 'bhtn' ở model dieu_chinh.py
                #sang field: 'bhxh_bh', 'bhtn_bh' của model bao_hiem.py
                bh['bhxh_bh'] = self.bhxh
                bh['bhtn_bh'] = self.bhtn
                
                bh.write({'state': 'dangchay',
                         'trangthai_bh': 'dangchay'})
                
            rec.state = "daduyet" #state của model dieu_chinh.py chuyển trạng thái
                  
        gt_ketnoi_lichsu_qua_dc = {
            'name': self.name.id,
            'knls_thamchieu': self.thamchieu,
            'knls_thoigian': self.thoigian,
            'knls_bhxh': self.bhxh,
            'knls_bhtn': self.bhtn,
            'bhxh_md_nld': self.bhxh_mucdongnld,
            'bhxh_md_cty': self.bhxh_mucdongcty,
            'bhtn_md_nld': self.bhtn_mucdongnld,
            'bhtn_md_cty': self.bhtn_mucdongcty,
            'bhyt_md_nld': self.bhyt_mucdongnld,
            'bhyt_md_cty': self.bhyt_mucdongcty
        }
        
        list_vals = []   
        #dùng dictionary (0, 0, values): thêm (add) các record được tạo (created) từ các values được cung cấp
        list_vals.append([0, 0, gt_ketnoi_lichsu_qua_dc]) #nối thêm (append) dictionary(0, 0, values) vào biến list_vals
        
        self.write({'knls_dieuchinh': list_vals}) #tạo bản ghi (record) các gt trong one2many tree view: lstd_dieuchinh trong form view dieu_chinh.py

        gt_lstd_qua_bh = {
            'name' : self.name.id,
            'thamchieu_ls' : self.thamchieu,
            'thoigian_ls' : self.thoigian,
            'bhxh_ls' : self.bhxh,
            'bhtn_ls' : self.bhtn,
            'bhxh_nld' : self.bhxh_mucdongnld,
            'bhxh_cty' : self.bhxh_mucdongcty,
            'bhtn_nld' : self.bhtn_mucdongnld,
            'bhtn_cty' : self.bhtn_mucdongcty,
            'bhyt_nld' : self.bhyt_mucdongnld,
            'bhyt_cty' : self.bhyt_mucdongcty
        }
        
        list_of_lstd = []
        list_of_lstd.append([0, 0, gt_lstd_qua_bh])
        
        bh.write({'lstd_baohiem': list_of_lstd}) #tạo bản ghi (record) THEO TỪNG TÊN CỦA USER trong one2many tree view: lstd_baohiem
    
        return True            
################################################################################################################################
    
    def chapthuan_tld(self): #định nghĩa nút 'Chấp Thuận' sau khi click 'Tăng lao động'
        for rec in self:
            
            bh_tld = self.env["bao.hiem"].search([('name','=',rec.name.id)])
            if bh_tld:
                #set default các giá trị khi state chuyển trạng thái
                bh_tld['bhxh_nld_bh'] = self.bhxh_mucdongnld
                bh_tld['bhxh_cty_bh'] = self.bhxh_mucdongcty
                bh_tld['bhtn_nld_bh'] = self.bhtn_mucdongnld
                bh_tld['bhtn_cty_bh'] = self.bhtn_mucdongcty
                bh_tld['bhyt_nld_bh'] = self.bhyt_mucdongnld
                bh_tld['bhyt_cty_bh'] = self.bhyt_mucdongcty
                
                bh_tld['bhxh_bh'] = self.bhxh
                bh_tld['bhtn_bh'] = self.bhtn
                
                
                bh_tld.write({'state': 'dangchay',
                             'trangthai_bh': 'dangchay'})
                
            rec.state = "daduyet" #state của model dieu_chinh.py chuyển trạng thái ở tld


        gt_ketnoi_lichsu_qua_dc_tld = {
            'name': self.name.id,
            'knls_thamchieu': self.thamchieu,
            'knls_thoigian': self.thoigian,
            'knls_bhxh': self.bhxh,
            'knls_bhtn': self.bhtn,
            'bhxh_md_nld': self.bhxh_mucdongnld,
            'bhxh_md_cty': self.bhxh_mucdongcty,
            'bhtn_md_nld': self.bhtn_mucdongnld,
            'bhtn_md_cty': self.bhtn_mucdongcty,
            'bhyt_md_nld': self.bhyt_mucdongnld,
            'bhyt_md_cty': self.bhyt_mucdongcty,
            'loai': 'tanglaodong'
        }
        
        list_of_ketnoi_lichsu = []
        list_of_ketnoi_lichsu.append([0, 0, gt_ketnoi_lichsu_qua_dc_tld])
        
        self.write({'knls_dieuchinh': list_of_ketnoi_lichsu})
        
        gt_lstd_qua_bh_tld = {
            'name' : self.name.id,
            'thamchieu_ls' : self.thamchieu,
            'thoigian_ls' : self.thoigian,
            'bhxh_ls' : self.bhxh,
            'bhtn_ls' : self.bhtn,
            'bhxh_nld' : self.bhxh_mucdongnld,
            'bhxh_cty' : self.bhxh_mucdongcty,
            'bhtn_nld' : self.bhtn_mucdongnld,
            'bhtn_cty' : self.bhtn_mucdongcty,
            'bhyt_nld' : self.bhyt_mucdongnld,
            'bhyt_cty' : self.bhyt_mucdongcty,
            'loai': 'tanglaodong'
        }

        list_of_lstd_tld = []
        list_of_lstd_tld.append([0, 0, gt_lstd_qua_bh_tld])
        
        bh_tld.write({'lstd_baohiem': list_of_lstd_tld})
        
        return True
################################################################################################################################
        
    def bihuy(self):
        for rec in self:
            rec.state = "bihuy"
            return True
        
    def veduthao(self):
        for rec in self:
            rec.state = "moi"
            return True
################################################################################################################################

    def giam_tam_thoi_popup(self):
        for rec in self:
            gtt_bh = self.env["bao.hiem"].search([('name','=',rec.name.id)])
            if gtt_bh:
                #theo quy trình; khi giảm tạm thời, mức đóng các loại bh... sẽ = 0
                gtt_bh['bhxh_bh'] = 0.00
                gtt_bh['bhtn_bh'] = 0.00
                
                gtt_bh.write({'state': 'giamtamthoi',
                             'trangthai_bh': 'giamtamthoi'})

        ketnoi_lichsu_gtt = {
            'name': self.name.id,
            'knls_thamchieu': self.thamchieu,
            'knls_thoigian': self.thoigian,
            'knls_bhxh': 0.00,
            'knls_bhtn': 0.00,
            'bhxh_md_nld': self.bhxh_mucdongnld,
            'bhxh_md_cty': self.bhxh_mucdongcty,
            'bhtn_md_nld': self.bhtn_mucdongnld,
            'bhtn_md_cty': self.bhtn_mucdongcty,
            'bhyt_md_nld': self.bhyt_mucdongnld,
            'bhyt_md_cty': self.bhyt_mucdongcty,
            'loai': 'giamtamthoi'
        }
        
        list_gtt = []
        list_gtt.append([0, 0, ketnoi_lichsu_gtt])
        
        self.write({'knls_dieuchinh': list_gtt})
        
        gt_lstd_qua_bh_gtt = {
            'name' : self.name.id,
            'thamchieu_ls' : self.thamchieu,
            'thoigian_ls' : self.thoigian,
            'bhxh_ls' : 0.00,
            'bhtn_ls' : 0.00,
            'bhxh_nld' : self.bhxh_mucdongnld,
            'bhxh_cty' : self.bhxh_mucdongcty,
            'bhtn_nld' : self.bhtn_mucdongnld,
            'bhtn_cty' : self.bhtn_mucdongcty,
            'bhyt_nld' : self.bhyt_mucdongnld,
            'bhyt_cty' : self.bhyt_mucdongcty,
            'loai': 'giamtamthoi'
        }
        
        list_of_lstd_gtt = []
        list_of_lstd_gtt.append([0, 0, gt_lstd_qua_bh_gtt])

        gtt_bh.write({'lstd_baohiem': list_of_lstd_gtt})
                
        return True
################################################################################################################################
    
    def ket_thuc_popup(self):
        for rec in self:
            kt_bh = self.env["bao.hiem"].search([('name','=',rec.name.id)])
            if kt_bh:
                #theo quy trình; khi kết thúc, mức đóng các loại bh... sẽ = 0 , (%) mức đóng các loại = 0
                kt_bh['bhxh_bh'] = 0.00
                kt_bh['bhtn_bh'] = 0.00
                kt_bh['bhxh_nld_bh'] = 0.00
                kt_bh['bhxh_cty_bh'] = 0.00
                kt_bh['bhtn_nld_bh'] = 0.00
                kt_bh['bhtn_cty_bh'] = 0.00
                kt_bh['bhyt_nld_bh'] = 0.00
                kt_bh['bhyt_cty_bh'] = 0.00
                
                
                kt_bh.write({'state': 'ketthuc',
                            'trangthai_bh': 'ketthuc'})
        
        ketnoi_lichsu_kt = {
            'name': self.name.id,
            'knls_thamchieu': self.thamchieu,
            'knls_thoigian': self.thoigian,
            'knls_bhxh': 0.00,
            'knls_bhtn': 0.00,
            'bhxh_md_nld': 0.00,
            'bhxh_md_cty': 0.00,
            'bhtn_md_nld': 0.00,
            'bhtn_md_cty': 0.00,
            'bhyt_md_nld': 0.00,
            'bhyt_md_cty': 0.00,
            'loai': 'ket_thuc'
        }
        
        list_kt = []
        list_kt.append([0, 0, ketnoi_lichsu_kt])
        
        self.write({'knls_dieuchinh': list_kt})
        
        gt_lstd_qua_bh_kt = {
            'name' : self.name.id,
            'thamchieu_ls' : self.thamchieu,
            'thoigian_ls' : self.thoigian,
            'bhxh_ls' : 0.00,
            'bhtn_ls' : 0.00,
            'bhxh_nld' : 0.00,
            'bhxh_cty' : 0.00,
            'bhtn_nld' : 0.00,
            'bhtn_cty' : 0.00,
            'bhyt_nld' : 0.00,
            'bhyt_cty' : 0.00,
            'loai': 'ket_thuc'
        }
        
        list_of_lstd_kt = []
        list_of_lstd_kt.append([0, 0, gt_lstd_qua_bh_kt])

        kt_bh.write({'lstd_baohiem': list_of_lstd_kt})
                     
        return True
################################################################################################################################    
    
class dc_tba(models.TransientModel):
    _name = 'dc.tba'
    _description = 'Thông Báo A'

#    message = fields.Text(string="Người Lao động này chưa đăng ký sổ Bảo Hiểm !", readonly=True, store=True)

    def dk_so_bao_hiem(self):
        return {
            'view_mode': 'form',
            'res_model': 'bao.hiem',
            #'target': 'main'  : để xóa đi những thông tin cũ của record đã xóa
            'target': 'main',
            'type': 'ir.actions.act_window',
            }
    
    def huy_dk_sbh(self):
        return {
            'view_mode': 'form',
            'res_model': 'dieu.chinh',
            'target': 'main',
            'type': 'ir.actions.act_window',
        }
    