import tkinter as tk
from tkinter import ttk
import re
import logging
import traceback
import sys
import tkinter.messagebox

class main_GUI(object):   # 把整个GUI程序 封装在一个类里面
    def __init__(self, master=None):    # 窗体定义，基本函数，其它的都靠它来触发
        self.root = master

        # 因为tk中异常只在控制台输出，也不会抛出，所以要重写异常处理，增加logging记录功能
        tk.Tk.report_callback_exception = self.show_error

        #w, h = self.root.maxsize()
        #self.root.geometry("{}x{}".format(w, h))
        self.root.geometry('1024x600')        
        
        self.creatPage()
        self.menu_input()
        self.menu_tree()
        self.menu_bar()
        #self.add_input_list()
        #ttk.Style().theme_use('clam')   #('clam','alt','default','classic')

    def show_error(self, exc, val, tb):  # 在原异常处理下增加了logging
        print("Exception in Tkinter callback", file=sys.stderr)
        sys.last_type = exc
        sys.last_value = val
        sys.last_traceback = tb
        traceback.print_exception(exc, val, tb)

        err = 'Exception in Tkinter callback\n'
        for item in traceback.format_exception(exc, val, tb):
            err = err+item
        logging.warning(err)
        self.lab_text.set('')
        tkinter.messagebox.showerror(title='程序错误', message=err)

    def creatPage(self,):    # 把界面内容放在一个一起了，便于修改
        frame_input = ttk.Frame(self.root)
        frame_lable = ttk.Frame(self.root)
        frame_table = ttk.Frame(self.root)
        frame_input.pack()
        frame_lable.pack()
        frame_table.pack(padx=10, expand='yes', fill='both')

        self.t1 = tk.StringVar()
        self.t2 = tk.StringVar()

        self.search_var = tk.StringVar()
        #self.search_input = ttk.Entry(frame_input, width=30, textvariable=self.search_var,font=("微软雅黑", 12))
        self.search_input = ttk.Combobox(
            frame_input, width=30, textvariable=self.search_var, font=("微软雅黑", 12))

        self.search_input.pack(padx=10, pady=10, side='left')
        self.search_input.bind('<Button-3>', self.R_click_en1)
        self.search_input.bind("<Return>", self.search_input_enter)

        

        #对于和事件绑定的函数,会自动给个event参数,所有在定义时要加上event参数

        self.find_iid = self.find_yeild()
        ttk.Button(frame_input,
                   text='物料/图纸查询', command=self.search_input_enter).pack(padx=20, pady=10, side='left')

        ttk.Button(frame_input,
                   text='表内查找\下一个', command=self.find_treebom_GUI).pack(padx=20, pady=10, side='left')

        

        self.lab_text = tk.StringVar()
        ttk.Label(frame_table, textvariable=self.lab_text,
                  font=("微软雅黑", 12, 'italic')).pack(pady=5)

        self.tev = ttk.Treeview(frame_table, columns=(
            '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11'), selectmode='browse')

        self.tree = {}
        self.tree_select = {}
        self.vbar = ttk.Scrollbar(frame_table,
                                  orient='vertical',
                                  command=self.tev.yview)
        self.tev.configure(yscrollcommand=self.vbar.set)
        self.vbar.pack(side='right', fill='y')

        self.hbar = ttk.Scrollbar(
            frame_table, orient='horizontal', command=self.tev.xview)
        self.tev.configure(xscrollcommand=self.hbar.set)
        self.hbar.pack(side='bottom', fill='x')

        self.tev.pack(expand='yes', fill='both')
        self.tev.bind('<Button-3>', self.R_click_tree)

    def read_file(self,):  #读取本地的一些信息，类似cookies
        pass

    def add_input_list(self,search=None):
        '向搜索框添加搜索关键词，并写入文本文件中；'
        cmb_re = list(self.search_input['value'])
        if not cmb_re:
            cmb_re = []

        if search in cmb_re:
            cmb_re.remove(search)
        cmb_re.insert(0, search)
        if len(cmb_re) > 12:
            del cmb_re[-1]
        self.search_input['value'] = cmb_re


    def menu_input(self,):        # 输入框的右键菜单
        def onpaste(event=None):
            self.en1.event_generate('<<Paste>>')

        def copy(event=None):
            self.en1.event_generate("<<Copy>>")

        def cut(event=None):
            self.en1.event_generate("<<Cut>>")

        self.menu_input = tk.Menu(self.root, tearoff=0)
        self.menu_input.add_command(label="剪切", command=cut)
        self.menu_input.add_separator()
        self.menu_input.add_command(label="复制", command=copy)
        self.menu_input.add_separator()
        self.menu_input.add_command(label="粘贴", command=onpaste)


    def menu_bar(self,):   # 定义菜单栏
        def creat_file_menu(bar):
            m_file = tk.Menu(bar, tearoff=0)  # 创建2级菜单组
            # mabr上添加一个标签,链接到file_m
            bar.add_cascade(label='读取EXCEL文件', menu=m_file)

            m_file.add_separator()
            m_file.add_command(label='导入ERP BOM',
                                command=lambda: self.read_bom_GUI(tp='BATCH'))
            m_file.add_separator()
            m_file.add_command(
                label='导入设计BOM', command=lambda: self.read_bom_GUI(tp='DESIGN'))
            m_file.add_separator()
            m_file.add_command(
                label='导入定制BOM', command=lambda: self.read_bom_GUI(tp='CUSTOM'))
            m_file.add_separator()
            m_file.add_command(
                label='导入实验BOM', command=lambda: self.read_bom_GUI(tp='EXPER'))
            m_file.add_separator()
            m_file.add_command(
                label='导入设计更改清单', command=self.read_design_change_GUI)
            m_file.add_separator()
            m_file.add_command(
                label='仅读取BOM', command=lambda: self.read_temp_GUI(tp='TEMP'))
            m_file.add_separator()
            m_file.add_command(label='更新物料库', command=self.read_code_GUI)
            m_file.add_separator()
            m_file.add_command(
                label='导出模板', command=self.download_template_GUI)
            m_file.add_separator()
            

        def creat_cost_menu(bar):
            m_cost = tk.Menu(bar, tearoff=0)
            m_cost.add_separator()
            m_cost.add_command(label='导入成本文件', command=self.read_cost_GUI)
            m_cost.add_separator()
            m_cost.add_command(label='成本变动物料', command=self.view_changed_cost)
            m_cost.add_separator()
            m_cost.add_command(label='重算BOM成本', command=self.recalc_tree_cost_GUI)
            m_cost.add_separator()
            m_cost.add_command(label='查看物料成本', command=self.tree_add_cost)

            bar.add_cascade(label='成本', menu=m_cost)

        def creat_view_menu(bar):
            m_view = tk.Menu(bar, tearoff=0)  # 创建2级菜单组
            

            root_b = tk.StringVar()

            

            

            m_view.add_command(label='小批 BOM', command=lambda: view_root('BATCH'))
            m_view.add_separator()

            m_view.add_command(label='试制 BOM', command=lambda: view_root('DESIGN'))
            m_view.add_separator()

            m_view.add_command(label=' 列表全部展开 ', command=lambda: self.tree_fold(unfold=True))
            m_view.add_separator()
            m_view.add_command(
                label=' 列表全部折叠 ', command=lambda: self.tree_fold(unfold=False))
            m_view.add_separator()
            m_view.add_command(
                label='BOM去除装配体', command=self.remove_assemble_GUI)

            bar.add_cascade(label=' 查看BOM ', menu=m_view)

        def creat_path_menu(bar):
            m_path = tk.Menu(bar, tearoff=0)            

            m_path.add_command(label='编辑图纸目录', command=self.view_drawpath)
            bar.add_cascade(label='图纸目录', menu=m_path)



        def creat_tool_menu(bar):
            m_tool = tk.Menu(bar, tearoff=0)
            m_tool.add_separator()
            m_tool.add_command(
                label='检查Excel编码', command=lambda: self.check_excel_GUI(tp='CHECK'))
            m_tool.add_separator()
            m_tool.add_command(
                label='计算部件数量', command=lambda: self.check_excel_GUI(tp='QTY'))

            m_tool.add_separator()
            m_tool.add_command(
                label='去除装配体', command=lambda: self.read_temp_GUI(tp='REMOVE'))
            m_tool.add_separator()
            m_tool.add_command(label='数据库操作', command=self.edit_db_GUI2)

            bar.add_cascade(label='EXCEL工具', menu=m_tool)

        def creat_about_menu(bar):
            bar.add_command(label='版本', command=self.ver)

        menu_bar = tk.Menu(self.root)  # 创建菜单组
        creat_file_menu(menu_bar)
        creat_cost_menu(menu_bar)
        creat_view_menu(menu_bar)
        creat_path_menu(menu_bar)
        
        creat_tool_menu(menu_bar)
        creat_about_menu(menu_bar)
        self.root.config(menu=menu_bar)  # 把mbar菜单组 配置到窗体;


    def menu_table(self,):    # 定义了treeview处的右键菜单内容，但菜单弹出要由post来调用
        def tree_copy(x):
            self.root.clipboard_clear()
            self.root.clipboard_append(x)

        self.menu_tree_code = tk.Menu(self.root, tearoff=0)
        self.menu_tree_code.add_command(
            label="复制", command=lambda: tree_copy(self.tree_select['item']))
        self.menu_tree_code.add_separator()
        self.menu_tree_code.add_command(
            label="复制物料信息", command=lambda: tree_copy(self.tree_select['code']+'; '+self.tree_select['draw']+'; '+self.tree_select['name']))
        self.menu_tree_code.add_separator()
        self.menu_tree_code.add_command(
            label="反查小批BOM", command=lambda: self.find_parent_GUI(self.tree_select['code'], db='BATCH'))
        self.menu_tree_code.add_separator()
        self.menu_tree_code.add_command(
            label="查询小批BOM子件", command=lambda: self.find_child_GUI(self.tree_select['code'],db='BATCH'))
        self.menu_tree_code.add_separator()
        self.menu_tree_code.add_command(
            label="反查设计BOM", command=lambda: self.find_parent_GUI(self.tree_select['code'], db='DESIGN'))
        self.menu_tree_code.add_separator()

        self.menu_tree_code.add_command(
            label="查询设计BOM子件", command=lambda: self.find_child_GUI(self.tree_select['code'], db='DESIGN'))
        self.menu_tree_code.add_separator()        
        self.menu_tree_code.add_command(label="打开图纸", command=self.open_draw_GUI)        
        self.menu_tree_code.add_separator()
        self.menu_tree_code.add_command(label="导出列表",command=self.tree_save)
        self.menu_tree_code.add_separator()
        self.menu_tree_code.add_command(
            label="查看设计更改", command=lambda: self.find_design_change([self.tree_select['code'], self.tree_select['draw']], op='OR'))

        self.menu_tree_path = tk.Menu(self.root, tearoff=0)
        self.menu_tree_path.add_command(label="添加目录", command=lambda: self.edit_path(type='ADD'))
        self.menu_tree_path.add_separator()
        self.menu_tree_path.add_command(label="删除目录", command=lambda: self.edit_path(type='DEL'))
        self.menu_tree_path.add_separator()
        self.menu_tree_path.add_command(label="重新搜索目录", command=lambda: self.edit_path(type='UPDATE'))
        self.menu_tree_path.add_separator()
        self.menu_tree_path.add_command(label="打开", command=lambda: self.open_path(self.tree_select['path']))
        self.menu_tree_path.add_separator()


