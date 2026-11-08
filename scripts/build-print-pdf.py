"""Build the two A4 booklets from build-print.mjs's shared print model.
Requires reportlab, Pillow and PyMuPDF. Fonts default to Windows Arial/Georgia; override BB_FONT_DIR.
"""
import json,os,sys,html
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from PIL import Image as PILImage
from io import BytesIO
from reportlab.lib.utils import ImageReader
ROOT=Path(__file__).resolve().parent.parent
DATA=json.loads((ROOT/'print/print-data.json').read_text(encoding='utf-8'))
FONT_DIR=Path(os.environ.get('BB_FONT_DIR',str(ROOT/'.print-fonts') if (ROOT/'.print-fonts').exists() else 'C:/Windows/Fonts'))
for name,file in [('Body','arial.ttf'),('BodyBold','arialbd.ttf'),('BodyItalic','ariali.ttf'),('Title','georgia.ttf'),('TitleItalic','georgiai.ttf')]:
    pdfmetrics.registerFont(TTFont(name,str(FONT_DIR/file)))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='BodyBold',italic='BodyItalic',boldItalic='BodyBold')
INK=colors.HexColor('#192a27'); ACCENT=colors.HexColor('#a54932'); LINE=colors.HexColor('#bec9bd'); PALE=colors.HexColor('#edf1ea')
W,H=A4; LEFT=42.5; WIDTH=W-85
STYLES={
 'body':ParagraphStyle('body',fontName='Body',fontSize=11,leading=14.6,textColor=INK),
 'small':ParagraphStyle('small',fontName='Body',fontSize=9,leading=12,textColor=INK),
 'tiny':ParagraphStyle('tiny',fontName='Body',fontSize=7.5,leading=10,textColor=colors.HexColor('#505950')),
 'intro':ParagraphStyle('intro',fontName='Body',fontSize=12,leading=16,textColor=INK),
 'h1':ParagraphStyle('h1',fontName='Title',fontSize=29,leading=32,textColor=INK),
 'h2':ParagraphStyle('h2',fontName='BodyBold',fontSize=13,leading=17,textColor=INK),
 'h3':ParagraphStyle('h3',fontName='BodyBold',fontSize=11,leading=14,textColor=INK),
 'tag':ParagraphStyle('tag',fontName='TitleItalic',fontSize=13,leading=16,textColor=colors.HexColor('#745d45')),
 'table':ParagraphStyle('table',fontName='Body',fontSize=10.5,leading=13.4,textColor=INK),
 'tablebold':ParagraphStyle('tablebold',fontName='BodyBold',fontSize=10.3,leading=13.3,textColor=INK),
}
def e(s):return html.escape(str(s),quote=True)
def link(label,url):return '<link href="'+e(url)+'">'+e(label)+'</link>'
def money(n):return f'{n:,}'
class Book:
 def __init__(self,filename,title,label):
    self.c=canvas.Canvas(str(ROOT/'print'/filename),pagesize=A4,pageCompression=1,invariant=1)
    self.c.setTitle(title+' | Brands Bangkok');self.c.setAuthor('Brands Bangkok')
    self.label=label;self.n=0;self.y=0;self.compact=False
 def start(self):
    if self.n:self.finish()
    self.n+=1;c=self.c
    c.setFillColor(ACCENT);c.setFont('Title',30);c.drawString(LEFT,H-54,'B.')
    c.setFillColor(INK);c.setFont('BodyBold',13.5);c.drawString(LEFT+46,H-42,'Brands Bangkok')
    c.setFont('Body',8);c.drawString(LEFT+46,H-55,'Fashion. Retail. Possibility.')
    c.setStrokeColor(LINE);c.setLineWidth(.6);c.line(LEFT,H-66,W-LEFT,H-66);self.y=H-84
 def p(self,text,style='body',after=8,x=None,width=None):
    p=Paragraph(text,STYLES[style]); w,h=p.wrap(width or WIDTH,H)
    if x is None:
      if self.y-h<58:raise ValueError(f'Page overflow: {self.label} page {self.n}: {text[:75]} at {self.y-h}')
      p.drawOn(self.c,LEFT,self.y-h);self.y-=h+after
    else:p.drawOn(self.c,x,self.y-h)
    return h
 def heading(self,label,title,lead):
    self.c.setFillColor(ACCENT);self.c.setFont('BodyBold',8.5);self.c.drawString(LEFT,self.y,e(label).upper().replace('&amp;','&'));self.y-=19
    self.p(e(title),'h1',9);self.p(e(lead),'intro',10)
 def h2(self,text):
    self.y-=5;self.p(e(text),'h2',5)
 def table(self,headers,rows,widths,numeric=False,group=False):
    cells=[]
    for ri,row in enumerate([headers]+rows):
      cells.append([Paragraph(str(value),ParagraphStyle('cell',parent=STYLES['tablebold' if ri==0 else 'table'],alignment=2 if numeric and col >= (2 if group else 1) else 0)) for col,value in enumerate(row)])
    tab=Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT')
    cmds=[('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),PALE),('LINEABOVE',(0,0),(-1,0),1,INK),('LINEBELOW',(0,0),(-1,-1),.4,LINE),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),4 if self.compact else 7),('BOTTOMPADDING',(0,0),(-1,-1),4 if self.compact else 7)]
    if group:
      for row in (1,4,7):cmds.append(('LINEABOVE',(0,row),(-1,row),.8,colors.HexColor('#92a491')))
    tab.setStyle(TableStyle(cmds)); w,h=tab.wrap(WIDTH,H)
    if self.y-h<58:raise ValueError(f'Table overflow {self.label} page {self.n}')
    tab.drawOn(self.c,LEFT,self.y-h);self.y-=h+10
 def rate(self):
    r=DATA['rate'];self.y-=3
    self.c.setStrokeColor(LINE);self.c.line(LEFT,self.y,W-LEFT,self.y);self.y-=10
    self.p(f'<b>Currency conversion:</b> 1 THB = ¥{r["rate"]} · {r["displayDate"]} · '+link(r['sourceName'],r['sourceUrl'])+'<br/>Thai baht × '+str(r['rate'])+' = Japanese yen. Round to the nearest yen.','small',0)
 def finish(self):
    self.c.setStrokeColor(LINE);self.c.line(LEFT,44,W-LEFT,44)
    self.c.setFillColor(colors.HexColor('#596259'));self.c.setFont('Body',8);self.c.drawString(LEFT,29,'Brands Bangkok · '+self.label);self.c.drawRightString(W-LEFT,29,f'{self.n} / 6')
    self.c.showPage()
 def save(self):self.finish();self.c.save()
def location_book():
 from location_design import build
 build(Book,DATA,ROOT)
def rental_book():
 b=Book('brands-bangkok-rental-rates.pdf','Retail spaces & rates','Retail spaces & rates');b.start();b.compact=True
 b.heading('Business services','Retail spaces & rates.','Space for your next collection. Rental options at five Bangkok shopping centres.')
 b.p('Rates vary by location, season, length of stay and space size. Each location has its own rate page.','small',7)
 b.h2('Space and stay options')
 b.table(['Option','Choices'],[['Space size','Compact · 20 m² / Standard · 40 m² / Large · 60 m²'],['Length of stay','1 week · 7 days / 2 weeks · 14 days / 4 weeks · 28 days'],['Season','Feb – Apr / May – Jul / Aug – Oct / Nov – Jan']],[115,WIDTH-115])
 b.p('Any listed space size can be combined with any listed stay and season.','small',3)
 b.h2('Setup options');b.table(['Setup','What is included'],[[e(s['label']),e(s['includes'])]for s in DATA['setups']],[115,WIDTH-115])
 b.h2('Optional extras')
 b.table(['Service','Price'],[['Extra stock storage','THB 300 per day<br/>7 days: 2,100 · 14 days: 4,200 · 28 days: 8,400'],['Printed brand signs','THB 6,000 · One-time charge']],[150,WIDTH-150])
 b.h2('Your total before opening');b.p('Space rental + setup + optional extras + refundable deposit.','body',8)
 for t in DATA['terms']:b.p(e(t),'small',5)
 b.rate()
 for v in DATA['venues']:
    b.start();b.heading(v['area']+' · Retail space',v['name'],'Short-term retail · All table prices are in Thai baht (THB).')
    b.h2('Space rental for the full stay')
    b.p('Rental prices below cover the full stay. Other charges are added separately.')
    b.table(['Space','Stay','Feb – Apr','May – Jul','Aug – Oct','Nov – Jan'],[[str(r['area'])+' m²',str(r['days'])+' days']+[money(n)for n in r['values']]for r in v['rents']],[55,64]+[(WIDTH-119)/4]*4,True,True)
    b.h2('Setup and refundable deposit')
    b.p('Choose one setup. Setup is charged once. The refundable deposit is separate.')
    b.table(['Space','Space only','Retail setup','Brand display','Refundable<br/>deposit'],[[str(r['area'])+' m²']+[money(r[k])for k in ['space','retail','brand','deposit']]for r in v['charges']],[55]+[(WIDTH-55)/4]*4,True)
    b.p('Setup descriptions and full rental terms are on page 1.','small',5)
    b.h2('Optional extras')
    b.p('Stock storage: THB 300 per day. Printed brand signs: THB 6,000 once.','body',8)
    b.p('<b>Total before opening = rent + setup + extras + deposit.</b>','body',10)
    b.p('The deposit is returned if there is no damage or unpaid charge. Staff, stock, payment equipment, electricity and taxes are not included. Exact dates and position are confirmed before booking. All rental terms are on page 1.','small',8)
    b.rate()
 b.save()
if __name__=='__main__':
 location_book();rental_book()
 import pymupdf
 vector_dir=ROOT/'print/location-pages';vector_dir.mkdir(exist_ok=True)
 with pymupdf.open(ROOT/'print/brands-bangkok-locations.pdf') as document:
  for i,page in enumerate(document,1):
   (vector_dir/f'page-{i}.svg').write_text(page.get_svg_image(text_as_path=True),encoding='utf-8')
 print('Built two 6-page A4 PDF booklets.')
