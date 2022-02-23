# -*- coding: utf-8 -*-
from datetime import timedelta, datetime, date
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError, Warning
#khai báo calendar để áp dụng cho compute function 'Tổng Ngày Công'
import calendar

class DuLieu(models.Model):
    _name = "du.lieu"
    _description = "Dữ liệu ban đầu từ Máy chấm công"
    
    name_dl = fields.Many2one('hr.employee','Nhân viên',
                             states={
                                'tiepnhan': [('readonly', True)],
                                'hoantat': [('readonly', True)]
                            })
    
    thoigian_dl = fields.Date('Thời gian', default=fields.Date.today,
                             states={
                                'tiepnhan': [('readonly', True)],
                                'hoantat': [('readonly', True)]
                            })
    
    time1 = fields.Float('Thời gian 1', 
                        states={
                                'tiepnhan': [('readonly', True)],
                                'hoantat': [('readonly', True)]
                            })
    
    time2 = fields.Float('Thời gian 2',
                        states={
                                'tiepnhan': [('readonly', True)],
                                'hoantat': [('readonly', True)]
                            })
    
    ca_lam_viec_dl = fields.Many2one('planning.role', 'Ca làm việc', readonly=True)
    
    state = fields.Selection([
            ('ghinhan_dl', 'Ghi Nhận'),
            ('tiepnhan_dl', 'Tiếp Nhận'),
            ('hoantat_dl', 'Đã Chấm Công'),
            ('kt_data', 'Kiểm Tra Lại Dữ Liệu'),
            #Dành cho chấm công theo Ca Làm Việc
            #('hoantat_ca_dl', 'Đã Chấm Công Theo Ca'),
            ], string="Trạng thái", readonly=True)
    
    min_time1 = fields.Float('Min Time 1', compute='_tim_min_time1')    
    @api.depends('time1')
    def _tim_min_time1(self):
        for rec in self:
            min_time1_val = min(self.filtered(lambda x: x.name_dl == rec.name_dl and x.thoigian_dl == rec.thoigian_dl).mapped('time1'))
            rec.min_time1 = min_time1_val
            
    max_time1 = fields.Float('Max Time 1', compute='_tim_max_time1')    
    @api.depends('time1')
    def _tim_max_time1(self):
        for rec in self:
            max_time1_val = max(self.filtered(lambda x: x.name_dl == rec.name_dl and x.thoigian_dl == rec.thoigian_dl).mapped('time1'))
            rec.max_time1 = max_time1_val
            
    min_time2 = fields.Float('Min Time 2', compute='_tim_min_time2')    
    @api.depends('time2')
    def _tim_min_time2(self):
        for rec in self:
            min_time2_val = min(self.filtered(lambda x: x.name_dl == rec.name_dl and x.thoigian_dl == rec.thoigian_dl).mapped('time2'))
            rec.min_time2 = min_time2_val
            
    max_time2 = fields.Float('Max Time 2', compute='_tim_max_time2')    
    @api.depends('time2')
    def _tim_max_time2(self):
        for rec in self:
            max_time2_val = max(self.filtered(lambda x: x.name_dl == rec.name_dl and x.thoigian_dl == rec.thoigian_dl).mapped('time2'))
            rec.max_time2 = max_time2_val

#-----------------------------------------
# Chấm Công theo Nhân Viên
#-----------------------------------------    
class ChamCongNhanVien(models.Model):
    _name = "chamcong.nv"
    _description = "Chấm công theo từng nhân viên"
    _rec_name = "name_ccnv"
    
    name_ccnv = fields.Many2one('hr.employee', 'Nhân viên', required=True,
                               states={
                                    'daduocxacnhan': [('readonly', True)],
                                    'daduyet': [('readonly', True)],
                                    'chamcong_ccnv': [('readonly', True)]
                                })
    
    ca_lam_viec_ccnv = fields.Many2one('planning.role', string='Ca làm việc',
                                      states={
                                            'daduocxacnhan': [('readonly', True)],
                                            'daduyet': [('readonly', True)],
                                            'chamcong_ccnv': [('readonly', True)]
                                        })
    
    thoigian_ccnv = fields.Date('Ngày làm việc', default=fields.Date.today,
                               states={
                                    'daduocxacnhan': [('readonly', True)],
                                    'daduyet': [('readonly', True)],
                                    'chamcong_ccnv': [('readonly', True)]
                                })
    
    thamchieu_ccnv = fields.Char('Tham chiếu', required=True,
                                states={
                                    'daduocxacnhan': [('readonly', True)],
                                    'daduyet': [('readonly', True)],
                                    'chamcong_ccnv': [('readonly', True)]
                                })
    
    giovao_ccnv = fields.Float('Giờ Vào', states={
                                    'daduocxacnhan': [('readonly', True)],
                                    'daduyet': [('readonly', True)],
                                    'chamcong_ccnv': [('readonly', True)]
                                })
    
    giora_ccnv = fields.Float('Giờ Ra', states={
                                    'daduocxacnhan': [('readonly', True)],
                                    'daduyet': [('readonly', True)],
                                    'chamcong_ccnv': [('readonly', True)]
                                })
    
    trangthai_ccnv = fields.Selection([
            ('chuaxong_ccnv', 'Chưa Chấm Công'),
            ('chochapthuan_ccnv', 'Chưa Chấp Thuận'),
            ('choxacnhan_ccnv', 'Chưa Xác Nhận')
            ], string="Trạng thái")
    
    state = fields.Selection([
            ('moi', 'DỰ THẢO'),
            ('daduocxacnhan', 'ĐÃ ĐƯỢC XÁC NHẬN'),
            ('daduyet', 'ĐÃ DUYỆT'),
            ('chamcong_ccnv', 'HOÀN TẤT'),
            ],default='moi')
    
    lscc_kn_ccnv = fields.One2many('ls.chamcong', 'ccnv_kn_lscc', string="Danh Sách Chấm Công")
    
    @api.onchange('name_ccnv')
    def kiemtra_dulieu(self):
        warning_dl = self.env["du.lieu"].search([])
        res = {}
        if not warning_dl:
            self.name_ccnv = False            
            #Note: thông báo bằng 'warning' dạng này chỉ được dùng với onchange
            res['warning'] = {'title': _('Thông Báo'), 
                              'message': _('Không có Dữ liệu chấm công.\nVui lòng kiểm tra lại ở mục Dữ liệu!')}
            return res
        
    def xacnhan_ccnv(self):
        if not self.ca_lam_viec_ccnv:
            self.trangthai_ccnv = "choxacnhan_ccnv"
            message = {
               'type': 'ir.actions.client',
               'tag': 'display_notification',
               'params': {
                   'title': _('Thông Báo'),
                   'message': 'Bạn chưa chọn Ca làm việc.\nVui lòng chọn để tiếp tục!',
                   'sticky': False,
                }
            }
            return message

        else:
            self.trangthai_ccnv = "chochapthuan_ccnv"
            self.state = "daduocxacnhan"
            
    def chapthuan_ccnv(self):
        for rec in self:
            list_duplicate = self.env["ls.chamcong"].search([('name', '=', self.name_ccnv.id),
                                                            ('ca_lam_viec_lscc', '=', self.ca_lam_viec_ccnv.id),
                                                            ('ngay_bd_lscc', '=', self.thoigian_ccnv)])
            if list_duplicate:
                raise Warning ("Nhân viên này đã được Chấm công!\nVui lòng kiểm tra lại ở mục Lịch Sử!")
        
            else:
                ca_lam_viec = self.env["ca.lamviec"].search([('name_clv', '=', self.ca_lam_viec_ccnv.id)])
                for line in ca_lam_viec:
                    if not rec.giovao_ccnv:
                        if rec.giora_ccnv:
                            raise Warning("Không có Dữ liệu Giờ Vào. Vui lòng kiểm tra lại !")
                        else:
                            raise Warning("Không có Dữ liệu Giờ Vào/Giờ Ra. Vui lòng kiểm tra lại !")
                    else:
                        if not rec.giora_ccnv:
                            raise Warning("Không có Dữ liệu Giờ Ra. Vui lòng kiểm tra lại !")
                        else:
                            if rec.giovao_ccnv >= rec.giora_ccnv:
                                raise Warning("Giờ Vào KHÔNG thể lớn hơn (>) hoặc bằng (=) Giờ Ra.\nVui lòng kiểm tra lại !")
                            else:
                                no_duplicate = {
                                            'name': rec.name_ccnv.id,
                                            'ngay_bd_lscc': rec.thoigian_ccnv,
                                            'ca_lam_viec_lscc': rec.ca_lam_viec_ccnv.id,
                                            'time1_lscc': rec.giovao_ccnv,
                                            'time2_lscc': rec.giora_ccnv,
                                            'thamchieu_lscc': 'chuaxong'
                                            }
                                list_data = []
                                list_data.append([0, 0, no_duplicate])
                                self.write({'lscc_kn_ccnv': list_data})
            
            self.trangthai_ccnv = "chuaxong_ccnv"
            self.state = "daduyet"
            
    def chamcong_ccnv(self):
        ca_lam_viec = self.env["ca.lamviec"].search([('name_clv', '=', self.ca_lam_viec_ccnv.id)])
        for nhanvien in ca_lam_viec:
            dscc_nv = self.env["ls.chamcong"].search([('ca_lam_viec_lscc', '=', self.ca_lam_viec_ccnv.id),
                                                      ('ngay_bd_lscc', '=', self.thoigian_ccnv)])
            for a in dscc_nv:
                if a.time1_lscc >= nhanvien.giovao1:
                    if a.time1_lscc <= nhanvien.giovao2:
                        if a.time2_lscc >= nhanvien.giora1: #Giờ Vào, Giờ Ra đều HỢP LỆ
                            a.ngaycong = 1
                            a.write({'thamchieu_lscc': 'chamcong_nv'})
                        else:
                            a.ngaycong = 0.5
                            a.write({'thamchieu_lscc': 'early_ccnv'})
                    else:
                        if a.time2_lscc >= nhanvien.giora1:
                            a.ngaycong = 0.5
                            a.write({'thamchieu_lscc': 'late_ccnv'})
                        else:
                            #ngày công = 0
                            a.write({'thamchieu_lscc': 'late_early_ccnv'})
                else:
                    if a.time2_lscc >= nhanvien.giora1:
                        a.ngaycong = 1
                        a.write({'thamchieu_lscc': 'chamcong_nv'})
                    else:
                        a.ngaycong = 0.5
                        a.write({'thamchieu_lscc': 'early_ccnv'})

        self.trangthai_ccnv = False
        self.state = "chamcong_ccnv"
        
    def veduthao_ccnv(self):
        for rec in self:
            #Khi về dự thảo, thì record tạo ra từ 'Xác Nhận' vẫn được save với trạng thái 'Chờ Xác Nhận'. 
            #Không cần xóa record.
            rec.trangthai_ccnv = 'choxacnhan_ccnv'
            rec.state = "moi"
            return True
        
    def huy_ccnv(self):
        for rec in self:
            #Xóa record hiện tại
            rec.unlink()
            
            #Sau khi xóa, trở lại form view với trạng thái ban đầu
            return {
                'view_mode': 'form',
                'res_model': 'chamcong.nv',
                #Dùng 'main' thay 'current' hợp lý hơn vì đã xóa record
                'target': 'main',
                'type': 'ir.actions.act_window',
                }

        return True
        
#-----------------------------------------
# Chấm Công theo Ca
#-----------------------------------------            
class ChamCong(models.Model):
    _name = "cham.cong"
    _description = "Dựa vào Lịch làm việc và dữ liệu check-in, check-out thực tế để Chấm Công"
    #Thể hiện giá trị của ca_lam_viec thay cho name (mặc định) sau khi tạo
    _rec_name = "ca_lam_viec"
    
    thoigian = fields.Date('Ngày', default=fields.Date.today,
                          states={
                                'daduocxacnhan': [('readonly', True)], #data field name = readonly khi state = daduocxacdinh
                                'daduyet': [('readonly', True)], #data field name = readonly khi state = daduyet (ĐÃ DUYỆt)
                                'chamcong': [('readonly', True)] #data field name = readonly khi state = bihuy (BỊ HỦY)
                            })
    
    thamchieu = fields.Selection([('del_duplicate', 'Xóa Trùng Lắp')], string="Tham Chiếu")
    
    #chọn data từ model planning.role của module Planning
    ca_lam_viec = fields.Many2one('planning.role', string="Ca làm việc",
                                 states={
                                'daduocxacnhan': [('readonly', True)],
                                'daduyet': [('readonly', True)],
                                'chamcong': [('readonly', True)]
                            })
    
    #Tạo status bar
    state = fields.Selection([
            ('moi', 'DỰ THẢO'),
            ('daduocxacnhan', 'ĐÃ ĐƯỢC XÁC NHẬN'),
            ('daduyet', 'ĐÃ DUYỆT'),
            ('chamcong', 'HOÀN TẤT'),
            ],default='moi')
    
    trangthai_cc = fields.Selection([
            ('chuaxong', 'Chưa Chấm Công'),
            ('chochapthuan', 'Chưa Chấp Thuận'),
            ('choxacnhan', 'Chưa Xác Nhận'),
            ('hoantat_ca', 'Hoàn Tất'),
            ], string="Trạng thái")
    
    lscc_kn_chamcong = fields.One2many('ls.chamcong', 'chamcong_kn_lscc', string="Lịch Sử Chấm Công")    
    baocao_kn_chamcong = fields.One2many('bao.cao', 'chamcong_kn_bc', string="Báo Cáo")
    dscc_kn_chamcong = fields.One2many('ds.chamcong', 'chamcong_kn_dscc', string="Lịch Làm Việc")
           
    @api.onchange('ca_lam_viec')
    def onchange_get_data(self):
        #Kiểm tra xem tab 'Dữ Liệu' có data trước không (bắt buộc)
        #Nếu chưa có, raise thông báo
        warning_dulieu = self.env["du.lieu"].search([])
        res = {}
        if not warning_dulieu:            
            #Note: thông báo bằng 'warning' dạng này chỉ được dùng với onchange
            res['warning'] = {'title': _('Thông Báo'),
                             'message': _('Không có Dữ liệu chấm công.\nVui lòng kiểm tra lại ở mục Dữ liệu!')}
            return res

        for rec in self:
            #Theo vòng lặp, khi thay đổi giá trị onchange 'ca_lam_viec',
            #Thì field planning_slot_kn_chamcong sẽ xóa đi giá trị cũ. 
            #Cách này tương tự như khai báo lines = [(5, 0, 0)] để xóa giá trị cũ
            rec.dscc_kn_chamcong = False