#-----------------以下窗口动作触发------------------------------

    def input_click(self, event):   # 输入框绑定动作
        self.menu_input.post(event.x_root, event.y_root)   # 在事件坐标处,弹出对应的菜单

    def table_click(self, event):   # 鼠标右键绑定的动作，该程序通过前面的bind 和右键绑定在一起
        iid = self.tev.identify_row(event.y)   # 返回事件发生时鼠标坐标对应的行
        n = self.tev.identify_column(event.x)
        if iid:  # 如果鼠标所在是空,则不执行右键动作
            self.tree_select['id'] = iid    # 当右键时选中目前鼠标所在的行id
            self.tev.selection_set(iid)
            self.tree_select['x'] = event.x_root
            self.tree_select['y'] = event.y_root
            n = int(n.replace('#', ''))
            self.tree_select['item'] = self.tev.item(iid, 'values')[n-1]

            if self.tree['type'] in ('CODE', 'CODE-COST', 'BOM', 'BOM-COST', 'BOM-SINGLE'):
                self.tree_select['code'] = self.tev.item(
                    self.tev.selection(), 'values')[0]
                self.tree_select['draw'] = self.tev.item(
                    self.tev.selection(), 'values')[1]
                self.tree_select['name'] = self.tev.item(
                    self.tev.selection(), 'values')[2]

                if self.tree_select['code'] == '':
                    self.tree_select['code'] = self.tree_select['draw'] + \
                        self.tree_select['name']

                self.menu_tree_code.post(event.x_root, event.y_root)
            elif self.tree['type'] == 'PATH':
                self.tree_select['path'] = self.tev.item(
                    self.tev.selection(), 'values')[1]
                self.tree_select['file'] = self.tev.item(
                    self.tev.selection(), 'values')[0]
                self.menu_tree_path.post(event.x_root, event.y_root)

    def get_input(self,):
        search = self.search_var.get()
        if search in ('', ' ', None):
            return

        search = search.upper()  # 转大写，去首尾空格
        search=search.strip()
                
        self.add_input_list(search)

        return search.split()

    def search_input_enter(self, event=None):  # 和事件绑定的函数,在事件触发时,会自动给一个event参数,所有定义时必须加上
        '当下拉框为 所有或空时，直接进行编码库查询；否则进入选择的BOM中查询'
        search = self.get_input()
        self.find_code_View(search)

    
