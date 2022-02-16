# 对文件的操作方法
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
#import reportlab.pdfbase.ttfonts
from datetime import datetime
import os,time
from PyPDF4 import PdfFileReader, PdfFileMerger, PdfFileWriter
import asyncio

# 读取目录内所有文件
class fileModel():
    def __init__(self):
        pass
    # 读取excel内容

    @staticmethod
    def readExcel():
        pass

    # 筛选出指定目录中特定文件类型的文件，返回文件名、文件路径
    @staticmethod
    def path_scan(path, type):
        # root 表示当前正在访问的文件夹路径
        # dirs 表示该文件夹下的子目录名list
        # files 表示该文件夹下的文件list
        allfile = []
        for root, dir, files in os.walk(path):
            for file in files:
                firstname, lastname = os.path.splitext(file.upper())
                if lastname in type:
                    allfile.append([file, os.path.join(root, file)])
            return allfile

    # pdf加水印,根据页面大小确定对应水印；添加创建时间，作者，标题，关键词；申请单号，申请时间
    # 上传时加水印；添加时间、作者、归档时间、阶段标记；修改制作程序；
    # 申请时添加申请时间，并将文件组合在一起,并加密
    @staticmethod
    def add_watermark(file_stream, mark, out, info):
        """把水印添加到pdf中"""
        pdf_output = PdfFileWriter()
        #input_stream = open(pdf_file_in, 'rb')
        pdf_input = PdfFileReader(file_stream, strict=False)
        pdf_info = pdf_input.getDocumentInfo()
        # 获取PDF文件的页数
        pageNum = pdf_input.getNumPages()

        # 读入水印pdf文件
        pdf_watermark = PdfFileReader(open(mark, 'rb'), strict=False)
        # 给每一页打水印
        for i in range(pageNum):
            page = pdf_input.getPage(i)
            page.mergePage(pdf_watermark.getPage(0))
            # page.compressContentStreams()  # 压缩内容
            pdf_output.addPage(page)

        # 加密码
        #pdf_output.encrypt(user_pwd='', owner_pwd='12345',use_128bit=True)
        pdf_output.addMetadata(pdf_info)
        # 可以更改一些属性值
        pdf_output.addMetadata({'/Comment': '新的属性', '/Title': '新的标题'})
        pdf_output.write(open(out, 'wb'))

# 创建水印文件2
def create_watermark(page,stage,fileno):
    print('水印开始...' + str(datetime.now()))
    # 默认大小为21cm*29.7cm
    name = str(time.time())+'.pdf'    
    c = canvas.Canvas(name, pagesize=(page[0]*mm, page[1]*mm))
    # 移动坐标原点(坐标系左下为(0,0))
    # 坐标单位默认是点，1mm等于2.834; 1inch等于72;
    #c.translate(10*cm, 5*cm)
    # 首先判断页面大小，决定水印位置
    if page[0]<220:
        c.translate((page[0]-45)*mm, (page[1]-33)*mm)
    else:
        c.translate((page[0]-40)*mm, (page[1]-25)*mm)

    # 设置字体格式与大小,中文需要加载能够显示中文的字体，否则就会乱码，注意字体路径
    try:
        pdfmetrics.registerFont(TTFont('kaishu', 'simkai.TTF'))

        c.setFont('kaishu', 24)
    except:
        # 默认字体，只能够显示英文
        c.setFont("Helvetica", 24)

    
    # 指定描边的颜色
    c.setStrokeColorRGB(255, 0, 0)    
    # 指定填充颜色
    c.setFillColorRGB(0, 0, 0)
    # 画一个矩形,边框的位置和大小fill=0不填充
    c.setLineWidth(0.7*mm)
    c.rect(0, 0, 30*mm, 15*mm, fill=0)

    c.rotate(0)
    # 指定填充颜色
    c.setFillColorRGB(255, 0, 0)
    # 设置透明度，1为不透明
    #c.setFillAlpha(0.3)

    # 画几个文本，注意坐标系旋转的影响
    c.drawString(13, 20, stage)
    #c.setFillAlpha(0.6)

    c.setFont("Helvetica", 11)
    createdate = (datetime.now()).strftime("%Y-%m-%d")
    c.drawString(15, 5, createdate)

    c.setFont("Helvetica", 8)
    #tag = str(int(time.time()))  # 给文件加时间戳
    c.drawString(5, 45, fileno)

    # 关闭并保存pdf文件
    c.save()
    print('水印结束...' + str(datetime.now()))
    return name

def merge(pdf_input, mark):    
    pageNum = pdf_input.getNumPages()
    pdf_output = PdfFileWriter()
    pdf_watermark = PdfFileReader(open(mark, 'rb'), strict=False)
    for i in range(pageNum):
        page = pdf_input.getPage(i)
        page.mergePage(pdf_watermark.getPage(0))        
        pdf_output.addPage(page)    
    return pdf_output

def savepdf(pdf_output, file_path):    
    pdf_output.write(open(file_path, 'wb'))    

#在PDF上加水印，输入为文件流
async def add_watermark(file_path,stage,fileno):
    """把水印添加到pdf中"""
    #print('文件开始...' + str(datetime.now()))
    
    pdf_input = PdfFileReader(file_path)
    if pdf_input.isEncrypted:
        return 
    pdf_info = pdf_input.getDocumentInfo()
    w, h = pdf_input.getPage(0).mediaBox[2:]
    # 页面尺寸转换为毫米
    page = (int(w)*0.3528, int(h)*0.3528)

    # 创建水印文件
    #create_watermark(page,stage,fileno)
    mark = create_watermark(page, stage, fileno)
    #mark=await asyncio.get_event_loop().run_in_executor(None, create_watermark, page, stage, fileno)
    # 读入水印pdf文件
    #mark='d:/mark.pdf'    
    
    pdf_output = await asyncio.get_event_loop().run_in_executor(None, merge, pdf_input, mark)
    #pdf_output = merge(file_path, mark)
    # 加密码
    pdf_output.encrypt(user_pwd='', owner_pwd='12345',use_128bit=True)
    pdf_output.addMetadata(pdf_info)
    # 可以更改一些属性值
    #pdf_output.addMetadata(info)
    #savepdf(pdf_output, file_path)
    await asyncio.get_event_loop().run_in_executor(None, savepdf, pdf_output, file_path)    
    
    #print('文件结束...' + str(datetime.now()))


def files_add_mark_async(files):
    print('异步start..' + str(datetime.now()))
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    loop = asyncio.get_event_loop()
    tasks=[]
    
    for file in files:
        tasks.append(add_watermark(file[0], file[1], file[2]))        

    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()
    print('异步end..' + str(datetime.now()))

if __name__=='__main__':
    add_watermark('d:/a4.pdf','小 批','210010')