#            lines = [(5, 0, 0)]

            #khai báo các biến đang rỗng ở lúc đầu
            lines = []     
            #Nếu field 'ca_lam_viec' trong model 'cham.cong' có data:
            if rec.ca_lam_viec:                
                gio = datetime.min.time() #min.time : nữa đêm
                ngay = rec.thoigian
                list_id = self.env["planning.slot"].search([('role_id', '=', rec.ca_lam_viec.id),
                                                            ('start_datetime', '>', datetime.combine(ngay,gio)),
                                                            ('start_datetime', '<', ngay + timedelta(days=1))])              
                #Khai báo biến 'a' là 'đại diện các field' trong từng record trong biến list_id
                #đang chứa DANH SÁCH các record thỏa điều kiện:
                for a in list_id:
                    #biến vals tùy theo yêu cầu sẽ khai báo các field tương ứng để chứa data id bên ngoài vào
                    vals = {
                        'ca_lam_viec_dscc': a.role_id.id,
                        'name_dscc': a.employee_id.id,
                        'thoigian_bd_dscc': a.start_datetime, 
                        'thoigian_kt_dscc': a.end_datetime
                        }
                        #Gắn (append) các data của biến vals vào biến rỗng lines bằng dictionary(0, 0, {values})
                        #(0, 0,  { values })    link to a new record that needs to be created with the given values dictionary
                    lines.append((0, 0, vals))
                #Ghi các data của lines vào các field tương ứng của field one2many: planning_slot_kn_chamcong
                rec.dscc_kn_chamcong = lines

    def xacnhan(self):
        if not self.ca_lam_viec:
            self.trangthai_cc = "choxacnhan"
            message = {
               'type': 'ir.actions.client',
               'tag': 'display_notification',
               'params': {
                   'title': _('Thông Báo'),
                   'message': 'Bạn chưa chọn Ca làm việc.\nVui lòng chọn để tiếp tục!',
                   'sticky': False,
                }
            }
            return message

        else:
            self.trangthai_cc = "chochapthuan"
            self.state = "daduocxacnhan"                      
        return True
    
    def chapthuan(self):
        for line in self.dscc_kn_chamcong:
            if not line.trangthai_dscc:
                #Xét duplicate: Đầu tiên sẽ dò trong model ls_chamcong.py các field tương ứng '=' với các field
                #của o2m field: dscc_kn_chamcong với đk field trangthai_dscc '=': Rỗng (False)
                list_duplicate = self.env["ls.chamcong"].search([('ngay_bd_lscc', '=', self.thoigian),
                                                                 ('ca_lam_viec_lscc', '=', line.ca_lam_viec_dscc.id),
                                                                 ('name', '=', line.name_dscc.id)]) #(*)
                #Nếu thỏa các điều kiện (*)
                if list_duplicate:
                    return {
                            'name': "Thông Báo",
                            'view_mode': 'form',
                            'res_model': 'tb.lscc',
                            'context': {'default_ngay_tb': self.thoigian,
                                        'default_ca_lam_viec_tb': self.ca_lam_viec.id},
                            'target': 'new',
                            'type': 'ir.actions.act_window',
                            } 
                else:
                    duplicate_baocao = self.env['bao.cao'].search([('ngay_bd_bc', '=', self.thoigian),
                                                                   ('ca_lam_viec_bc', '=', line.ca_lam_viec_dscc.id),
                                                                   ('name_bc', '=', line.name_dscc.id)])
                    if duplicate_baocao:
                        return {
                                'name': "Thông Báo",
                                'view_mode': 'form',
                                'res_model': 'tb.lscc',
                                'context': {'default_ngay_tb': self.thoigian,
                                            'default_ca_lam_viec_tb': self.ca_lam_viec.id},
                                'target': 'new',
                                'type': 'ir.actions.act_window',
                                }
                    else:
                        list_dulieu = self.env["du.lieu"].search([('name_dl', '=', line.name_dscc.id),
                                                                  ('thoigian_dl', '=', self.thoigian)])
                        ds_calamviec = self.env["ca.lamviec"].search([('name_clv', '=', line.ca_lam_viec_dscc.id)])
                        for clv in ds_calamviec:
                            if clv.giovao1 <= 16.30:
                                h = []
                                i = []
                                j = []
                                k = []
                                l = []
                                for dulieu in list_dulieu:
                                    nhieu_record = self.env['du.lieu'].search([('name_dl', '=', dulieu.name_dl.id),
                                                                               ('thoigian_dl', '=', dulieu.thoigian_dl),
                                                                               ('state', '=', False)])
                                    if nhieu_record:
                                        for nhieu in nhieu_record:
                                            #Đặt nhiều record của 1 nv về trạng thái = 'Tiếp Nhận'
                                            nhieu.write({'state': 'tiepnhan_dl'})
                                            nhieu['ca_lam_viec_dl'] = line.ca_lam_viec_dscc.id
                                    if dulieu.max_time1 >= dulieu.max_time2:
                                        if dulieu.max_time1 <= clv.giovao2 + 0.1: #giovao2 + 10 phút: nếu <= : coi như không có giờ ra
                                            h = dulieu
                                            line.write({'trangthai_dscc': 'xacnhan'})
                                            break
                                        #nếu > giovao2:
                                        else:
                                            #thì xét nếu max_time1 có >= giora1:
                                            if dulieu.max_time1 >= clv.giora1:
                                                #Nếu >= giora1, xét tiếp nếu min_time1 có >= giora1: chỉ lấy max_time1 làm giờ ra
                                                #NOTE: không cần so sánh min_time1 với min_time2 vì: mặc định min_time1 luôn < min_time2
                                                if dulieu.min_time1 >= clv.giora1:
                                                    i = dulieu
                                                    line.write({'trangthai_dscc': 'xacnhan'})
                                                    break
                                                #Nếu không, 
                                                else:
                                                    #thì xét tiếp nếu min_time1 <= giora1 - 10 phút: lấy min_time1 và max_time1 làm giờ vào và ra
                                                    if dulieu.min_time1 <= clv.giora1 - 0.1:
                                                        j = dulieu
                                                        line.write({'trangthai_dscc': 'xacnhan'})
                                                        break
                                                    #Ngược lại,
                                                    else:
                                                        #Nếu min_time1 > giora1 - 0.1: chỉ lấy max_time1 làm giờ ra, coi như ko có giờ vào
                                                        i = dulieu
                                                        line.write({'trangthai_dscc': 'xacnhan'})
                                                        break
                                            else:
                                                j = dulieu
                                                line.write({'trangthai_dscc': 'xacnhan'})
                                                break
                                    else:
                                        if dulieu.max_time2 <= clv.giovao2 + 0.1:
                                            k = dulieu
                                            line.write({'trangthai_dscc': 'xacnhan'})
                                            break
                                        else:
                                            l = dulieu
                                            line.write({'trangthai_dscc': 'xacnhan'})
                                            break
                                if h:
                                    val_1 = {
                                            'name': line.name_dscc.id,
                                            'ngay_bd_lscc': self.thoigian,
                                            'ngay_kt_lscc': self.thoigian,
                                            'ca_lam_viec_lscc': line.ca_lam_viec_dscc.id,
                                            'time1_lscc': h.min_time1
                                            }
                                    list_val_1 = []
                                    list_val_1.append([0, 0, val_1])
                                    self.write({'lscc_kn_chamcong': list_val_1})
                                if i:
                                    val_2 = {
                                            'name': line.name_dscc.id,
                                            'ngay_bd_lscc': self.thoigian,
                                            'ngay_kt_lscc': self.thoigian,
                                            'ca_lam_viec_lscc': line.ca_lam_viec_dscc.id,
                                            'time2_lscc': i.max_time1
                                            }
                                    list_val_2 = []
                                    list_val_2.append([0, 0, val_2])
                                    self.write({'lscc_kn_chamcong': list_val_2})
                                if j:
                                    val_5 = {
                                            'name': line.name_dscc.id,
                                            'ngay_bd_lscc': self.thoigian,
                                            'ngay_kt_lscc': self.thoigian,
                                            'ca_lam_viec_lscc': line.ca_lam_viec_dscc.id,
                                            'time1_lscc': j.min_time1,
                                            'time2_lscc': j.max_time1
                                            }
                                    list_val_5 = []
                                    list_val_5.append([0, 0, val_5])
                                    self.write({'lscc_kn_chamcong': list_val_5})
                                if k:
                                    val_3 = {
                                            'name': line.name_dscc.id,
                                            'ngay_bd_lscc': self.thoigian,
                                            'ngay_kt_lscc': self.thoigian,
                                            'ca_lam_viec_lscc': line.ca_lam_viec_dscc.id,
                                            'time1_lscc': k.min_time1,
                                            }
                                    list_val_3 = []
                                    list_val_3.append([0, 0, val_3])
                                    self.write({'lscc_kn_chamcong': list_val_3})
                                if l:
                                    val_4 = {
                                            'name': line.name_dscc.id,
                                            'ngay_bd_lscc': self.thoigian,
                                            'ngay_kt_lscc': self.thoigian,
                                            'ca_lam_viec_lscc': line.ca_lam_viec_dscc.id,
                                            'time1_lscc': l.min_time1,
                                            'time2_lscc': l.max_time2
                                            }
                                    list_val_4 = []
                                    list_val_4.append([0, 0, val_4])
                                    self.write({'lscc_kn_chamcong': list_val_4})
                            #có làm qua đêm
                            else:
                                m = []
                                n = []
                                o = []
                                p = []
                                for dl in list_dulieu:
                                    nhieu_record = self.env['du.lieu'].search([('name_dl', '=', dl.name_dl.id),
                                                                               ('thoigian_dl', '=', dl.thoigian_dl),
                                                                               ('state', '=', False)])
                                    if nhieu_record:
                                        for nhieu in nhieu_record:
                                            #Đặt nhiều record của 1 nv về trạng thái = 'Tiếp Nhận'
                                            nhieu.write({'state': 'tiepnhan_dl'})
                                            nhieu['ca_lam_viec_dl'] = line.ca_lam_viec_dscc.id
                                    if dl.max_time1 >= dl.max_time2:
                                        #giovao2 + 10 phút: nếu <= : coi như không có giờ ra
                                        if dl.max_time1 <= clv.giovao2 + 0.1:
                                            m = dl
                                            line.write({'trangthai_dscc': 'xacnhan'})
                                            break
                                        #nếu > : coi như đó là giờ ra
                                        else:
                                            n = dl
                                            line.write({'trangthai_dscc': 'xacnhan'})
                                            break
                                    else:
                                        if dl.max_time2 <= clv.giovao2 + 0.1:
                                            o = dl
                                            line.write({'trangthai_dscc': 'xacnhan'})
                                            break
                                        else:
                                            p = dl
                                            line.write({'trangthai_dscc': 'xacnhan'})
                                            break                          
                                if m:
                                    val_5 = {
                                            'name': line.name_dscc.id,
                                            #ngày bắt đầu là ở thời điểm chọn chấm công
                                            'ngay_bd_lscc': self.thoigian,
                                            #có làm qua đêm, nên ngày kết thúc + thêm 1 ngày
                                            'ngay_kt_lscc': self.thoigian + timedelta(days=1),
                                            'ca_lam_viec_lscc': line.ca_lam_viec_dscc.id,
                                            #Lấy giờ nhỏ nhất làm giờ vào
                                            'time1_lscc': m.min_time1
                                            }
                                    list_val_5 = []
                                    list_val_5.append([0, 0, val_5])
                                    self.write({'lscc_kn_chamcong': list_val_5})
                                if n:
                                    val_6 = {
                                            'name': line.name_dscc.id,
                                            'ngay_bd_lscc': self.thoigian,
                                            'ngay_kt_lscc': self.thoigian + timedelta(days=1),
                                            'ca_lam_viec_lscc': line.ca_lam_viec_dscc.id,
                                            'time1_lscc': n.min_time1,
                                            #Lấy giờ lớn nhất của time1 làm giờ ra do > clv.giovao2 + 0.1
                                            'time2_lscc': n.max_time1
                                            }
                                    list_val_6 = []
                                    list_val_6.append([0, 0, val_6])
                                    self.write({'lscc_kn_chamcong': list_val_6})
                                if o:
                                    val_7 = {
                                            'name': line.name_dscc.id,
                                            'ngay_bd_lscc': self.thoigian,
                                            'ngay_kt_lscc': self.thoigian + timedelta(days=1),
                                            'ca_lam_viec_lscc': line.ca_lam_viec_dscc.id,
                                            'time1_lscc': o.min_time1,
                                            }
                                    list_val_7 = []
                                    list_val_7.append([0, 0, val_7])
                                    self.write({'lscc_kn_chamcong': list_val_7})                    
                                if p:
                                    val_8 = {
                                            'name': line.name_dscc.id,
                                            'ngay_bd_lscc': self.thoigian,
                                            'ngay_kt_lscc': self.thoigian + timedelta(days=1),
                                            'ca_lam_viec_lscc': line.ca_lam_viec_dscc.id,
                                            'time1_lscc': p.min_time1,
                                            'time2_lscc': p.max_time2,
                                            }
                                    list_val_8 = []
                                    list_val_8.append([0, 0, val_8])
                                    self.write({'lscc_kn_chamcong': list_val_8})        
                
        self.trangthai_cc = "chuaxong"
        self.state = 'daduyet'                              
        return True
            
    def chamcong(self):        
        for rec in self.dscc_kn_chamcong:
            #Các record bị 'trùng lặp' ở DS chấm công (nếu có) sẽ bị XÓA ở nút 'Chấm Công'
            if rec.trangthai_dscc == 'trunglap':
                rec.unlink()
                self.thamchieu = "del_duplicate"
            else:
                ds_clv = self.env["ca.lamviec"].search([('name_clv', '=', rec.ca_lam_viec_dscc.id)])
                for clv in ds_clv:
                    #Xác định các record thuộc 'Danh Sách Chấm Công' có clv với giờ vào <= 16.30
                    if clv.giovao1 <= 16.30:
                        #và chọn record có trạng thái = "Rỗng"...
                        if not rec.trangthai_dscc:
                            #... để ghi vào trạng thái = 'Xem Báo Cáo'...
                            rec.write({'trangthai_dscc': 'xem_bc',
                                       'thamchieu_dscc': 'cc_ca'})
                            thongso = {
                                        'name_bc': rec.name_dscc.id,
                                        'ngay_bd_bc': self.thoigian,
                                        'ngay_kt_bc': self.thoigian,
                                        'ca_lam_viec_bc': clv.name_clv.id,
                                        'thamchieu_bc': 'no_data'
                                        }
                            bc_thongso = []
                            bc_thongso.append([0, 0, thongso])
                            #... đồng thời ghi ra 'Báo Cáo' các giá trị của biến 'val'
                            self.write({'baocao_kn_chamcong': bc_thongso})
                        else:
                            ds_lscc = self.env["ls.chamcong"].search([('name', '=', rec.name_dscc.id),
                                                                      ('ca_lam_viec_lscc', '=', rec.ca_lam_viec_dscc.id),
                                                                      #chỉ có clv trong ngày mới có ngay kết thúc = self.ngay, nếu ko là clv qua đêm
                                                                      ('ngay_kt_lscc', '=', self.thoigian)])
                            for ds in ds_lscc:
                                if not ds.time1_lscc:
                                    if ds.time2_lscc:
                                        rec.write({'trangthai_dscc': 'xem_bc',
                                                   'thamchieu_dscc': 'cc_ca'})
                                        val = {
                                                'name_bc': ds.name.id,
                                                'ngay_bd_bc': ds.ngay_bd_lscc,
                                                'ngay_kt_bc': ds.ngay_kt_lscc,
                                                'ca_lam_viec_bc': ds.ca_lam_viec_lscc.id,
                                                'giovao_bc': ds.time1_lscc,
                                                'giora_bc': ds.time2_lscc,
                                                'thamchieu_bc': 'no_data_vao'
                                                }
                                        list_bc_val = []
                                        list_bc_val.append([0, 0, val])
                                        self.write({'baocao_kn_chamcong': list_bc_val})
                                        #XÓA record này ở 'Lịch Sử Chấm Công', cho user xem ở mục 'Báo Cáo'
                                        ds.unlink()
                                    #else:
                                        #không có time1_lscc:
                                            #không có time2_lscc:
                                                #=> no_data: giống trường hợp trên
                                else:
                                    if ds.time1_lscc <= clv.giovao2:
                                        #Xét tiếp giờ ra. Nếu ko có giờ ra (time2_lscc = False)
                                        if not ds.time2_lscc:
                                            rec.write({'trangthai_dscc': 'xem_bc',
                                                       'thamchieu_dscc': 'cc_ca'})
                                            val_2 = {
                                                        'name_bc': ds.name.id,
                                                        'ngay_bd_bc': ds.ngay_bd_lscc,
                                                        'ngay_kt_bc': ds.ngay_kt_lscc,
                                                        'ca_lam_viec_bc': ds.ca_lam_viec_lscc.id,
                                                        'giovao_bc': ds.time1_lscc,
                                                        'giora_bc': ds.time2_lscc,
                                                        'thamchieu_bc': 'no_data_ra'
                                                        }
                                            list_bc_val_2 = []
                                            list_bc_val_2.append([0, 0, val_2])
                                            self.write({'baocao_kn_chamcong': list_bc_val_2})
                                            #XÓA record này ở 'Lịch Sử Chấm Công', cho user xem ở mục 'Báo Cáo'
                                            ds.unlink()
                                        else:
                                            if ds.time2_lscc >= clv.giora1:
                                                ds.ngaycong = 1
                                                trangthai_dulieu = self.env["du.lieu"].search([('name_dl', '=', ds.name.id),
                                                                                               ('thoigian_dl', '=', ds.ngay_bd_lscc)])
                                                for tt in trangthai_dulieu:
                                                    tt.write({'state': 'hoantat_dl'})
                                                    self.write({'trangthai_cc': 'hoantat_ca'})
                                                    rec.write({'thamchieu_dscc': 'cc_ca'})
                                            #Ngược lại, nếu time2_lscc < giovao1:
                                            else:
                                                #Thì xét nếu time2_lscc <= giờ vào + 3 tiếng: Không chấm công 
                                                if ds.time2_lscc <= clv.giovao2 + 3:
                                                    ds.ngaycong = 0
                                                    ds.write({'thamchieu_lscc': 'early'})
                                                    trangthai_dulieu = self.env["du.lieu"].search([('name_dl', '=', ds.name.id),
                                                                                                   ('thoigian_dl', '=', ds.ngay_bd_lscc)])
                                                    for tt in trangthai_dulieu:
                                                        tt.write({'state': 'hoantat_dl'})
                                                        self.write({'trangthai_cc': 'hoantat_ca'})
                                                        rec.write({'thamchieu_dscc': 'cc_ca'})
                                                else:
                                                    ds.ngaycong = 0.5
                                                    ds.write({'thamchieu_lscc': 'early'})
                                                    trangthai_dulieu = self.env["du.lieu"].search([('name_dl', '=', ds.name.id),
                                                                                                   ('thoigian_dl', '=', ds.ngay_bd_lscc)])
                                                    for tt in trangthai_dulieu:
                                                        tt.write({'state': 'hoantat_dl'})
                                                        self.write({'trangthai_cc': 'hoantat_ca'})
                                                        rec.write({'thamchieu_dscc': 'cc_ca'})
                                    #Ngược lại, nếu time1_lscc > giovao2:
                                    else:
                                        #Thì xét nếu time1_lscc >= giovao2 + 30 phút: Không chấm công
                                        #Note: ko cần xét giờ ra
                                        if ds.time1_lscc >= clv.giovao2 + 0.30:
                                            ds.ngaycong = 0
                                            ds.write({'thamchieu_lscc': 'late'})
                                            trangthai_dulieu = self.env["du.lieu"].search([('name_dl', '=', ds.name.id),
                                                                                           ('thoigian_dl', '=', ds.ngay_bd_lscc)])
                                            for tt in trangthai_dulieu:
                                                tt.write({'state': 'hoantat_dl'})
                                                self.write({'trangthai_cc': 'hoantat_ca'})
                                                rec.write({'thamchieu_dscc': 'cc_ca'})
                                        #Ngược lại, nếu time1_lscc < giovao2 + 30 phút: Chấm 0.5 ngày công
                                        else:
                                            if not ds.time2_lscc:
                                                rec.write({'trangthai_dscc': 'xem_bc',
                                                           'thamchieu_dscc': 'cc_ca'})
                                                val_2 = {
                                                        'name_bc': ds.name.id,
                                                        'ngay_bd_bc': ds.ngay_bd_lscc,
                                                        'ngay_kt_bc': ds.ngay_kt_lscc,
                                                        'ca_lam_viec_bc': ds.ca_lam_viec_lscc.id,
                                                        'giovao_bc': ds.time1_lscc,
                                                        'giora_bc': ds.time2_lscc,
                                                        'thamchieu_bc': 'no_data_ra'
                                                        }
                                                list_bc_val_2 = []
                                                list_bc_val_2.append([0, 0, val_2])
                                                self.write({'baocao_kn_chamcong': list_bc_val_2})
                                                #XÓA record này ở 'Lịch Sử Chấm Công', cho user xem ở mục 'Báo Cáo'
                                                ds.unlink()
                                            else:
                                                if ds.time2_lscc >= clv.giora1:
                                                    ds.ngaycong = 0.5
                                                    ds.write({'thamchieu_lscc': 'late'})
                                                    trangthai_dulieu = self.env["du.lieu"].search([('name_dl', '=', ds.name.id),
                                                                                                   ('thoigian_dl', '=', ds.ngay_bd_lscc)])
                                                    for tt in trangthai_dulieu:
                                                        tt.write({'state': 'hoantat_dl'})
                                                        self.write({'trangthai_cc': 'hoantat_ca'})
                                                        rec.write({'thamchieu_dscc': 'cc_ca'})
                                                else:
                                                    #ngày công = 0
                                                    ds.write({'thamchieu_lscc': 'late_early'})
                                                    trangthai_dulieu = self.env["du.lieu"].search([('name_dl', '=', ds.name.id),
                                                                                                   ('thoigian_dl', '=', ds.ngay_bd_lscc)])
                                                    for tt in trangthai_dulieu:
                                                        tt.write({'state': 'hoantat_dl'})
                                                        self.write({'trangthai_cc': 'hoantat_ca'})
                                                        rec.write({'thamchieu_dscc': 'cc_ca'})
                    #Nếu > 16.30
                    else:
                        if not rec.trangthai_dscc:
                            rec.write({'trangthai_dscc': 'xem_bc',
                                       'thamchieu_dscc': 'cc_ca'})
                            xet_bc = self.env['bao.cao'].search([('name_bc', '=', rec.name_dscc.id),
                                                                 ('ngay_bd_bc', '=', self.thoigian + timedelta(days=1))])
                            if xet_bc:
                                for xet in xet_bc:
                                    val = {
                                            'name_bc': rec.name_dscc.id,
                                            'ngay_bd_bc': self.thoigian,
                                            'ngay_kt_bc': self.thoigian + timedelta(days=1),
                                            'ca_lam_viec_bc': clv.name_clv.id,
                                            'giora_bc': xet.giora_bc,
                                            'thamchieu_bc': 'no_data_vao'
                                            }
                                    bc_val = []
                                    bc_val.append([0, 0, val])
                                    #... thì tập hợp lại và ghi ra 'Báo Cáo' record mới có trạng thái : no_data_vao
                                    self.write({'baocao_kn_chamcong': bc_val})
                                    #Đồng thời, xóa record cũ (ngày 8) trước đó đi
                                    xet.unlink()
                            #Nếu ko '=' (ko tìm thấy)...
                            else:
                                val = {
                                        'name_bc': rec.name_dscc.id,
                                        'ngay_bd_bc': self.thoigian,
                                        'ngay_kt_bc': self.thoigian + timedelta(days=1),
                                        'ca_lam_viec_bc': clv.name_clv.id,
                                        'thamchieu_bc': 'no_data_vao'
                                        }
                                bc_val = []
                                bc_val.append([0, 0, val])
                                #... thì in ra record mới ở 'Báo Cáo' có trạng thái: no_data
                                self.write({'baocao_kn_chamcong': bc_val})
                        else:
                            #Xét trường hợp có record của nv ở 'Báo Cáo' trước.
                            #VD: Ca đêm giờ vào ngày 7, giờ ra ngày 8. Khi chấm công, nhân sự chọn chấm công ngày 8 trước (ko theo thứ tự)
                            lich_su = self.env['ls.chamcong'].search([('name', '=', rec.name_dscc.id),
                                                                      ('ngay_kt_lscc', '=', self.thoigian + timedelta(days=1))])
                            if lich_su:
                                x = []
                                for ls in lich_su:
                                    bao_cao = self.env['bao.cao'].search([('name_bc', '=', ls.name.id),
                                                                          ('ngay_bd_bc', '=', ls.ngay_kt_lscc)])
                                    #Nếu record của nv ca đêm ngày 7 '=' với record ngày 8
                                    if bao_cao:
                                        x = ls
                                        rec.write({'thamchieu_dscc': 'cc_ca'})
                                        for bc in bao_cao:
                                            ca_lam_viec = self.env['ca.lamviec'].search([('name_clv', '=', ls.ca_lam_viec_lscc.id)])
                                            for clv in ca_lam_viec:
                                                if x.time1_lscc <= clv.giovao2:
                                                    #chỉ cần xét giờ ra của 'Báo Cáo'
                                                    if bc.giora_bc >= clv.giora1:
                                                        val = {
                                                                'name': bc.name_bc.id,
                                                                'ngay_bd_lscc': self.thoigian,
                                                                'ngay_kt_lscc': bc.ngay_bd_bc,
                                                                'ca_lam_viec_lscc': ls.ca_lam_viec_lscc.id,
                                                                'time1_lscc': x.time1_lscc,
                                                                'time2_lscc': bc.giora_bc,
                                                                'ngaycong': 1
                                                                }
                                                        list_val = []
                                                        list_val.append([0, 0, val])
                                                        self.write({'lscc_kn_chamcong': list_val})
                                                        du_lieu1 = self.env['du.lieu'].search([('name_dl', '=', ls.name.id),
                                                                                               ('thoigian_dl', '=', self.thoigian),
                                                                                               ('state', '=', 'tiepnhan_dl')])
                                                        for z in du_lieu1:
                                                            z.write({'state': 'hoantat_dl'})
                                                        du_lieu2 = self.env['du.lieu'].search([('name_dl', '=', ls.name.id),
                                                                                               ('thoigian_dl', '=', self.thoigian + timedelta(days=1)),
                                                                                               ('state', '=', 'tiepnhan_dl')])
                                                        for i in du_lieu2:
                                                            i.write({'state': 'hoantat_dl'})
                                                        #xóa record ở 'Báo Cáo' ngày 8
                                                        bc.unlink()
                                                        #Sau khi tạo record mới vời đầy đủ giờ vào, giờ ra, xóa record ở 'Lịch Sử Chấm Công' ngày 7
                                                        ls.unlink()
                                                    else:
                                                        val = {
                                                                'name': bc.name_bc.id,
                                                                'ngay_bd_lscc': self.thoigian,
                                                                'ngay_kt_lscc': bc.ngay_bd_bc,
                                                                'ca_lam_viec_lscc': ls.ca_lam_viec_lscc.id,
                                                                'time1_lscc': x.time1_lscc,
                                                                'time2_lscc': bc.giora_bc,
                                                                'ngaycong': 0.5,
                                                                'thamchieu_lscc': 'early'
                                                                }
                                                        list_val = []
                                                        list_val.append([0, 0, val])
                                                        self.write({'lscc_kn_chamcong': list_val})
                                                        du_lieu1 = self.env['du.lieu'].search([('name_dl', '=', ls.name.id),
                                                                                               ('thoigian_dl', '=', self.thoigian),
                                                                                               ('state', '=', 'tiepnhan_dl')])
                                                        for z in du_lieu1:
                                                            z.write({'state': 'hoantat_dl'})
                                                        du_lieu2 = self.env['du.lieu'].search([('name_dl', '=', ls.name.id),
                                                                                               ('thoigian_dl', '=', self.thoigian + timedelta(days=1)),
                                                                                               ('state', '=', 'tiepnhan_dl')])
                                                        for i in du_lieu2:
                                                            i.write({'state': 'hoantat_dl'})
                                                        bc.unlink()
                                                        ls.unlink()
                                                else:
                                                    if bc.giora_bc >= clv.giora1:
                                                        val = {
                                                                'name': bc.name_bc.id,
                                                                'ngay_bd_lscc': self.thoigian,
                                                                'ngay_kt_lscc': bc.ngay_bd_bc,
                                                                'ca_lam_viec_lscc': ls.ca_lam_viec_lscc.id,
                                                                'time1_lscc': x.time1_lscc,
                                                                'time2_lscc': bc.giora_bc,
                                                                'ngaycong': 0.5,
                                                                'thamchieu_lscc': 'late'
                                                                }
                                                        list_val = []
                                                        list_val.append([0, 0, val])
                                                        self.write({'lscc_kn_chamcong': list_val})
                                                        du_lieu1 = self.env['du.lieu'].search([('name_dl', '=', ls.name.id),
                                                                                               ('thoigian_dl', '=', self.thoigian),
                                                                                               ('state', '=', 'tiepnhan_dl')])
                                                        for z in du_lieu1:
                                                            z.write({'state': 'hoantat_dl'})
                                                        du_lieu2 = self.env['du.lieu'].search([('name_dl', '=', ls.name.id),
                                                                                               ('thoigian_dl', '=', self.thoigian + timedelta(days=1)),
                                                                                               ('state', '=', 'tiepnhan_dl')])
                                                        for i in du_lieu2:
                                                            i.write({'state': 'hoantat_dl'})
                                                        bc.unlink()
                                                        ls.unlink()
                                                    else:
                                                        val = {
                                                                'name': bc.name_bc.id,
                                                                'ngay_bd_lscc': self.thoigian,
                                                                'ngay_kt_lscc': bc.ngay_bd_bc,
                                                                'ca_lam_viec_lscc': ls.ca_lam_viec_lscc.id,
                                                                'time1_lscc': x.time1_lscc,
                                                                'time2_lscc': bc.giora_bc,
                                                                'ngaycong': 0,
                                                                'thamchieu_lscc': 'late_early'
                                                                }
                                                        list_val = []
                                                        list_val.append([0, 0, val])
                                                        self.write({'lscc_kn_chamcong': list_val})
                                                        du_lieu1 = self.env['du.lieu'].search([('name_dl', '=', ls.name.id),
                                                                                               ('thoigian_dl', '=', self.thoigian),
                                                                                               ('state', '=', 'tiepnhan_dl')])
                                                        for z in du_lieu1:
                                                            z.write({'state': 'hoantat_dl'})
                                                        du_lieu2 = self.env['du.lieu'].search([('name_dl', '=', ls.name.id),
                                                                                               ('thoigian_dl', '=', self.thoigian + timedelta(days=1)),
                                                                                               ('state', '=', 'tiepnhan_dl')])
                                                        for i in du_lieu2:
                                                            i.write({'state': 'hoantat_dl'})
                                                        bc.unlink()
                                                        ls.unlink()
                                    else:
                                        #Nếu record ca đêm ngày 7 không '=' (không tìm thấy) record ngày 8
                                        #thì ghi trạng thái của record ngày 7 là: 'Chờ dữ liệu giờ ra'
                                        ls.write({'thamchieu_lscc': 'chogiora'})
                                        rec.write({'thamchieu_dscc': 'cc_ca'})

        #XÉT CÁC RECORD của model 'Dữ Liệu' CÓ 'state' = 'Rỗng' (ngoài vòng lặp For)
        
        #Note: Ca đêm sẽ không được nghỉ phép 0.5 ngày
        ngoai_dscc = self.env["du.lieu"].search([('thoigian_dl', '=', self.thoigian),
                                                 ('state', '=', False)])
        a = []
        b = []
        c = []
        d = []
        e = []
        f = []
        g = []
        h = []
        for ngoai in ngoai_dscc:
            tim_trong_lscc = self.env["ls.chamcong"].search([('name', '=', ngoai.name_dl.id),
                                                             ('ca_lam_viec_lscc', '=', self.ca_lam_viec.id),
                                                             ('ngay_kt_lscc', '=', ngoai.thoigian_dl)])
            if tim_trong_lscc:
                #Khai báo biến 'giatri': Rỗng ở ngoài vòng lặp
                giatri = []
                for tim in tim_trong_lscc:
                    tim_clv = self.env["ca.lamviec"].search([('name_clv', '=', tim.ca_lam_viec_lscc.id)])
                    for line in tim_clv:
                        giatri = tim
                        #Xét giờ vào của record ngày này:
                        if giatri.time1_lscc <= line.giovao2:
                            #Xét giờ ra của record ngày kia
                            if ngoai.max_time1 >= ngoai.max_time2:
                                if ngoai.max_time1 >= line.giora1:
                                    a = ngoai
                                    break
                                else:
                                    b = ngoai
                                    break
                            else:
                                if ngoai.max_time2 >= line.giora1:
                                    c = ngoai
                                    break
                                else:
                                    d = ngoai
                                    break
                        else:
                            #Xét giờ ra của record ngày kia
                            if ngoai.max_time1 >= ngoai.max_time2:
                                if ngoai.max_time1 >= line.giora1:
                                    e = ngoai
                                    break
                                else:
                                    f = ngoai
                                    break
                            else:
                                if ngoai.max_time2 >= line.giora1:
                                    g = ngoai
                                    break
                                else:
                                    h = ngoai
                                    break
            #else:
            #    b_c = self.env['bao.cao'].search([('ngay_kt_bc', '=', self.thoigian),
            #                                      ('ca_lam_viec_bc', '=', self.ca_lam_viec.id)])
            #    if b_c:
            #        for bc in b_c:
                        
                #raise Warning ("Ngày hoặc Ca làm việc đang chọn không có Dữ Liệu 'Giờ Vào', hoặc không có trong 'Lịch Làm Việc'.\nVui lòng kiểm tra lại ! ")
                #Nếu không thỏa đk trong biến 'tim_trong_lscc', (có thể do nhân sự chấm công không theo thứ tự ngày) 
                #Thì record đó hoặc không có trong 'Lịch Làm Việc', hoặc không có data Giờ Vào (Ca đêm)
                #Do các record này còn nằm trong vòng lặp của 'Danh Sách Chấm Công'
                #Nên các record này sẽ lần lượt được so sánh với Từng Record của 'Danh Sách Chấm Công'
                #Để tránh lặp lại theo vòng lặp, xét đk:
                #Chỉ in ra các record có tên, ngày và state ='False'
                #Vậy theo vòng lặp, Nếu các record có state ='tiepnhan_dl' => không in ra 'Báo Cáo'
                #xet_dl = self.env['du.lieu'].search([('name_dl', '=', ngoai.name_dl.id),
                #                                     ('thoigian_dl', '=', self.thoigian),
                #                                     ('state', '=', False)])
                #i = []
                #j = []
                #k = []
                #l = []
                #for x in xet_dl:
                    #Do 1 user có thể có nhiều record data chấm công (quét nhiều lần)
                #    nhieu_record = self.env['du.lieu'].search([('name_dl', '=', x.name_dl.id),
                #                                               ('thoigian_dl', '=', x.thoigian_dl),
                #                                               ('state', '=', False)])
                #    if nhieu_record:
                #        for nhieu in nhieu_record:
                            #Đặt nhiều record của 1 nv về trạng thái = 'Ghi Nhận'
                #            nhieu.write({'state': 'ghinhan_dl'})
                    #if x.max_time1 >= x.max_time2:
                        #VD: max_time1 = 7.30 <= max.time1 + 0.05 = 7.35
                        #if x.max_time1 <= x.min_time1 + 0.05:
                            #=> Là ca đêm nên: chỉ lấy max_time1 làm giờ ra
                            #i = x
                            #break
                        #else:
                            #Ngược lại, Nếu '>': sẽ lấy min_time1 và max_time1 làm giờ vào giờ ra ở 'Báo Cáo'
                            #j = x
                            #break
                    #else:
                    #    if x.max_time2 <= x.min_time1 + 0.05:
                    #        k = x
                    #        break
                    #    else:
                    #        l = x
                    #        break
                #if i:
                    #Trước khi in ra 'Báo Cáo', kt xem record ngày 8 có '=' (tìm thấy) record ngày 7 ko?
                    #xet_bc = self.env['bao.cao'].search([('name_bc', '=', i.name_dl.id),
                    #                                     ('ngay_kt_bc', '=', self.thoigian)])
                    #Nếu tìm thấy...
                    #if xet_bc:
                    #    val = {
                    #            'name_bc': i.name_dl.id,
                    #            'ngay_bd_bc': self.thoigian - timedelta(days=1),
                    #            'ngay_kt_bc': self.thoigian,
                    #            'giora_bc': i.max_time1,
                    #            'thamchieu_bc': 'no_data_vao'
                    #            }
                    #    bc_val = []
                    #    bc_val.append([0, 0, val])
                        #... in ra 'Báo Cáo' với đúng ngày bd và kt báo cáo 
                    #    self.write({'baocao_kn_chamcong': bc_val})
                    #else:
                        #Nếu ko...
                    #    val = {
                    #            'name_bc': i.name_dl.id,
                    #            'ngay_bd_bc': self.thoigian,
                    #            'ngay_kt_bc': self.thoigian,
                    #            'giora_bc': i.max_time1,
                    #            'thamchieu_bc': 'no_data_vao'
                    #            }
                    #    bc_val = []
                    #    bc_val.append([0, 0, val])
                        #... thì in ra 'Báo Cáo' với ngày mặc định cho ngày bd và kt
                    #    self.write({'baocao_kn_chamcong': bc_val})        
                #if j:
                    #xet_bc = self.env['bao.cao'].search([('name_bc', '=', j.name_dl.id),
                    #                                     ('ngay_kt_bc', '=', self.thoigian)])
                    #if xet_bc:
                    #    val = {
                    #            'name_bc': j.name_dl.id,
                    #            'ngay_bd_bc': self.thoigian - timedelta(days=1),
                    #            'ngay_kt_bc': self.thoigian,
                    #            'giora_bc': j.max_time1,
                    #            'thamchieu_bc': 'no_data_vao'
                    #            }
                    #    bc_val = []
                    #    bc_val.append([0, 0, val])
                    #    self.write({'baocao_kn_ccn': bc_val})
                    #else:
                    #    val = {
                    #            'name_bc': j.name_dl.id,
                    #            'ngay_bd_bc': self.thoigian,
                    #            'ngay_kt_bc': self.thoigian,
                    #            'giovao_bc': j.min_time1,
                    #            'giora_bc': j.max_time1,
                    #            'thamchieu_bc': 'no_pl'
                    #            }
                    #    bc_val = []
                    #    bc_val.append([0, 0, val])
                    #    self.write({'baocao_kn_chamcong': bc_val})    
                #if k:
                #    xet_bc = self.env['bao.cao'].search([('name_bc', '=', k.name_dl.id),
                #                                         ('ngay_kt_bc', '=', self.thoigian)])
                #    if xet_bc:
                #        val = {
                #                'name_bc': k.name_dl.id,
                #                'ngay_bd_bc': self.thoigian - timedelta(days=1),
                #                'ngay_kt_bc': self.thoigian,
                #                'giora_bc': k.max_time2,
                #                'thamchieu_bc': 'no_data_vao'
                #                }
                #        bc_val = []
                #        bc_val.append([0, 0, val])
                #        self.write({'baocao_kn_chamcong': bc_val})
                #    else:
                #        val = {
                #                'name_bc': k.name_dl.id,
                #                'ngay_bd_bc': self.thoigian,
                #                'ngay_kt_bc': self.thoigian,
                #                'giora_bc': k.max_time2,
                #                'thamchieu_bc': 'no_data_vao'
                #                }
                #        bc_val = []
                #        bc_val.append([0, 0, val])
                #        self.write({'baocao_kn_chamcong': bc_val})
                #if l:
                #    xet_bc = self.env['bao.cao'].search([('name_bc', '=', l.name_dl.id),
                #                                         ('ngay_kt_bc', '=', self.thoigian)])
                #    if xet_bc:
                #        val = {
                #                'name_bc': l.name_dl.id,
                #                'ngay_bd_bc': self.thoigian - timedelta(days=1),
                #                'ngay_kt_bc': self.thoigian,
                #                'giora_bc': l.max_time2,
                #                'thamchieu_bc': 'no_data_vao'
                #                }
                #        bc_val = []
                #        bc_val.append([0, 0, val])
                #        self.write({'baocao_kn_ccn': bc_val})
                #    else:
                #        val = {
                #                'name_bc': l.name_dl.id,
                #                'ngay_bd_bc': self.thoigian,
                #                'ngay_kt_bc': self.thoigian,
                #                'giovao_bc': l.min_time1,
                #                'giora_bc': l.max_time2,
                #                'thamchieu_bc': 'no_pl'
                #                }
                #        bc_val = []
                #        bc_val.append([0, 0, val])
                #        self.write({'baocao_kn_chamcong': bc_val}) 
        if a:
            val = {
                    'name': a.name_dl.id,
                    'ngay_bd_lscc': self.thoigian - timedelta(days=1),
                    'ngay_kt_lscc': self.thoigian,
                    'ca_lam_viec_lscc': tim.ca_lam_viec_lscc.id,
                    #Lấy giá trị giờ vào trong time1_lscc của record thỏa đk trong domain vào ngày này (*)
                    #gắn vào field time1_lscc của record vào ngày kia để tạo record mới ở ls.chamcong với đầy đủ giờ vào/ra
                    'time1_lscc': giatri.time1_lscc,
                    'time2_lscc': a.max_time1,
                    'ngaycong': 1
                    }
            list_val = []
            list_val.append([0, 0, val])
            self.write({'lscc_kn_chamcong': list_val})
            #Đồng thời, XÓA luôn record (*)
            tim.unlink()
            #Sau khi hoàn tất chấm công, chuyển trạng thái của record trong model du_lieu.py vào ngày này (VD: ngày vào: 7)
            xet_dl1 = self.env["du.lieu"].search([('thoigian_dl', '=', self.thoigian - timedelta(days=1)),
                                                  ('state', '=', 'tiepnhan_dl')])
            if xet_dl1:
                for xet in xet_dl1:
                    xet.write({'state': 'hoantat_dl'})
            #Sau khi hoàn tất chấm công, chuyển trạng thái của record trong model du_lieu.py vào ngày kia (VD: ngày ra: 8)
            #Xét 1 Record (hoặc nhiều Record) của 1 user có cùng tên, cùng ngày và state = 'Rỗng'
            xet_dl2 = self.env["du.lieu"].search([('thoigian_dl', '=', self.thoigian),
                                                  ('state', '=', False),
                                                  ('name_dl', '=', a.name_dl.id)])
            if xet_dl2:
                for xet in xet_dl2:
                    xet.write({'state': 'hoantat_dl'})
        if b:
            val = {
                    'name': b.name_dl.id,
                    'ngay_bd_lscc': self.thoigian - timedelta(days=1),
                    'ngay_kt_lscc': self.thoigian,
                    'ca_lam_viec_lscc': tim.ca_lam_viec_lscc.id,
                    #Lấy giá trị giờ vào trong time1_lscc của record thỏa đk trong domain vào ngày này (*)
                    #gắn vào field time1_lscc của record vào ngày kia để tạo record mới ở ls.chamcong với đầy đủ giờ vào/ra
                    'time1_lscc': giatri.time1_lscc,
                    'time2_lscc': b.max_time1,
                    'ngaycong': 0.5,
                    'thamchieu_lscc': 'early'
                    }
            list_val = []
            list_val.append([0, 0, val])
            self.write({'lscc_kn_chamcong': list_val})
            #Đồng thời, XÓA luôn record (*)
            tim.unlink()
            #Sau khi hoàn tất chấm công, chuyển trạng thái của record trong model du_lieu.py vào ngày này (VD: ngày vào: 7)
            xet_dl3 = self.env["du.lieu"].search([('thoigian_dl', '=', self.thoigian - timedelta(days=1)),
                                                  ('state', '=', 'tiepnhan_dl')])
            if xet_dl3:
                for xet in xet_dl3:
                    xet.write({'state': 'hoantat_dl'})
            #Sau khi hoàn tất chấm công, chuyển trạng thái của record trong model du_lieu.py vào ngày kia (VD: ngày ra: 8)
            #Xét 1 Record (hoặc nhiều Record) của 1 user có cùng tên, cùng ngày và state = 'Rỗng'
            xet_dl4 = self.env["du.lieu"].search([('thoigian_dl', '=', self.thoigian),
                                                  ('state', '=', False),
                                                  ('name_dl', '=', b.name_dl.id)])
            if xet_dl4:
                for xet in xet_dl2:
                    xet.write({'state': 'hoantat_dl'})
        if c:
            val = {
                    'name': c.name_dl.id,
                    'ngay_bd_lscc': self.thoigian - timedelta(days=1),
                    'ngay_kt_lscc': self.thoigian,
                    'ca_lam_viec_lscc': tim.ca_lam_viec_lscc.id,
                    'time1_lscc': giatri.time1_lscc,
                    'time2_lscc': c.max_time2,
                    'ngaycong': 1
                    }
            list_val = []
            list_val.append([0, 0, val])
            self.write({'lscc_kn_chamcong': list_val})
            tim.unlink()
            xet_dl5 = self.env["du.lieu"].search([('thoigian_dl', '=', self.thoigian - timedelta(days=1)),
                                                  ('state', '=', 'tiepnhan_dl')])
            if xet_dl5:
                for xet in xet_dl5:
                    xet.write({'state': 'hoantat_dl'})
            xet_dl6 = self.env["du.lieu"].search([('thoigian_dl', '=', self.thoigian),
                                                  ('state', '=', False),
                                                  ('name_dl', '=', c.name_dl.id)])
            if xet_dl6:
                for xet in xet_dl6:
                    xet.write({'state': 'hoantat_dl'})
        if d:
            val = {
                    'name': d.name_dl.id,
                    'ngay_bd_lscc': self.thoigian - timedelta(days=1),
                    'ngay_kt_lscc': self.thoigian,
                    'ca_lam_viec_lscc': tim.ca_lam_viec_lscc.id,
                    'time1_lscc': giatri.time1_lscc,
                    'time2_lscc': d.max_time2,
                    'ngaycong': 1
                    }
            list_val = []
            list_val.append([0, 0, val])
            self.write({'lscc_kn_chamcong': list_val})
            tim.unlink()
            xet_dl7 = self.env["du.lieu"].search([('thoigian_dl', '=', self.thoigian - timedelta(days=1)),
                                                  ('state', '=', 'tiepnhan_dl')])
            if xet_dl7:
                for xet in xet_dl7:
                    xet.write({'state': 'hoantat_dl'})
            xet_dl8 = self.env["du.lieu"].search([('thoigian_dl', '=', self.thoigian),
                                                  ('state', '=', False),
                                                  ('name_dl', '=', d.name_dl.id)])
            if xet_dl8:
                for xet in xet_dl8:
                    xet.write({'state': 'hoantat_dl'})
        if e:
            val = {
                    'name': e.name_dl.id,
                    'ngay_bd_lscc': self.thoigian - timedelta(days=1),
                    'ngay_kt_lscc': self.thoigian,
                    'ca_lam_viec_lscc': tim.ca_lam_viec_lscc.id,
                    'time1_lscc': giatri.time1_lscc,
                    'time2_lscc': e.max_time1,
                    'ngaycong': 0.5,
                    'thamchieu_lscc': 'late'
                    }
            list_val = []
            list_val.append([0, 0, val])
            self.write({'lscc_kn_chamcong': list_val})
            tim.unlink()
            xet_dl9 = self.env["du.lieu"].search([('thoigian_dl', '=', self.thoigian - timedelta(days=1)),
                                                  ('state', '=', 'tiepnhan_dl')])
            if xet_dl9:
                for xet in xet_dl9:
                    xet.write({'state': 'hoantat_dl'})
            xet_dl10 = self.env["du.lieu"].search([('thoigian_dl', '=', self.thoigian),
                                                   ('state', '=', False),
                                                   ('name_dl', '=', e.name_dl.id)])
            if xet_dl10:
                for xet in xet_dl10:
                    xet.write({'state': 'hoantat_dl'})
        if f:
            val = {
                    'name': f.name_dl.id,
                    'ngay_bd_lscc': self.thoigian - timedelta(days=1),
                    'ngay_kt_lscc': self.thoigian,
                    'ca_lam_viec_lscc': tim.ca_lam_viec_lscc.id,
                    'time1_lscc': giatri.time1_lscc,
                    'time2_lscc': f.max_time1,
                    'ngaycong': 0,
                    'thamchieu_lscc': 'late_early'
                    }
            list_val = []
            list_val.append([0, 0, val])
            self.write({'lscc_kn_chamcong': list_val})
            tim.unlink()
            xet_dl11 = self.env["du.lieu"].search([('thoigian_dl', '=', self.thoigian - timedelta(days=1)),
                                                   ('state', '=', 'tiepnhan_dl')])
            if xet_dl11:
                for xet in xet_dl11:
                    xet.write({'state': 'hoantat_dl'})
            xet_dl12 = self.env["du.lieu"].search([('thoigian_dl', '=', self.thoigian),
                                                   ('state', '=', False),
                                                   ('name_dl', '=', f.name_dl.id)])
            if xet_dl12:
                for xet in xet_dl12:
                    xet.write({'state': 'hoantat_dl'})
        if g:
            val = {
                    'name': g.name_dl.id,
                    'ngay_bd_lscc': self.thoigian - timedelta(days=1),
                    'ngay_kt_lscc': self.thoigian,
                    'ca_lam_viec_lscc': tim.ca_lam_viec_lscc.id,
                    'time1_lscc': giatri.time1_lscc,
                    'time2_lscc': g.max_time2,
                    'ngaycong': 0.5,
                    'thamchieu_lscc': 'late'
                    }
            list_val = []
            list_val.append([0, 0, val])
            self.write({'lscc_kn_chamcong': list_val})
            tim.unlink()
            xet_dl13 = self.env["du.lieu"].search([('thoigian_dl', '=', self.thoigian - timedelta(days=1)),
                                                   ('state', '=', 'tiepnhan_dl')])
            if xet_dl13:
                for xet in xet_dl13:
                    xet.write({'state': 'hoantat_dl'})
            xet_dl14 = self.env["du.lieu"].search([('thoigian_dl', '=', self.thoigian),
                                                   ('state', '=', False),
                                                   ('name_dl', '=', g.name_dl.id)])
            if xet_dl14:
                for xet in xet_dl14:
                    xet.write({'state': 'hoantat_dl'})
        if h:
            val = {
                    'name': h.name_dl.id,
                    'ngay_bd_lscc': self.thoigian - timedelta(days=1),
                    'ngay_kt_lscc': self.thoigian,
                    'ca_lam_viec_lscc': tim.ca_lam_viec_lscc.id,
                    'time1_lscc': giatri.time1_lscc,
                    'time2_lscc': h.max_time2,
                    'ngaycong': 0,
                    'thamchieu_lscc': 'late_early'
                    }
            list_val = []
            list_val.append([0, 0, val])
            self.write({'lscc_kn_chamcong': list_val})
            tim.unlink()
            xet_dl15 = self.env["du.lieu"].search([('thoigian_dl', '=', self.thoigian - timedelta(days=1)),
                                                   ('state', '=', 'tiepnhan_dl')])
            if xet_dl15:
                for xet in xet_dl15:
                    xet.write({'state': 'hoantat_dl'})
            xet_dl16 = self.env["du.lieu"].search([('thoigian_dl', '=', self.thoigian),
                                                   ('state', '=', False),
                                                   ('name_dl', '=', h.name_dl.id)])
            if xet_dl16:
                for xet in xet_dl16:
                    xet.write({'state': 'hoantat_dl'})
                              
        #Sau khi hoàn tất chấm công, thì đưa trạng thái của cham_cong.py về rỗng ' '
        self.trangthai_cc = "hoantat_ca"
        """Tạo hiệu ứng popup Thông Báo khi chuyển trạng thái 'chamcong' """
        self.sudo().write({
        'state': 'chamcong'
            })
        return {
            'effect': {
            'fadeout': 'fast',
            'message': 'HOÀN TẤT',
            'type': 'rainbow_man',
                }
            }             
    
    def veduthao(self):
        #Khi về dự thảo, thì record tạo ra từ 'Xác Nhận' vẫn được save với trạng thái 'Chờ Xác Nhận'. 
        #Không cần xóa record.
        self.trangthai_cc = 'choxacnhan'
        self.state = "moi"
        return True
        
    def huy(self):
        for rec in self:
            # Đưa các record thỏa điều kiện ở model du_lieu.py (tab Dữ Liệu) về trạng thái ban đầu:
            for line in rec.lscc_kn_chamcong:
                xoa_trangthai_dulieu = self.env["du.lieu"].search([('thoigian_dl', '=', rec.thoigian),
                                                                   ('ca_lam_viec_dl', '=', rec.ca_lam_viec.id)])
                if xoa_trangthai_dulieu:
                    xoa_trangthai_dulieu.write({'state': False,
                                                'ca_lam_viec_dl': False})                
                #xóa rec trong model ls_chamcong.py
                line.unlink()
            # xóa luôn record chấm công theo Ca trong model 'cham_cong.py'
            rec.unlink()            
            #Sau khi xóa, trở lại form view với trạng thái ban đầu
            return {
                'view_mode': 'form',
                'res_model': 'cham.cong',
                #Dùng 'main' thay 'current' hợp lý hơn vì đã xóa record
                'target': 'main',
                'type': 'ir.actions.act_window',
                }
     