#-----------树形表格-----------------------------------------

    def set_tree_title(self,tev,type):        
        tree_title = {
        'CODE': ('序号', '编码', '图号', '名称', '材料', '重量', '备注',),
        'CODE-COST': ('序号', '编码', '图号', '名称', ' ', ' ', '材料成本', '人工', '费用', '单件成本', ' ', '更新日期',),
        'BOM': ('层次', '编码', '图号', '名称', '数量', '部件数量', '材料', '重量', '备注',),
        'BOM-SINGLE':('序号', '编码', '图号', '名称', '数量', '部件数量', '材料', '重量', '备注',),
        'BOM-COST': ('层次', '编码', '图号', '名称', '数量', '部件数量', '材料成本', '人工', '费用', '单件成本', '合计成本', '更新日期',),
        'PATH': ('序号', '图号', '图纸路径','图纸数量'),
        'UPDATE': ('序号','物料文件', '读取结果', '备注信息'),
        }

        title_width = {
            '序号':60,'层次':120,'编码':120, '图号':140, '名称':260, '材料':100, '重量':60,'数量':60, '部件数量':60, '备注':100,'材料成本':60, '人工':60, '费用':60, '单件成本':100,'合计成本':100, '更新日期':300,'图纸路径':400,'物料文件':300,'读取结果':120,'图纸数量':120,'备注信息':300,' ':10,
        }

        title_field={'序号':'sn','层次':'lv','编码':'code', '图号':'draw', '名称':'name', '材料':'m', '重量':'weight','数量':'q', '部件数量':'total', '备注':'remark','材料成本':60, '人工':60, '费用':60, '单件成本':'cost','合计成本':'total_cost', '更新日期':'add_time','图纸路径':'filepath','物料文件':300,'读取结果':120,'图纸数量':120,'备注信息':300,' ':10,}
        
        
        for n in range(1, 12):  #初始化列宽
            tev.column(str(n), width=40)
        self.tree['field']=[]

        if type in tree_title:
            self.tree['col']=tree_title[type]
            
            for n, name in enumerate(tree_title[type]):
                if n == 0:
                    n = '#' + str(n)
                
                tev.heading(str(n), text=name,command=lambda _n=str(n): self.tree_sort(self.tev, _n, False))
                tev.column(str(n), width=title_width[name])

                self.tree['field'].append(title_field[name])


    def tree_sort(self,tev, col, reverse):
        '用tree-bom列表的项进行排序，再移动treeview显示内容；对多层次也可使用'            
        if col == '#0':
            col = '0'
        l = [(k[int(col)], k[-1]) for k in self.tree['bom']]
        #l = [(tv.set(k, col), k) for k in tv.get_children('')]   #多层次下只能得到最顶层父项id
        if col == '0':
            pt = {0:''}
            for (lv,k) in l:
                pt[lv] = k
                tev.move(k, pt[lv-1], 99999)   #重新构建层次关系               
        else:
            try:
                l.sort(key=lambda t: t[0], reverse=reverse)
            except:  #如果排序错误，说明存在混合格式，把所有字符串当做0，重新排序
                for n, (val, k) in enumerate(l):
                    if not isinstance(val, (int, float)):
                        l[n]=(0,k)
                l.sort(key=lambda t: t[0], reverse=reverse)
            
            for index, (val, k) in enumerate(l):
                tev.move(k, '', index)    #移动的同时删除了层次关系

        tev.heading(col, command=lambda: self.tree_sort(tev, col, not reverse))
        tev.see(tev.selection())    #把选择的行显示出来


    def tree_out(self,bom,type='BOM'):  #输入为字典列表,根据field填入
        for item in self.tev.get_children():  # 对treeview进行清空
            self.tev.delete(item)      
        
        iid_bom=[]        
        
        fields = self.tree.get('field','')

        piid={'ROOT':''}
        sn={'ROOT':0}
        for item in bom:
            # 按parent去找设置层次，按field填入数据
            if item['parent'] not in piid:
                item['piid']=''
            else:
                item['piid']=piid[item['parent']]
            
            if item['parent'] not in sn:
                sn['ROOT']+=1                
                item['sn_n']=sn['ROOT']
            else:
                sn[item['parent']]+=1
                item['sn_n'] = sn[item['parent']]

            sn[item['code']]=0

            row=[]
            for key in fields:  # 组合表格内容
                if key not in item:
                    row.append('')
                else:
                    if key=='code' and item['code']==item.get('draw','')+item.get('name',''):
                        row.append('')
                    elif item[key]==0:
                        row.append('')
                    else:
                        row.append(item.get(key,''))

            item['iid']=self.tev.insert(item['piid'],'end',text=str(item['sn_n']), values=row)
            piid[item['code']]=item['iid']

        self.tree['bom']= iid_bom


    def tree_update(self,):
        pass

    def tree_bold(self, iid_list):
        '将给出的iid加粗显示,并展开'
        if 'bom' not in self.tree:
            return

        for item in self.tree['bom']:
            iid = item[-1]
            self.tev.item(iid, tag='', open=False)

            if item[:len(iid_list[0])] in iid_list:
                self.tev.item(iid, tag='tar', open=True)
                iid_p = iid
                for n in (1, 2, 3):
                    iid_p = self.tev.parent(iid_p)
                    self.tev.item(iid_p, open=True)

        self.tev.tag_configure(
            'tar', foreground='blue', background='red', font=('宋体', 10, 'bold'))


    def tree_fold(self, unfold=True):
        if self.tree['bom']:
            for k in self.tree['bom']:
                self.tev.item(k[-1], open=unfold)


    def tree_save(self,):
        def get_tev_title():
            t = {'name': [], 'width': []}
            for n in range(0, 12):
                if n == 0:
                    n = '#0'
                t['name'].append(self.tev.heading(str(n),)['text'])
                t['width'].append(self.tev.column(str(n),)['width'])
            return t

        file = tk.filedialog.asksaveasfilename(defaultextension=".xlsx", title='保存文件',
                                               filetypes=[('xlsx', '*.xlsx')])
        col_tit = get_tev_title()
        rst = self.mod.save_to_excel(
            file, self.tree['bom'], self.lab_text.get(), col_tit)

        if 'error' in rst:
            self.lab_text.set(rst['error'])
        else:
            self.lab_text.set('已成功导出到文件：' + file)
            startfile('file:'+file)

#-----------------以下窗口视图函数--------------------------------

    def find_code_View(self,search): #物料查询视图
        pass

    def find_child_View(self,search): #物料查询视图
        pass

    def find_parent_View(self, search):  # 物料查询视图
        pass