#-----------------------------------------
# Chấm Công theo Ngày
#-----------------------------------------
class ChamCongNgay(models.Model):
    _name = "chamcong.ngay"
    _description = "Dựa vào Dữ liệu thực tế trong ngày, sau đó so sánh với Lịch làm việc tương ứng để Chấm Công"
     #Thể hiện giá trị của 'ngay' thay cho name (mặc định) sau khi tạo
    _rec_name = "ngay"
    
    ngay = fields.Date('Ngày Làm Việc',
                                        states={
                                                'daduocxacnhan_ccn': [('readonly', True)],
                                                'daduyet_ccn': [('readonly', True)],
                                                'chamcong_ccn': [('readonly', True)]
                                                })
    
    thamchieu_ccn = fields.Selection([('xoa_tl', 'Xóa Trùng Lặp')], string='Tham Chiếu')
    
    trangthai_ccn =fields.Selection([
                ('chuaxong_ccn', 'Chưa Chấm Công'),
                ('chochapthuan_ccn', 'Chưa Chấp Thuận'),
                ('choxacnhan_ccn', 'Chưa Xác Nhận'),
                ('hoantat_ccn', 'Hoàn Tất'),
                ], string="Trạng thái")    
    #Tạo status bar
    state = fields.Selection([
            ('moi_ccn', 'DỰ THẢO'),
            ('daduocxacnhan_ccn', 'ĐÃ ĐƯỢC XÁC NHẬN'),
            ('daduyet_ccn', 'ĐÃ DUYỆT'),
            ('chamcong_ccn', 'HOÀN TẤT'),
            ],default='moi_ccn')
    
    lscc_kn_ccn = fields.One2many('ls.chamcong', 'ccn_kn_lscc', string="Danh Sách Chấm Công")    
    baocao_kn_ccn = fields.One2many('bao.cao', 'ccn_kn_bc', string="Báo Cáo")
    dscc_kn_cc_ngay = fields.One2many('ds.chamcong', 'ccn_kn_dscc', string="Lịch Làm Việc")
    
    @api.onchange('ngay')
    def onchange_get_data(self):
        #Kiểm tra xem tab 'Dữ Liệu' có data trước không (bắt buộc). Nếu chưa có, raise Thông Báo
        warning_dulieu = self.env["du.lieu"].search([])
        res = {}
        if not warning_dulieu:            
            #Note: thông báo bằng 'warning' dạng này chỉ được dùng với onchange
            res['warning'] = {'title': _('Thông Báo'),
                             'message': _('Không có Dữ liệu chấm công.\nVui lòng kiểm tra lại ở mục Dữ liệu!')}
            return res
        
        for rec in self:
            rec.dscc_kn_cc_ngay = False
            #khai báo các biến đang rỗng ở lúc đầu
            lines = []     
            #Nếu field 'ngay' trong model 'chamcong.ngay' có data:
            if rec.ngay:
            #KHÔNG THỂ so sánh field 'ngay' là "date field" với field 'start_datetime' là "datetime field" trong model planning.slot
            #Để so sánh được, dùng combine để kết hợp biến 'time_ccn' với 'date_ccn' => để biến field 'ngay' thành datetime field
            #Tham khảo: https://www.kdnuggets.com/2019/06/how-use-datetime.html
                gio = datetime.min.time() #min.time : nữa đêm
                ngay = rec.ngay
                list_dl = self.env["planning.slot"].search([('start_datetime','>', datetime.combine(ngay,gio)),
                                                            #Dùng timedelta(days=1): thêm dư 1 ngày để tìm được ngày hiện tại
                                                            ('start_datetime', '<', ngay + timedelta(days=1))])
                for a in list_dl:
                    vals = {
                        'name_dscc': a.employee_id.id,
                        'ca_lam_viec_dscc': a.role_id.id,
                        'thoigian_bd_dscc': a.start_datetime,
                        'thoigian_kt_dscc': a.end_datetime,
                        }
                    lines.append((0, 0, vals))
                #Ghi các data của lines vào các field tương ứng của field one2many: dscc_kn_cc_ngay
                rec.dscc_kn_cc_ngay = lines

    def xacnhan_ngay(self):
        if not self.ngay:
            self.trangthai_ccn = "choxacnhan_ccn"
            message = {
               'type': 'ir.actions.client',
               'tag': 'display_notification',
               'params': {
                   'title': _('Thông Báo'),
                   'message': 'Bạn chưa chọn Ngày làm việc.\nVui lòng chọn để tiếp tục!',
                   'sticky': False,
                }
            }
            return message

        else:   
            self.trangthai_ccn = "chochapthuan_ccn"
            self.state = "daduocxacnhan_ccn"                       
        return True
    
    def chapthuan_ngay(self):
        for line in self.dscc_kn_cc_ngay:
            if not line.trangthai_dscc:
                duplicate_lscc_ngay = self.env["ls.chamcong"].search([('ngay_bd_lscc', '=', self.ngay),
                                                                      ('ca_lam_viec_lscc', '=', line.ca_lam_viec_dscc.id),
                                                                      ('name', '=', line.name_dscc.id)])
                #Nếu có duplicate ở 'Lịch Sử Chấm Công'
                if duplicate_lscc_ngay:
                    return {
                            'name': "Thông Báo",
                            'view_mode': 'form',
                            'res_model': 'tbb.lscc',
                            'context': {'default_ngay_tbb': self.ngay},
                            'target': 'new',
                            'type': 'ir.actions.act_window',
                            }
                else:
                    #Nếu không, xét tiếp duplicate ở 'Báo Cáo'
                    duplicate_baocao = self.env['bao.cao'].search([('ngay_bd_bc', '=', self.ngay),
                                                                   ('ca_lam_viec_bc', '=', line.ca_lam_viec_dscc.id),
                                                                   ('name_bc', '=', line.name_dscc.id)])
                    if duplicate_baocao:
                        return {
                                'name': "Thông Báo",
                                'view_mode': 'form',
                                'res_model': 'tbb.lscc',
                                'context': {'default_ngay_tbb': self.ngay},
                                'target': 'new',
                                'type': 'ir.actions.act_window',
                                }
                    else:
                        #Do 1 nv có thể quét nhiều lần trên máy chấm công
                        #1 lần quét sẽ tạo 1 record và data sẽ đưa vào field time1 (1 record có 2 field time1 và time2 chứa data)
                        #Vậy với lần quét thứ 3, sẽ tạo record thứ 2 và data được đặt vào field đầu tiên là time1 (mặc định). Tương tự,...
                        #Note: data field time1 chắc chắn >= data field time2
                        #Vậy sẽ tạo nên nhiều DUPLICATE record của nv đó nhưng với data ở time1 và time2 khác nhau
                        list_dulieu = self.env["du.lieu"].search([('name_dl', '=', line.name_dscc.id),
                                                                  ('thoigian_dl', '=', self.ngay)])
                
                        list_calamviec = self.env["ca.lamviec"].search([('name_clv', '=', line.ca_lam_viec_dscc.id)])
                        for clv in list_calamviec:
                            #Để xác định nv có ca làm việc bắt đầu từ ngày này, kết thúc từ ngày kia ko?
                            #Giờ vào từ 17h là ca làm việc qua đêm: lấy dư 16.30
                            if clv.giovao1 <= 16.30: #<= ko làm qua đêm, làm trong ngày
                                #Để lấy 1 record duy nhất với MIN/MAX data từ các Duplicate record của 1 nv
                                #Dùng break để ngắt vòng lặp khi thỏa đk
                                #Khai báo biến rỗng 's t o p q' ở ngoài vòng lặp
                                s = []
                                t = []
                                o = []
                                p = []
                                q = []
                                #'dl' đại diện cho các field của biến recordset: list_dulieu
                                for dl in list_dulieu:
                                    nhieu_record = self.env['du.lieu'].search([('name_dl', '=', dl.name_dl.id),
                                                                               ('thoigian_dl', '=', dl.thoigian_dl),
                                                                               ('state', '=', False)])
                                    if nhieu_record:
                                        for nhieu in nhieu_record:
                                            #Đặt nhiều record của 1 nv về trạng thái = 'Tiếp Nhận'
                                            nhieu.write({'state': 'tiepnhan_dl'})
                                    if dl.max_time1 >= dl.max_time2:
                                        if dl.max_time1 <= clv.giovao2 + 0.1: #giovao2 + 10 phút: nếu <= : coi như không có giờ ra
                                            s = dl
                                            line.write({'trangthai_dscc': 'xacnhan'})
                                            #ngắt vòng lặp khi thỏa đk
                                            break
                                        #nếu > giovao2:
                                        else:
                                            #thì xét nếu max_time1 có >= giora1:
                                            if dl.max_time1 >= clv.giora1:
                                                #Nếu >= giora1, xét tiếp nếu min_time1 có >= giora1: chỉ lấy max_time1 làm giờ ra
                                                if dl.min_time1 >= clv.giora1:
                                                    t = dl
                                                    line.write({'trangthai_dscc': 'xacnhan'})
                                                    break
                                                #Nếu không, 
                                                else:
                                                    #thì xét tiếp nếu min_time1 <= giora1 - 10 phút: lấy min_time1 và max_time1 làm giờ vào và ra
                                                    if dl.min_time1 <= clv.giora1 - 0.1:
                                                        q = dl
                                                        line.write({'trangthai_dscc': 'xacnhan'})
                                                        break
                                                    #Ngược lại,
                                                    else:
                                                        #Nếu min_time1 > giora1 - 0.1: chỉ lấy max_time1 làm giờ ra, coi như ko có giờ vào
                                                        t = dl
                                                        line.write({'trangthai_dscc': 'xacnhan'})
                                                        break
                                            # Nếu max_time1 < clv.giora1:
                                            else:
                                                q = dl
                                                line.write({'trangthai_dscc': 'xacnhan'})
                                                break
                                    else:
                                        if dl.max_time2 <= clv.giovao2 + 0.1:
                                            o = dl
                                            line.write({'trangthai_dscc': 'xacnhan'})
                                            break
                                        else:
                                            p = dl
                                            line.write({'trangthai_dscc': 'xacnhan'})
                                            break
                                #dùng 's' ở ngoài vòng lặp
                                if s:
                                    val_1 = {
                                            'name': line.name_dscc.id,
                                            'ngay_bd_lscc': self.ngay,
                                            'ngay_kt_lscc': self.ngay,
                                            'ca_lam_viec_lscc': line.ca_lam_viec_dscc.id,
                                            'time1_lscc': s.min_time1
                                            }
                                    list_val_1 = []
                                    list_val_1.append([0, 0, val_1])
                                    self.write({'lscc_kn_ccn': list_val_1})
                                if t:
                                    val_2 = {
                                            'name': line.name_dscc.id,
                                            'ngay_bd_lscc': self.ngay,
                                            'ngay_kt_lscc': self.ngay,
                                            'ca_lam_viec_lscc': line.ca_lam_viec_dscc.id,
                                            'time2_lscc': t.max_time1
                                            }
                                    list_val_2 = []
                                    list_val_2.append([0, 0, val_2])
                                    self.write({'lscc_kn_ccn': list_val_2})
                                if q:
                                    val_5 = {
                                            'name': line.name_dscc.id,
                                            'ngay_bd_lscc': self.ngay,
                                            'ngay_kt_lscc': self.ngay,
                                            'ca_lam_viec_lscc': line.ca_lam_viec_dscc.id,
                                            'time1_lscc': q.min_time1,
                                            'time2_lscc': q.max_time1
                                            }
                                    list_val_5 = []
                                    list_val_5.append([0, 0, val_5])
                                    self.write({'lscc_kn_ccn': list_val_5})
                                if o:
                                    val_3 = {
                                            'name': line.name_dscc.id,
                                            'ngay_bd_lscc': self.ngay,
                                            'ngay_kt_lscc': self.ngay,
                                            'ca_lam_viec_lscc': line.ca_lam_viec_dscc.id,
                                            'time1_lscc': o.min_time1,
                                            }
                                    list_val_3 = []
                                    list_val_3.append([0, 0, val_3])
                                    self.write({'lscc_kn_ccn': list_val_3})
                                if p:
                                    val_4 = {
                                            'name': line.name_dscc.id,
                                            'ngay_bd_lscc': self.ngay,
                                            'ngay_kt_lscc': self.ngay,
                                            'ca_lam_viec_lscc': line.ca_lam_viec_dscc.id,
                                            'time1_lscc': p.min_time1,
                                            'time2_lscc': p.max_time2
                                            }
                                    list_val_4 = []
                                    list_val_4.append([0, 0, val_4])
                                    self.write({'lscc_kn_ccn': list_val_4})
                            #có làm qua đêm
                            else:
                                a = []
                                b = []
                                c = []
                                d = []
                                for dl in list_dulieu:
                                    nhieu_record = self.env['du.lieu'].search([('name_dl', '=', dl.name_dl.id),
                                                                               ('thoigian_dl', '=', dl.thoigian_dl),
                                                                               ('state', '=', False)])
                                    if nhieu_record:
                                        for nhieu in nhieu_record:
                                            #Đặt nhiều record của 1 nv về trạng thái = 'Tiếp Nhận'
                                            nhieu.write({'state': 'tiepnhan_dl'})
                                    if dl.max_time1 >= dl.max_time2:
                                        #giovao2 + 10 phút: nếu <= : coi như không có giờ ra
                                        if dl.max_time1 <= clv.giovao2 + 0.1:
                                            a = dl
                                            line.write({'trangthai_dscc': 'xacnhan'})
                                            break
                                        #nếu > : coi như đó là giờ ra
                                        else:
                                            b = dl
                                            line.write({'trangthai_dscc': 'xacnhan'})
                                            break
                                    else:
                                        if dl.max_time2 <= clv.giovao2 + 0.1:
                                            c = dl
                                            line.write({'trangthai_dscc': 'xacnhan'})
                                            break
                                        else:
                                            d = dl
                                            line.write({'trangthai_dscc': 'xacnhan'})
                                            break                          
                                if a:
                                    val_5 = {
                                            'name': line.name_dscc.id,
                                            #ngày bắt đầu là ở thời điểm chọn chấm công
                                            'ngay_bd_lscc': self.ngay,
                                            #có làm qua đêm, nên ngày kết thúc + thêm 1 ngày
                                            'ngay_kt_lscc': self.ngay + timedelta(days=1),
                                            'ca_lam_viec_lscc': line.ca_lam_viec_dscc.id,
                                            #Lấy giờ nhỏ nhất làm giờ vào
                                            'time1_lscc': a.min_time1
                                            }
                                    list_val_5 = []
                                    list_val_5.append([0, 0, val_5])
                                    self.write({'lscc_kn_ccn': list_val_5})
                                if b:
                                    val_6 = {
                                            'name': line.name_dscc.id,
                                            'ngay_bd_lscc': self.ngay,
                                            'ngay_kt_lscc': self.ngay + timedelta(days=1),
                                            'ca_lam_viec_lscc': line.ca_lam_viec_dscc.id,
                                            'time1_lscc': b.min_time1,
                                            #Lấy giờ lớn nhất của time1 làm giờ ra do > clv.giovao2 + 0.1
                                            'time2_lscc': b.max_time1
                                            }
                                    list_val_6 = []
                                    list_val_6.append([0, 0, val_6])
                                    self.write({'lscc_kn_ccn': list_val_6})
                                if c:
                                    val_7 = {
                                            'name': line.name_dscc.id,
                                            'ngay_bd_lscc': self.ngay,
                                            'ngay_kt_lscc': self.ngay + timedelta(days=1),
                                            'ca_lam_viec_lscc': line.ca_lam_viec_dscc.id,
                                            'time1_lscc': c.min_time1,
                                            }
                                    list_val_7 = []
                                    list_val_7.append([0, 0, val_7])
                                    self.write({'lscc_kn_ccn': list_val_7})                    
                                if d:
                                    val_8 = {
                                            'name': line.name_dscc.id,
                                            'ngay_bd_lscc': self.ngay,
                                            'ngay_kt_lscc': self.ngay + timedelta(days=1),
                                            'ca_lam_viec_lscc': line.ca_lam_viec_dscc.id,
                                            'time1_lscc': d.min_time1,
                                            'time2_lscc': d.max_time2,
                                            }
                                    list_val_8 = []
                                    list_val_8.append([0, 0, val_8])
                                    self.write({'lscc_kn_ccn': list_val_8})
                                
        self.trangthai_ccn = "chuaxong_ccn"                        
        self.state = "daduyet_ccn"           
        return True
    
    def chamcong_ngay(self):
        for rec in self.dscc_kn_cc_ngay:
            #Các record bị 'trùng lặp' ở DS chấm công (nếu có) sẽ bị XÓA ở nút 'Chấm Công'
            if rec.trangthai_dscc == 'trunglap':
                rec.unlink()
                self.thamchieu_ccn = 'xoa_tl'
            else:                
                ds_clv = self.env["ca.lamviec"].search([('name_clv', '=', rec.ca_lam_viec_dscc.id)])
                for clv in ds_clv:
                    #Xác định các record thuộc 'Danh Sách Chấm Công' là ca làm trong ngày hay làm qua đêm?
                    if clv.giovao1 <= 16.30:
                        #và chọn record có trạng thái = "Rỗng"...
                        if not rec.trangthai_dscc:
                            #... để ghi vào trạng thái = 'Xác nhận'...
                            rec.write({'trangthai_dscc': 'xem_bc'})
                            values = {
                                        'name_bc': rec.name_dscc.id,
                                        'ngay_bd_bc': self.ngay,
                                        'ngay_kt_bc': self.ngay,
                                        'ca_lam_viec_bc': clv.name_clv.id,
                                        'thamchieu_bc': 'no_data'
                                        }
                            bc_values = []
                            bc_values.append([0, 0, values])
                            #... đồng thời ghi ra 'Báo Cáo' các giá trị của biến 'val'
                            self.write({'baocao_kn_ccn': bc_values})
                        else:
                            ds_lscc = self.env["ls.chamcong"].search([('name', '=', rec.name_dscc.id),
                                                                      ('ca_lam_viec_lscc', '=', rec.ca_lam_viec_dscc.id),
                                                                      #chỉ có clv trong ngày mới có ngay kết thúc = self.ngay, nếu ko là clv qua đêm
                                                                      ('ngay_kt_lscc', '=', self.ngay)])
                            for ds in ds_lscc:
                                if not ds.time1_lscc:
                                    if ds.time2_lscc:
                                        rec.write({'trangthai_dscc': 'xem_bc'})
                                        val = {
                                                'name_bc': ds.name.id,
                                                'ngay_bd_bc': ds.ngay_bd_lscc,
                                                'ngay_kt_bc': ds.ngay_kt_lscc,
                                                'ca_lam_viec_bc': ds.ca_lam_viec_lscc.id,
                                                'giovao_bc': ds.time1_lscc,
                                                'giora_bc': ds.time2_lscc,
                                                'thamchieu_bc': 'no_data_vao'
                                                }
                                        list_bc_val = []
                                        list_bc_val.append([0, 0, val])
                                        self.write({'baocao_kn_ccn': list_bc_val})
                                        #XÓA record này ở 'Lịch Sử Chấm Công', cho user xem ở mục 'Báo Cáo'
                                        ds.unlink()
                                    #else:
                                        #không có time1_lscc:
                                            #không có time2_lscc:
                                                #=> no_data: giống trường hợp trên
                                else:
                                    if ds.time1_lscc <= clv.giovao2:
                                        #Xét tiếp giờ ra. Nếu ko có giờ ra (time2_lscc = False)
                                        if not ds.time2_lscc:
                                            rec.write({'trangthai_dscc': 'xem_bc'})
                                            val_2 = {
                                                        'name_bc': ds.name.id,
                                                        'ngay_bd_bc': ds.ngay_bd_lscc,
                                                        'ngay_kt_bc': ds.ngay_kt_lscc,
                                                        'ca_lam_viec_bc': ds.ca_lam_viec_lscc.id,
                                                        'giovao_bc': ds.time1_lscc,
                                                        'giora_bc': ds.time2_lscc,
                                                        'thamchieu_bc': 'no_data_ra'
                                                        }
                                            list_bc_val_2 = []
                                            list_bc_val_2.append([0, 0, val_2])
                                            self.write({'baocao_kn_ccn': list_bc_val_2})
                                            #XÓA record này ở 'Lịch Sử Chấm Công', cho user xem ở mục 'Báo Cáo'
                                            ds.unlink()
                                        else:
                                            if ds.time2_lscc >= clv.giora1:
                                                ds.ngaycong = 1
                                                trangthai_dulieu = self.env["du.lieu"].search([('name_dl', '=', ds.name.id),
                                                                                               ('thoigian_dl', '=', ds.ngay_bd_lscc)])
                                                for tt in trangthai_dulieu:
                                                    tt.write({'state': 'hoantat_dl'})
                                                    self.write({'trangthai_ccn': 'hoantat_ccn'})
                                            #Ngược lại, nếu time2_lscc < giovao1:
                                            else:
                                                #Thì xét nếu time2_lscc <= giờ vào + 3 tiếng: Không chấm công 
                                                if ds.time2_lscc <= clv.giovao2 + 3:
                                                    ds.ngaycong = 0
                                                    ds.write({'thamchieu_lscc': 'early'})
                                                    trangthai_dulieu = self.env["du.lieu"].search([('name_dl', '=', ds.name.id),
                                                                                                   ('thoigian_dl', '=', ds.ngay_bd_lscc)])
                                                    for tt in trangthai_dulieu:
                                                        tt.write({'state': 'hoantat_dl'})
                                                        self.write({'trangthai_ccn': 'hoantat_ccn'})
                                                else:
                                                    ds.ngaycong = 0.5
                                                    ds.write({'thamchieu_lscc': 'early'})
                                                    trangthai_dulieu = self.env["du.lieu"].search([('name_dl', '=', ds.name.id),
                                                                                                   ('thoigian_dl', '=', ds.ngay_bd_lscc)])
                                                    for tt in trangthai_dulieu:
                                                        tt.write({'state': 'hoantat_dl'})
                                                        self.write({'trangthai_ccn': 'hoantat_ccn'})
                                    #Ngược lại, nếu time1_lscc > giovao2:
                                    else:
                                        #Thì xét nếu time1_lscc >= giovao2 + 30 phút: Không chấm công
                                        if ds.time1_lscc >= clv.giovao2 + 0.30:
                                            ds.ngaycong = 0
                                            ds.write({'thamchieu_lscc': 'late'})
                                            trangthai_dulieu = self.env["du.lieu"].search([('name_dl', '=', ds.name.id),
                                                                                               ('thoigian_dl', '=', ds.ngay_bd_lscc)])
                                            for tt in trangthai_dulieu:
                                                tt.write({'state': 'hoantat_dl'})
                                                self.write({'trangthai_ccn': 'hoantat_ccn'})
                                        #Ngược lại, nếu time1_lscc < giovao2 + 30 phút: Chấm 0.5 ngày công
                                        else:
                                            if not ds.time2_lscc:
                                                rec.write({'trangthai_dscc': 'xem_bc'})
                                                val_2 = {
                                                        'name_bc': ds.name.id,
                                                        'ngay_bd_bc': ds.ngay_bd_lscc,
                                                        'ngay_kt_bc': ds.ngay_kt_lscc,
                                                        'ca_lam_viec_bc': ds.ca_lam_viec_lscc.id,
                                                        'giovao_bc': ds.time1_lscc,
                                                        'giora_bc': ds.time2_lscc,
                                                        'thamchieu_bc': 'no_data_ra'
                                                        }
                                                list_bc_val_2 = []
                                                list_bc_val_2.append([0, 0, val_2])
                                                self.write({'baocao_kn_ccn': list_bc_val_2})
                                                #XÓA record này ở 'Lịch Sử Chấm Công', cho user xem ở mục 'Báo Cáo'
                                                ds.unlink()
                                            else:
                                                if ds.time2_lscc >= clv.giora1:
                                                    ds.ngaycong = 0.5
                                                    ds.write({'thamchieu_lscc': 'late'})
                                                    trangthai_dulieu = self.env["du.lieu"].search([('name_dl', '=', ds.name.id),
                                                                                               ('thoigian_dl', '=', ds.ngay_bd_lscc)])
                                                    for tt in trangthai_dulieu:
                                                        tt.write({'state': 'hoantat_dl'})
                                                        self.write({'trangthai_ccn': 'hoantat_ccn'})
                                                else:
                                                    #ngày công = 0
                                                    ds.write({'thamchieu_lscc': 'late_early'})
                                                    trangthai_dulieu = self.env["du.lieu"].search([('name_dl', '=', ds.name.id),
                                                                                               ('thoigian_dl', '=', ds.ngay_bd_lscc)])
                                                    for tt in trangthai_dulieu:
                                                        tt.write({'state': 'hoantat_dl'})
                                                        self.write({'trangthai_ccn': 'hoantat_ccn'})
                    #Nếu > 16.30: làm qua đêm
                    else:
                        if not rec.trangthai_dscc:
                            rec.write({'trangthai_dscc': 'xem_bc'})
                            #Trước khi in ra 'Báo Cáo', xét trường hợp:
                            #do nhân sự chấm công ngày 8 trước (ko theo thứ tự), nên có record ở 'Báo Cáo' ngày 8
                            #Note: do không chấm công theo thứ tự, nên record ở 'Báo Cáo' ngày 8 ko xác định chính xác 'ngày bắt đầu', 'ngày kết thúc'
                            xet_bc = self.env['bao.cao'].search([('name_bc', '=', rec.name_dscc.id),
                                                                 ('ngay_bd_bc', '=', self.ngay + timedelta(days=1))])
                            #Nếu record của báo cáo ngày 7 '=' (tìm thấy) record ngày 8...
                            if xet_bc:
                                for xet in xet_bc:
                                    val = {
                                            'name_bc': rec.name_dscc.id,
                                            'ngay_bd_bc': self.ngay,
                                            'ngay_kt_bc': self.ngay + timedelta(days=1),
                                            'ca_lam_viec_bc': clv.name_clv.id,
                                            'giora_bc': xet.giora_bc,
                                            'thamchieu_bc': 'no_data_vao'
                                            }
                                    bc_val = []
                                    bc_val.append([0, 0, val])
                                    #... thì tập hợp lại và ghi ra 'Báo Cáo' record mới có trạng thái : no_data_vao
                                    self.write({'baocao_kn_ccn': bc_val})
                                    #Đồng thời, xóa record cũ (ngày 8) trước đó đi
                                    xet.unlink()
                            #Nếu ko '=' (ko tìm thấy)... (trường hợp này là c.c ngày 7 trước nhưng có thể nv (ca đêm) quên chấm công giờ vào)
                            else:
                                val = {
                                        'name_bc': rec.name_dscc.id,
                                        'ngay_bd_bc': self.ngay,
                                        'ngay_kt_bc': self.ngay + timedelta(days=1),
                                        'ca_lam_viec_bc': clv.name_clv.id,
                                        'thamchieu_bc': 'no_data_vao'
                                        }
                                bc_val = []
                                bc_val.append([0, 0, val])
                                #... thì in ra record mới ở 'Báo Cáo' có trạng thái: no_data
                                self.write({'baocao_kn_ccn': bc_val})
                        else:
                            #Xét trường hợp có record của nv ở 'Báo Cáo' trước.
                            #VD: Ca đêm giờ vào ngày 7, giờ ra ngày 8. Khi chấm công, nhân sự chọn chấm công ngày 8 trước (ko theo thứ tự)
                            lich_su = self.env['ls.chamcong'].search([('name', '=', rec.name_dscc.id),
                                                                      ('ngay_kt_lscc', '=', self.ngay + timedelta(days=1))])
                            if lich_su:
                                x = []
                                for ls in lich_su:
                                    bao_cao = self.env['bao.cao'].search([('name_bc', '=', ls.name.id),
                                                                          ('ngay_bd_bc', '=', ls.ngay_kt_lscc)])
                                    #Nếu record của nv ca đêm ngày 7 '=' với record ngày 8
                                    if bao_cao:
                                        x = ls
                                        for bc in bao_cao:
                                            ca_lam_viec = self.env['ca.lamviec'].search([('name_clv', '=', ls.ca_lam_viec_lscc.id)])
                                            for clv in ca_lam_viec:
                                                if x.time1_lscc <= clv.giovao2:
                                                    #chỉ cần xét giờ ra của 'Báo Cáo'
                                                    if bc.giora_bc >= clv.giora1:
                                                        val = {
                                                            'name': bc.name_bc.id,
                                                            'ngay_bd_lscc': self.ngay,
                                                            'ngay_kt_lscc': bc.ngay_bd_bc,
                                                            'ca_lam_viec_lscc': ls.ca_lam_viec_lscc.id,
                                                            'time1_lscc': x.time1_lscc,
                                                            'time2_lscc': bc.giora_bc,
                                                            'ngaycong': 1
                                                            }
                                                        list_val = []
                                                        list_val.append([0, 0, val])
                                                        self.write({'lscc_kn_ccn': list_val})
                                                        du_lieu1 = self.env['du.lieu'].search([('name_dl', '=', ls.name.id),
                                                                                               ('thoigian_dl', '=', self.ngay),
                                                                                               ('state', '=', 'tiepnhan_dl')])
                                                        for z in du_lieu1:
                                                            z.write({'state': 'hoantat_dl'})
                                                        du_lieu2 = self.env['du.lieu'].search([('name_dl', '=', ls.name.id),
                                                                                               ('thoigian_dl', '=', self.ngay+ timedelta(days=1)),
                                                                                               ('state', '=', 'tiepnhan_dl')])
                                                        for i in du_lieu2:
                                                            i.write({'state': 'hoantat_dl'})
                                                        #xóa record ở 'Báo Cáo' ngày 8
                                                        bc.unlink()
                                                        #Sau khi tạo record mới vời đầy đủ giờ vào, giờ ra, xóa record ở 'Lịch Sử Chấm Công' ngày 7
                                                        ls.unlink()
                                                    else:
                                                        val = {
                                                            'name': bc.name_bc.id,
                                                            'ngay_bd_lscc': self.ngay,
                                                            'ngay_kt_lscc': bc.ngay_bd_bc,
                                                            'ca_lam_viec_lscc': ls.ca_lam_viec_lscc.id,
                                                            'time1_lscc': x.time1_lscc,
                                                            'time2_lscc': bc.giora_bc,
                                                            'ngaycong': 0.5,
                                                            'thamchieu_lscc': 'early'
                                                            }
                                                        list_val = []
                                                        list_val.append([0, 0, val])
                                                        self.write({'lscc_kn_ccn': list_val})
                                                        du_lieu1 = self.env['du.lieu'].search([('name_dl', '=', ls.name.id),
                                                                                               ('thoigian_dl', '=', self.ngay),
                                                                                               ('state', '=', 'tiepnhan_dl')])
                                                        for z in du_lieu1:
                                                            z.write({'state': 'hoantat_dl'})
                                                        du_lieu2 = self.env['du.lieu'].search([('name_dl', '=', ls.name.id),
                                                                                               ('thoigian_dl', '=', self.ngay+ timedelta(days=1)),
                                                                                               ('state', '=', 'tiepnhan_dl')])
                                                        for i in du_lieu2:
                                                            i.write({'state': 'hoantat_dl'})
                                                        bc.unlink()
                                                        ls.unlink()
                                                else:
                                                    if bc.giora_bc >= clv.giora1:
                                                        val = {
                                                            'name': bc.name_bc.id,
                                                            'ngay_bd_lscc': self.ngay,
                                                            'ngay_kt_lscc': bc.ngay_bd_bc,
                                                            'ca_lam_viec_lscc': ls.ca_lam_viec_lscc.id,
                                                            'time1_lscc': x.time1_lscc,
                                                            'time2_lscc': bc.giora_bc,
                                                            'ngaycong': 0.5,
                                                            'thamchieu_lscc': 'late'
                                                            }
                                                        list_val = []
                                                        list_val.append([0, 0, val])
                                                        self.write({'lscc_kn_ccn': list_val})
                                                        du_lieu1 = self.env['du.lieu'].search([('name_dl', '=', ls.name.id),
                                                                                               ('thoigian_dl', '=', self.ngay),
                                                                                               ('state', '=', 'tiepnhan_dl')])
                                                        for z in du_lieu1:
                                                            z.write({'state': 'hoantat_dl'})
                                                        du_lieu2 = self.env['du.lieu'].search([('name_dl', '=', ls.name.id),
                                                                                               ('thoigian_dl', '=', self.ngay+ timedelta(days=1)),
                                                                                               ('state', '=', 'tiepnhan_dl')])
                                                        for i in du_lieu2:
                                                            i.write({'state': 'hoantat_dl'})
                                                        bc.unlink()
                                                        ls.unlink()
                                                    else:
                                                        val = {
                                                            'name': bc.name_bc.id,
                                                            'ngay_bd_lscc': self.ngay,
                                                            'ngay_kt_lscc': bc.ngay_bd_bc,
                                                            'ca_lam_viec_lscc': ls.ca_lam_viec_lscc.id,
                                                            'time1_lscc': x.time1_lscc,
                                                            'time2_lscc': bc.giora_bc,
                                                            'ngaycong': 0,
                                                            'thamchieu_lscc': 'late_early'
                                                            }
                                                        list_val = []
                                                        list_val.append([0, 0, val])
                                                        self.write({'lscc_kn_ccn': list_val})
                                                        du_lieu1 = self.env['du.lieu'].search([('name_dl', '=', ls.name.id),
                                                                                               ('thoigian_dl', '=', self.ngay),
                                                                                               ('state', '=', 'tiepnhan_dl')])
                                                        for z in du_lieu1:
                                                            z.write({'state': 'hoantat_dl'})
                                                        du_lieu2 = self.env['du.lieu'].search([('name_dl', '=', ls.name.id),
                                                                                               ('thoigian_dl', '=', self.ngay+ timedelta(days=1)),
                                                                                               ('state', '=', 'tiepnhan_dl')])
                                                        for i in du_lieu2:
                                                            i.write({'state': 'hoantat_dl'})
                                                        bc.unlink()
                                                        ls.unlink()
                                    else:
                                        #Nếu record ca đêm ngày 7 không '=' (không tìm thấy) record ngày 8
                                        #thì ghi trạng thái của record ngày 7 là: 'Chờ dữ liệu giờ ra'
                                        ls.write({'thamchieu_lscc': 'chogiora'})
                                        
            #XÉT CÁC RECORD của model 'Dữ Liệu' CÓ 'state' = 'Rỗng'
        
            #Note: Ca đêm sẽ không được nghỉ phép 0.5 ngày
            ngoai_dscc = self.env["du.lieu"].search([('thoigian_dl', '=', self.ngay),
                                                     ('state', '=', False)])
            a = []
            b = []
            c = []
            d = []
            e = []
            f = []
            g = []
            h = []
            for ngoai in ngoai_dscc:
                tim_trong_lscc = self.env["ls.chamcong"].search([('name', '=', ngoai.name_dl.id),
                                                                 ('ngay_kt_lscc', '=', ngoai.thoigian_dl)])
                if tim_trong_lscc:
                    #Khai báo biến 'giatri': Rỗng ở ngoài vòng lặp
                    giatri = []
                    for tim in tim_trong_lscc:
                        tim_clv = self.env["ca.lamviec"].search([('name_clv', '=', tim.ca_lam_viec_lscc.id)])
                        for line in tim_clv:
                            giatri = tim
                            #Xét giờ vào của record ngày này:
                            if giatri.time1_lscc <= line.giovao2:
                                #Xét giờ ra của record ngày kia
                                if ngoai.max_time1 >= ngoai.max_time2:
                                    if ngoai.max_time1 >= line.giora1:
                                        a = ngoai
                                        break
                                    else:
                                        b = ngoai
                                        break
                                else:
                                    if ngoai.max_time2 >= line.giora1:
                                        c = ngoai
                                        break
                                    else:
                                        d = ngoai
                                        break
                            else:
                                #Xét giờ ra của record ngày kia
                                if ngoai.max_time1 >= ngoai.max_time2:
                                    if ngoai.max_time1 >= line.giora1:
                                        e = ngoai
                                        break
                                    else:
                                        f = ngoai
                                        break
                                else:
                                    if ngoai.max_time2 >= line.giora1:
                                        g = ngoai
                                        break
                                    else:
                                        h = ngoai
                                        break
                else:
                    #Nếu không thỏa đk trong biến 'tim_trong_lscc', (có thể do nhân sự chấm công không theo thứ tự ngày) 
                    #Thì record đó hoặc không có trong 'Lịch Làm Việc', hoặc không có data Giờ Vào (Ca đêm)
                    #Do các record này còn nằm trong vòng lặp của 'Danh Sách Chấm Công'
                    #Nên các record này sẽ lần lượt được so sánh với Từng Record của 'Danh Sách Chấm Công'
                    #Để tránh lặp lại theo vòng lặp, xét đk:
                    #Chỉ in ra các record có tên, ngày và state ='False'
                    #Vậy theo vòng lặp, Nếu các record có state ='tiepnhan_dl' => không in ra 'Báo Cáo'
                    xet_dl = self.env['du.lieu'].search([('name_dl', '=', ngoai.name_dl.id),
                                                         ('thoigian_dl', '=', self.ngay),
                                                         ('state', '=', False)])
                    i = []
                    j = []
                    k = []
                    l = []
                    for x in xet_dl:
                        #Do 1 user có thể có nhiều record data chấm công (quét nhiều lần)
                        nhieu_record = self.env['du.lieu'].search([('name_dl', '=', x.name_dl.id),
                                                                   ('thoigian_dl', '=', x.thoigian_dl),
                                                                   ('state', '=', False)])
                        if nhieu_record:
                            for nhieu in nhieu_record:
                                #Đặt nhiều record của 1 nv về trạng thái = 'Tiếp Nhận'
                                nhieu.write({'state': 'tiepnhan_dl'})
                        if x.max_time1 >= x.max_time2:
                            #VD: max_time1 = 7.30 <= max.time1 + 0.05 = 7.35
                            if x.max_time1 <= x.min_time1 + 0.05:
                                #=> Là ca đêm nên: chỉ lấy max_time1 làm giờ ra
                                i = x
                                break
                            else:
                                #Ngược lại, Nếu '>': sẽ lấy min_time1 và max_time1 làm giờ vào giờ ra ở 'Báo Cáo'
                                j = x
                                break
                        else:
                            if x.max_time2 <= x.min_time1 + 0.05:
                                k = x
                                break
                            else:
                                l = x
                                break
                    if i:
                        #Trước khi in ra 'Báo Cáo', kt xem record ngày 8 có '=' (tìm thấy) record ngày 7 ko?
                        xet_bc = self.env['bao.cao'].search([('name_bc', '=', i.name_dl.id),
                                                             ('ngay_kt_bc', '=', self.ngay)])
                        #Nếu tìm thấy...
                        if xet_bc:
                            val = {
                                    'name_bc': i.name_dl.id,
                                    'ngay_bd_bc': self.ngay - timedelta(days=1),
                                    'ngay_kt_bc': self.ngay,
                                    'giora_bc': i.max_time1,
                                    'thamchieu_bc': 'no_data_vao'
                                    }
                            bc_val = []
                            bc_val.append([0, 0, val])
                            #... in ra 'Báo Cáo' với đúng ngày bd và kt báo cáo 
                            self.write({'baocao_kn_ccn': bc_val})
                        else:
                            #Nếu ko...
                            val = {
                                    'name_bc': i.name_dl.id,
                                    'ngay_bd_bc': self.ngay,
                                    'ngay_kt_bc': self.ngay,
                                    'giora_bc': i.max_time1,
                                    'thamchieu_bc': 'no_data_vao'
                                    }
                            bc_val = []
                            bc_val.append([0, 0, val])
                            #... thì in ra 'Báo Cáo' với ngày mặc định cho ngày bd và kt
                            self.write({'baocao_kn_ccn': bc_val})
                            
                    if j:
                        xet_bc = self.env['bao.cao'].search([('name_bc', '=', j.name_dl.id),
                                                             ('ngay_kt_bc', '=', self.ngay)])
                        if xet_bc:
                            val = {
                                    'name_bc': j.name_dl.id,
                                    'ngay_bd_bc': self.ngay - timedelta(days=1),
                                    'ngay_kt_bc': self.ngay,
                                    'giora_bc': j.max_time1,
                                    'thamchieu_bc': 'no_data_vao'
                                    }
                            bc_val = []
                            bc_val.append([0, 0, val])
                            self.write({'baocao_kn_ccn': bc_val})
                        else:
                            val = {
                                    'name_bc': j.name_dl.id,
                                    'ngay_bd_bc': self.ngay,
                                    'ngay_kt_bc': self.ngay,
                                    'giovao_bc': j.min_time1,
                                    'giora_bc': j.max_time1,
                                    'thamchieu_bc': 'no_pl'
                                    }
                            bc_val = []
                            bc_val.append([0, 0, val])
                            self.write({'baocao_kn_ccn': bc_val})    
                    if k:
                        xet_bc = self.env['bao.cao'].search([('name_bc', '=', k.name_dl.id),
                                                             ('ngay_kt_bc', '=', self.ngay)])
                        if xet_bc:
                            val = {
                                    'name_bc': k.name_dl.id,
                                    'ngay_bd_bc': self.ngay - timedelta(days=1),
                                    'ngay_kt_bc': self.ngay,
                                    'giora_bc': k.max_time2,
                                    'thamchieu_bc': 'no_data_vao'
                                    }
                            bc_val = []
                            bc_val.append([0, 0, val])
                            self.write({'baocao_kn_ccn': bc_val})
                        else:
                            val = {
                                    'name_bc': k.name_dl.id,
                                    'ngay_bd_bc': self.ngay,
                                    'ngay_kt_bc': self.ngay,
                                    'giora_bc': k.max_time2,
                                    'thamchieu_bc': 'no_data_vao'
                                    }
                            bc_val = []
                            bc_val.append([0, 0, val])
                            self.write({'baocao_kn_ccn': bc_val})
                    if l:
                        xet_bc = self.env['bao.cao'].search([('name_bc', '=', l.name_dl.id),
                                                             ('ngay_kt_bc', '=', self.ngay)])
                        if xet_bc:
                            val = {
                                    'name_bc': l.name_dl.id,
                                    'ngay_bd_bc': self.ngay - timedelta(days=1),
                                    'ngay_kt_bc': self.ngay,
                                    'giora_bc': l.max_time2,
                                    'thamchieu_bc': 'no_data_vao'
                                    }
                            bc_val = []
                            bc_val.append([0, 0, val])
                            self.write({'baocao_kn_ccn': bc_val})
                        else:
                            val = {
                                    'name_bc': l.name_dl.id,
                                    'ngay_bd_bc': self.ngay,
                                    'ngay_kt_bc': self.ngay,
                                    'giovao_bc': l.min_time1,
                                    'giora_bc': l.max_time2,
                                    'thamchieu_bc': 'no_pl'
                                    }
                            bc_val = []
                            bc_val.append([0, 0, val])
                            self.write({'baocao_kn_ccn': bc_val}) 
            if a:
                val = {
                        'name': a.name_dl.id,
                        'ngay_bd_lscc': self.ngay - timedelta(days=1),
                        'ngay_kt_lscc': self.ngay,
                        'ca_lam_viec_lscc': tim.ca_lam_viec_lscc.id,
                        #Lấy giá trị giờ vào trong time1_lscc của record thỏa đk trong domain vào ngày này (*)
                        #gắn vào field time1_lscc của record vào ngày kia để tạo record mới ở ls.chamcong với đầy đủ giờ vào/ra
                        'time1_lscc': giatri.time1_lscc,
                        'time2_lscc': a.max_time1,
                        'ngaycong': 1
                        }
                list_val = []
                list_val.append([0, 0, val])
                self.write({'lscc_kn_ccn': list_val})
                #Đồng thời, XÓA luôn record (*)
                tim.unlink()
                #Sau khi hoàn tất chấm công, chuyển trạng thái của record trong model du_lieu.py vào ngày này (VD: ngày vào: 7)
                xet_dl1 = self.env["du.lieu"].search([('thoigian_dl', '=', self.ngay - timedelta(days=1)),
                                                      ('state', '=', 'tiepnhan_dl')])
                if xet_dl1:
                    for xet in xet_dl1:
                        xet.write({'state': 'hoantat_dl'})
                #Sau khi hoàn tất chấm công, chuyển trạng thái của record trong model du_lieu.py vào ngày kia (VD: ngày ra: 8)
                #Xét 1 Record (hoặc nhiều Record) của 1 user có cùng tên, cùng ngày và state = 'Rỗng'
                xet_dl2 = self.env["du.lieu"].search([('thoigian_dl', '=', self.ngay),
                                                      ('state', '=', False),
                                                      ('name_dl', '=', a.name_dl.id)])
                if xet_dl2:
                    for xet in xet_dl2:
                        xet.write({'state': 'hoantat_dl'})
            if b:
                val = {
                        'name': b.name_dl.id,
                        'ngay_bd_lscc': self.ngay - timedelta(days=1),
                        'ngay_kt_lscc': self.ngay,
                        'ca_lam_viec_lscc': tim.ca_lam_viec_lscc.id,
                        #Lấy giá trị giờ vào trong time1_lscc của record thỏa đk trong domain vào ngày này (*)
                        #gắn vào field time1_lscc của record vào ngày kia để tạo record mới ở ls.chamcong với đầy đủ giờ vào/ra
                        'time1_lscc': giatri.time1_lscc,
                        'time2_lscc': b.max_time1,
                        'ngaycong': 0.5,
                        'thamchieu_lscc': 'early'
                        }
                list_val = []
                list_val.append([0, 0, val])
                self.write({'lscc_kn_ccn': list_val})
                #Đồng thời, XÓA luôn record (*)
                tim.unlink()
                #Sau khi hoàn tất chấm công, chuyển trạng thái của record trong model du_lieu.py vào ngày này (VD: ngày vào: 7)
                xet_dl3 = self.env["du.lieu"].search([('thoigian_dl', '=', self.ngay - timedelta(days=1)),
                                                      ('state', '=', 'tiepnhan_dl')])
                if xet_dl3:
                    for xet in xet_dl3:
                        xet.write({'state': 'hoantat_dl'})
                #Sau khi hoàn tất chấm công, chuyển trạng thái của record trong model du_lieu.py vào ngày kia (VD: ngày ra: 8)
                #Xét 1 Record (hoặc nhiều Record) của 1 user có cùng tên, cùng ngày và state = 'Rỗng'
                xet_dl4 = self.env["du.lieu"].search([('thoigian_dl', '=', self.ngay),
                                                      ('state', '=', False),
                                                      ('name_dl', '=', b.name_dl.id)])
                if xet_dl4:
                    for xet in xet_dl2:
                        xet.write({'state': 'hoantat_dl'})
            if c:
                val = {
                        'name': c.name_dl.id,
                        'ngay_bd_lscc': self.ngay - timedelta(days=1),
                        'ngay_kt_lscc': self.ngay,
                        'ca_lam_viec_lscc': tim.ca_lam_viec_lscc.id,
                        'time1_lscc': giatri.time1_lscc,
                        'time2_lscc': c.max_time2,
                        'ngaycong': 1
                        }
                list_val = []
                list_val.append([0, 0, val])
                self.write({'lscc_kn_ccn': list_val})
                tim.unlink()
                xet_dl5 = self.env["du.lieu"].search([('thoigian_dl', '=', self.ngay - timedelta(days=1)),
                                                      ('state', '=', 'tiepnhan_dl')])
                if xet_dl5:
                    for xet in xet_dl5:
                        xet.write({'state': 'hoantat_dl'})
                xet_dl6 = self.env["du.lieu"].search([('thoigian_dl', '=', self.ngay),
                                                      ('state', '=', False),
                                                      ('name_dl', '=', c.name_dl.id)])
                if xet_dl6:
                    for xet in xet_dl6:
                        xet.write({'state': 'hoantat_dl'})
            if d:
                val = {
                        'name': d.name_dl.id,
                        'ngay_bd_lscc': self.ngay - timedelta(days=1),
                        'ngay_kt_lscc': self.ngay,
                        'ca_lam_viec_lscc': tim.ca_lam_viec_lscc.id,
                        'time1_lscc': giatri.time1_lscc,
                        'time2_lscc': d.max_time2,
                        'ngaycong': 1
                        }
                list_val = []
                list_val.append([0, 0, val])
                self.write({'lscc_kn_ccn': list_val})
                tim.unlink()
                xet_dl7 = self.env["du.lieu"].search([('thoigian_dl', '=', self.ngay - timedelta(days=1)),
                                                      ('state', '=', 'tiepnhan_dl')])
                if xet_dl7:
                    for xet in xet_dl7:
                        xet.write({'state': 'hoantat_dl'})
                xet_dl8 = self.env["du.lieu"].search([('thoigian_dl', '=', self.ngay),
                                                      ('state', '=', False),
                                                      ('name_dl', '=', d.name_dl.id)])
                if xet_dl8:
                    for xet in xet_dl8:
                        xet.write({'state': 'hoantat_dl'})
            if e:
                val = {
                        'name': e.name_dl.id,
                        'ngay_bd_lscc': self.ngay - timedelta(days=1),
                        'ngay_kt_lscc': self.ngay,
                        'ca_lam_viec_lscc': tim.ca_lam_viec_lscc.id,
                        'time1_lscc': giatri.time1_lscc,
                        'time2_lscc': e.max_time1,
                        'ngaycong': 0.5,
                        'thamchieu_lscc': 'late'
                        }
                list_val = []
                list_val.append([0, 0, val])
                self.write({'lscc_kn_ccn': list_val})
                tim.unlink()
                xet_dl9 = self.env["du.lieu"].search([('thoigian_dl', '=', self.ngay - timedelta(days=1)),
                                                      ('state', '=', 'tiepnhan_dl')])
                if xet_dl9:
                    for xet in xet_dl9:
                        xet.write({'state': 'hoantat_dl'})
                xet_dl10 = self.env["du.lieu"].search([('thoigian_dl', '=', self.ngay),
                                                       ('state', '=', False),
                                                       ('name_dl', '=', e.name_dl.id)])
                if xet_dl10:
                    for xet in xet_dl10:
                        xet.write({'state': 'hoantat_dl'})
            if f:
                val = {
                        'name': f.name_dl.id,
                        'ngay_bd_lscc': self.ngay - timedelta(days=1),
                        'ngay_kt_lscc': self.ngay,
                        'ca_lam_viec_lscc': tim.ca_lam_viec_lscc.id,
                        'time1_lscc': giatri.time1_lscc,
                        'time2_lscc': f.max_time1,
                        'ngaycong': 0,
                        'thamchieu_lscc': 'late_early'
                        }
                list_val = []
                list_val.append([0, 0, val])
                self.write({'lscc_kn_ccn': list_val})
                tim.unlink()
                xet_dl11 = self.env["du.lieu"].search([('thoigian_dl', '=', self.ngay - timedelta(days=1)),
                                                       ('state', '=', 'tiepnhan_dl')])
                if xet_dl11:
                    for xet in xet_dl11:
                        xet.write({'state': 'hoantat_dl'})
                xet_dl12 = self.env["du.lieu"].search([('thoigian_dl', '=', self.ngay),
                                                       ('state', '=', False),
                                                       ('name_dl', '=', f.name_dl.id)])
                if xet_dl12:
                    for xet in xet_dl12:
                        xet.write({'state': 'hoantat_dl'})
            if g:
                val = {
                        'name': g.name_dl.id,
                        'ngay_bd_lscc': self.ngay - timedelta(days=1),
                        'ngay_kt_lscc': self.ngay,
                        'ca_lam_viec_lscc': tim.ca_lam_viec_lscc.id,
                        'time1_lscc': giatri.time1_lscc,
                        'time2_lscc': g.max_time2,
                        'ngaycong': 0.5,
                        'thamchieu_lscc': 'late'
                        }
                list_val = []
                list_val.append([0, 0, val])
                self.write({'lscc_kn_ccn': list_val})
                tim.unlink()
                xet_dl13 = self.env["du.lieu"].search([('thoigian_dl', '=', self.ngay - timedelta(days=1)),
                                                       ('state', '=', 'tiepnhan_dl')])
                if xet_dl13:
                    for xet in xet_dl13:
                        xet.write({'state': 'hoantat_dl'})
                xet_dl14 = self.env["du.lieu"].search([('thoigian_dl', '=', self.ngay),
                                                       ('state', '=', False),
                                                       ('name_dl', '=', g.name_dl.id)])
                if xet_dl14:
                    for xet in xet_dl14:
                        xet.write({'state': 'hoantat_dl'})
            if h:
                val = {
                        'name': h.name_dl.id,
                        'ngay_bd_lscc': self.ngay - timedelta(days=1),
                        'ngay_kt_lscc': self.ngay,
                        'ca_lam_viec_lscc': tim.ca_lam_viec_lscc.id,
                        'time1_lscc': giatri.time1_lscc,
                        'time2_lscc': h.max_time2,
                        'ngaycong': 0,
                        'thamchieu_lscc': 'late_early'
                        }
                list_val = []
                list_val.append([0, 0, val])
                self.write({'lscc_kn_ccn': list_val})
                tim.unlink()
                xet_dl15 = self.env["du.lieu"].search([('thoigian_dl', '=', self.ngay - timedelta(days=1)),
                                                       ('state', '=', 'tiepnhan_dl')])
                if xet_dl15:
                    for xet in xet_dl15:
                        xet.write({'state': 'hoantat_dl'})
                xet_dl16 = self.env["du.lieu"].search([('thoigian_dl', '=', self.ngay),
                                                       ('state', '=', False),
                                                       ('name_dl', '=', h.name_dl.id)])
                if xet_dl16:
                    for xet in xet_dl16:
                        xet.write({'state': 'hoantat_dl'})
                                        
        #Sau khi hoàn tất chấm công, thì đưa trạng thái của cham_cong.py về rỗng ' '
        self.trangthai_ccn = 'hoantat_ccn'
        self.state = 'chamcong_ccn'
        return True
    
    def veduthao_ngay(self):
        #Khi về dự thảo, thì record tạo ra từ 'Xác Nhận' vẫn được save với trạng thái 'Chờ Xác Nhận'. 
        #Không cần xóa record.
        self.trangthai_ccn = 'choxacnhan_ccn'
        self.state = "moi_ccn"
        return True
        
    def huy_ngay(self):
        for rec in self:
            # Đưa các record thỏa điều kiện ở model du_lieu.py (tab Dữ Liệu) về trạng thái ban đầu:
            for line in rec.lscc_kn_ccn:
                xoa_trangthai_dulieu = self.env["du.lieu"].search([('thoigian_dl', '=', line.ngay_bd_lscc),
                                                                   ('name_dl', '=', line.name.id)])
                if xoa_trangthai_dulieu:
                    xoa_trangthai_dulieu.write({'state': False})
                #xóa rec trong model ls_chamcong.py
                line.unlink()
            # xóa luôn record chấm công theo từng Ngày trong model 'chamcong_ngay.py'
            rec.unlink()           
            #Sau khi xóa, trở lại form view với trạng thái ban đầu
            return {
                'view_mode': 'form',
                'res_model': 'chamcong.ngay',
                #Dùng 'main' thay 'current' hợp lý hơn vì đã xóa record
                'target': 'main',
                'type': 'ir.actions.act_window',
                }
        
#------------------------------------------------
# Thông Báo Trùng Lặp A Trong Lịch Sử Chấm Công
#------------------------------------------------
class tb_lscc(models.TransientModel):
    _name = 'tb.lscc'
    _description = 'Chấm Công Theo Ca: (Thông Báo trùng lắp) các record đã có trong Lịch Sử Chấm Công, Báo Cáo'
    
    ngay_tb = fields.Date('Ngày', readonly=True)
    ca_lam_viec_tb = fields.Many2one('planning.role', string='Ca làm việc', readonly=True)
    
    def dong_y(self):
        cc_theo_ca = self.env["cham.cong"].search([('ca_lam_viec', '=', self.ca_lam_viec_tb.id),
                                                   ('thoigian', '=', self.ngay_tb)])
        for a in cc_theo_ca:
            ls_cc = self.env["ls.chamcong"].search([('ngay_bd_lscc', '=', self.ngay_tb)])
            b_c = self.env['bao.cao'].search([('ngay_bd_bc', '=', self.ngay_tb)])
            for b in ls_cc:
                gio = datetime.min.time() #min.time : nữa đêm
                ngay = b.ngay_bd_lscc
                ds_cc = self.env["ds.chamcong"].search([('ca_lam_viec_dscc', '=', b.ca_lam_viec_lscc.id),
                                                        ('name_dscc', '=', b.name.id),
                                                        ('thoigian_bd_dscc', '>', datetime.combine(ngay,gio)),
                                                        ('thoigian_bd_dscc', '<', ngay + timedelta(days=1))])
                if ds_cc:
                    for c in ds_cc:
                        if not c.trangthai_dscc:
                            c.trangthai_dscc = "trunglap"
            for d in b_c:
                gio = datetime.min.time() #min.time : nữa đêm
                ngay = d.ngay_bd_bc
                ds_cc = self.env["ds.chamcong"].search([('ca_lam_viec_dscc', '=', d.ca_lam_viec_bc.id),
                                                        ('name_dscc', '=', d.name_bc.id),
                                                        ('thoigian_bd_dscc', '>', datetime.combine(ngay,gio)),
                                                        ('thoigian_bd_dscc', '<', ngay + timedelta(days=1))])
                if ds_cc:
                    for e in ds_cc:
                        if not e.trangthai_dscc:
                            e.trangthai_dscc = 'trunglap'
            
            a.state = 'daduyet'
        return True

#------------------------------------------------
# Thông Báo Trùng Lặp B Trong Lịch Sử Chấm Công
#------------------------------------------------
class tbb_lscc(models.TransientModel):
    _name = 'tbb.lscc'
    _description = 'Chấm Công Theo Ngày: (Thông Báo B trùng lắp) các record đã có trong Lịch Sử Chấm Công, Báo Cáo'
    
    ngay_tbb = fields.Date('Ngày Làm Việc', readonly=True)
    
    def go_to_ok(self):
        cc_theo_ngay = self.env["chamcong.ngay"].search([('ngay', '=', self.ngay_tbb)])
        for a in cc_theo_ngay:
            ls_cc = self.env["ls.chamcong"].search([('ngay_bd_lscc', '=', self.ngay_tbb)])
            b_c = self.env['bao.cao'].search([('ngay_bd_bc', '=', self.ngay_tbb)])
            for b in ls_cc:
                gio = datetime.min.time() #min.time : nữa đêm
                ngay = b.ngay_bd_lscc
                ds_cc = self.env["ds.chamcong"].search([('ca_lam_viec_dscc', '=', b.ca_lam_viec_lscc.id),
                                                        ('name_dscc', '=', b.name.id),
                                                        ('thoigian_bd_dscc', '>', datetime.combine(ngay,gio)),
                                                        ('thoigian_bd_dscc', '<', ngay + timedelta(days=1))])
                if ds_cc:
                    for c in ds_cc:
                        if not c.trangthai_dscc:
                            c.trangthai_dscc = "trunglap"
            for d in b_c:
                gio = datetime.min.time() #min.time : nữa đêm
                ngay = d.ngay_bd_bc
                ds_cc = self.env["ds.chamcong"].search([('ca_lam_viec_dscc', '=', d.ca_lam_viec_bc.id),
                                                        ('name_dscc', '=', d.name_bc.id),
                                                        ('thoigian_bd_dscc', '>', datetime.combine(ngay,gio)),
                                                        ('thoigian_bd_dscc', '<', ngay + timedelta(days=1))])
                if ds_cc:
                    for e in ds_cc:
                        if not e.trangthai_dscc:
                            e.trangthai_dscc = 'trunglap'
                
            a.state = 'daduyet_ccn'
        return True

#-----------------------------------------
# Danh Sách Chấm Công
#-----------------------------------------
class DanhSachChamCong(models.Model):
    _name = "ds.chamcong"
    _description = "Danh sách Chấm công được copy từ 'Lịch làm việc' của model planning_slot.py"
    
    name_dscc = fields.Many2one('hr.employee', 'Nhân Viên')   
    ca_lam_viec_dscc = fields.Many2one('planning.role', 'Ca Làm Việc')
    thoigian_bd_dscc = fields.Datetime('Ngày Bắt Đầu')
    thoigian_kt_dscc = fields.Datetime('Ngày Kết Thúc')
    thamchieu_dscc = fields.Selection([
            ('cc_ca', 'C.C theo Ca'),
            ], string="Tham Chiếu")

    trangthai_dscc = fields.Selection([
            ('hoantat', 'Hoàn Tất'),
            ('trunglap', 'Trùng Lặp'),
            ('xacnhan', 'Xác Nhận'),
            ('xem_bc', 'Xem Báo Cáo'),
            ], string="Trạng Thái")
    
    #ondelete="cascade" : khi xóa record từ model 'chamcong' hoặc 'chamcong.ngay' thì sẽ tự động xóa record ở model 'ds.chamcong'
    chamcong_kn_dscc = fields.Many2one('cham.cong', ondelete="cascade")
    ccn_kn_dscc = fields.Many2one('chamcong.ngay', ondelete="cascade")
    
#-----------------------------------------
# Ca Làm Việc
#-----------------------------------------
class CaLamViec(models.Model):
    _name = "ca.lamviec"
    _description = "Model Ca làm việc chứa các khoảng thời gian Vào và Ra để so sánh với thời gian Vào/Ra của model Dữ Liệu"
    
    name_clv = fields.Many2one('planning.role', 'Ca làm việc')
    
    giovao1 = fields.Float('Giờ Vào Từ')
    giovao2 = fields.Float('Đến')
    giora1 = fields.Float('Giờ Ra Từ')
#    giora2 = fields.Float('Cho Đến')
    
#-----------------------------------------
# Lịch Sử Chấm Công
#-----------------------------------------        
class LichSuChamCong(models.Model):
    _name = "ls.chamcong"
    _description = "Lịch sử chấm công dựa theo model 'ds_chamcong.py' và Dữ liệu của máy chấm công"
    
    name = fields.Many2one('hr.employee', 'Nhân Viên')    
    ca_lam_viec_lscc = fields.Many2one('planning.role', 'Ca Làm Việc')
    ngay_bd_lscc = fields.Date('Ngày Bắt Đầu')
    ngay_kt_lscc = fields.Date('Ngày Kết Thúc')
    time1_lscc = fields.Float('Giờ Vào')    
    time2_lscc = fields.Float('Giờ Ra')
    chucdanh_lscc = fields.Char(related='name.job_title', string='Chức Danh', store=True)   
    thamchieu_lscc = fields.Selection([
            #Dành cho chấm công theo Nhân viên
            ('chuaxong', 'Chưa Chấm Công'),
            ('chamcong_nv', 'Chấm công theo Nhân viên'),
            ('late_ccnv', 'Đi Trễ (CCNV)'),
            ('early_ccnv', 'Về Sớm (CCNV)'),
            ('late_early_ccnv', 'Đi Trễ. Về Sớm (CCNV)'),
            #Dành cho Lịch sử Chấm công
            ('chogiora', 'Chờ dữ liệu Giờ Ra'),
            ('late', 'Đi Trễ'),
            ('early', 'Về Sớm'),
            ('late_early', 'Đi Trễ, Về Sớm !')
            ], string="Tham Chiếu")
    
    ngaycong = fields.Float('Ngày Công')    
    tong_ngaycong = fields.Float(compute='_tinh_ngaycong', string='Tổng Ngày Công')
    
    ccnv_kn_lscc = fields.Many2one('chamcong.nv')    
    chamcong_kn_lscc = fields.Many2one('cham.cong')
    ccn_kn_lscc = fields.Many2one('chamcong.ngay')
    
    @api.depends('ngaycong')
    def _tinh_ngaycong(self):
        #Tính tổng ngày công (dựa theo field ngày công của tất cả record) của TỪNG nhân viên theo TỪNG tháng
        for rec in self:
            #xác định tên của từng nhân viên để filter
            ten_nv = rec.name
            #xác định ngày cuối cùng của tháng, năm dựa theo calendar đã import
            last_day = calendar.monthrange(rec.ngay_bd_lscc.year, rec.ngay_bd_lscc.month)[1]
            #xác định ngày bắt đầu của tháng
            rec_start = rec.ngay_bd_lscc.replace(day=1)
            #xác định ngày kết thúc của tháng
            rec_end = rec.ngay_bd_lscc.replace(day=last_day)            
            #Tìm nạp (mapped) TẤT CẢ các record có chứa value của field 'ngaycong' thỏa mãn điều kiện filter,
            #và cộng TẤT CẢ value của field 'ngaycong' lại và cho vào biến 'sum_ngaycong'
            #Điều kiện filter: chỉ giữ lại những record có CÙNG TÊN VÀ TRONG 1 THÁNG ĐÓ (BAO GỒM CẢ NGÀY ĐẦU VÀ NGÀY CUỐI)
            sum_ngaycong = sum(self.filtered(
                lambda x: rec_start <= x.ngay_bd_lscc and rec_end >= x.ngay_bd_lscc and ten_nv == x.name).mapped('ngaycong'))
            #ghi kết quả của biến sum_ngaycong vào biến tong_ngaycong
            rec.tong_ngaycong = sum_ngaycong
                
        return True
    
#-----------------------------------------
# Báo Cáo
#-----------------------------------------    
class BaoCao(models.Model):
    _name = "bao.cao"
    _description = "Báo cáo danh sách các nhân viên không thỏa điều kiện để chấm công"
    
    name_bc = fields.Many2one('hr.employee', 'Nhân viên')    
    ca_lam_viec_bc = fields.Many2one('planning.role', 'Ca làm việc')    
    ngay_bd_bc = fields.Date('Ngày Bắt Đầu')
    ngay_kt_bc = fields.Date('Ngày Kết Thúc')
    giovao_bc = fields.Float('Giờ Vào')
    giora_bc = fields.Float('Giờ Ra')
    trangthai_bc = fields.Selection([
            #Dành cho Chấm Công theo Nhân Viên
            ('done', 'Đã Xử Lý')
            ], string="Trạng thái")
    
    chucdanh_bc = fields.Char(related='name_bc.job_title', string='Chức Danh', store=True)
    thamchieu_bc = fields.Selection([
            ('no_data', 'Không có Dữ liệu chấm công'),
            ('no_data_vao', 'Không có Dữ liệu Giờ Vào'),
            ('no_data_ra', 'Không có Dữ liệu Giờ Ra'),
            ('no_pl', 'Không có trong Lịch Làm Việc')
            ], string="Tham chiếu")
    
    chamcong_kn_bc = fields.Many2one('cham.cong')
    ccn_kn_bc = fields.Many2one('chamcong.ngay')

#-----------------------------------------
# Bảng Chấm Công
#-----------------------------------------    
class BangChamCong(models.Model):
    _name = "bang.chamcong"
    _description = "Thể hiện chi tiết Bảng Chấm Công, phụ thuộc vào Chấm Công"
    
    name = fields.Many2one('hr.employee', 'Nhân viên')
    
    start_date = fields.Date(default=fields.Date.today)
    end_date = fields.Date(string='End Date', store=True, compute='_get_end_date', inverse='_set_end_date')
    duration = fields.Float(digits=(6, 2), help="Duration in days")
    
    @api.depends('start_date', 'duration')
    def _get_end_date(self):
        for r in self:
            if not (r.start_date and r.duration):
                r.end_date = r.start_date
                continue

            # Add duration to start_date, but: Monday + 5 days = Saturday, so
            # subtract one second to get on Friday instead
            duration = timedelta(days=r.duration, seconds=-1)
            r.end_date = r.start_date + duration
            
    def _set_end_date(self):
        for r in self:
            if not (r.start_date and r.end_date):
                continue

            # Compute the difference between dates, but: Friday - Monday = 4 days,
            # so add one day to get 5 days instead
            r.duration = (r.end_date - r.start_date).days + 1
