"""Premium, individually composed location pages. Text comes from print-data.json."""
import json,html
from pathlib import Path
from io import BytesIO
from PIL import Image,ImageOps
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.utils import ImageReader
W,H=A4
def e(s):return html.escape(str(s),quote=True)
def colour(s):return colors.HexColor(s)
PALETTES={
 'centralworld':('#972f3e','#292c35','#f6eeeb'),
 'siam-center':('#684392','#352840','#f1ecf6'),
 'terminal-21-asok':('#167479','#1a354b','#edf3f2'),
 'siam-paragon':('#9b7941','#182f50','#f8f5ee'),
 'central-embassy':('#876c43','#25483c','#f5f3e9')
}
class Page:
 def __init__(self,c,root,v=None):
  self.c=c;self.root=root;self.v=v
  self.accent,self.ink,self.pale=PALETTES.get(v['slug'] if v else '',('#a54932','#192a27','#f4f1e9'))
  self.bottom=0
 def rect(self,x,t,w,h,fill):
  self.c.setFillColor(colour(fill));self.c.rect(x,H-t-h,w,h,stroke=0,fill=1)
 def line(self,x,t,w,col=None,weight=.7):
  self.c.setStrokeColor(colour(col or self.accent));self.c.setLineWidth(weight);self.c.line(x,H-t,x+w,H-t)
 def text(self,s,x,t,w,font='Body',size=11,leading=14.5,col=None,align=0):
  style=ParagraphStyle('part',fontName=font,fontSize=size,leading=leading,textColor=colour(col or self.ink),alignment=align)
  p=Paragraph(s,style);_,height=p.wrap(w,H)
  if t+height>768:raise ValueError(f"Text overflows {self.v and self.v['slug']}: {s[:50]} at {t+height}")
  p.drawOn(self.c,x,H-t-height);self.bottom=max(self.bottom,t+height);return t+height
 def title(self,s,x,t,w,size=38,align=0):
  return self.text(s,x,t,w,'Title',size,size*1.08,align=align)
 def label(self,s,x,t,w):
  return self.text(e(s.upper()),x,t,w,'BodyBold',8.5,11,col=self.accent)
 def brand(self):
  self.text('B.',42,25,36,'Title',28,30,col=self.accent)
  self.text('Brands Bangkok',83,29,300,'BodyBold',12,15)
  self.text('Fashion. Retail. Possibility.',83,46,300,'Body',7.5,10)
  self.line(42,66,W-84,'#d4d7d0',.5)
 def photo(self,record,x,t,w,h,label=True):
  im=Image.open(self.root/record['file']).convert('RGB')
  im=ImageOps.fit(im,(int(w*2.4),int(h*2.4)),method=Image.Resampling.LANCZOS,centering=(.5,.5))
  buf=BytesIO();im.save(buf,format='JPEG',quality=90,optimize=True)
  self.c.drawImage(ImageReader(BytesIO(buf.getvalue())),x,H-t-h,width=w,height=h)
  if label:
   cap=e(record['caption'])
   self.rect(x,t+h-18,w,18,self.ink)
   self.text(cap,x+8,t+h-14,w-16,'Body',7.7,10,col='#ffffff')
 def facts(self,x,t,w,stack=False):
  v=self.v
  if stack:
   end=self.text('<b>Retail setting</b><br/>'+e(v['type']),x,t,w,'Body',9,12)
   return self.text('<b>Rail access</b><br/>'+e(v['rail']),x,end+10,w,'Body',9,12)
  left=w*.59
  a=self.text('<b>Retail setting</b><br/>'+e(v['type']),x,t,left,'Body',9,12)
  b=self.text('<b>Rail access</b><br/>'+e(v['rail']),x+left+15,t,w-left-15,'Body',9,12)
  return max(a,b)
 def section(self,title,key,x,t,w):
  self.line(x,t,w,self.accent,.65)
  t=self.text(e(title),x,t+9,w,'BodyBold',11.5,14)+5
  return self.text(e(self.v[key]),x,t,w,'Body',11,14.6)+12
 def stack(self,items,x,t,w):
  for title,key in items:t=self.section(title,key,x,t,w)
  return t
 def footer(self,n,photos=None):
  # Quiet, necessary image attribution; venue research notes are kept off the page.
  if photos:
   credits=[]
   for i,p in enumerate(photos,1):
    credits.append(f'{i}. <link href="{e(p["url"])}">{e(p["author"])}</link> · <link href="{e(p["licenseUrl"])}">{e(p["license"])}</link>')
   txt='Photos: '+' &nbsp; / &nbsp; '.join(credits)+' · Wikimedia Commons · Cropped.'
   para=Paragraph(txt,ParagraphStyle('credit',fontName='Body',fontSize=7,leading=9,textColor=colour('#62665f')))
   _,hh=para.wrap(W-84,30);para.drawOn(self.c,42,H-777-hh)
  self.line(42,805,W-84,'#c6cbbb',.5)
  self.c.setFillColor(colour(self.ink));self.c.setFont('Body',8)
  self.c.drawString(42,H-821,'Brands Bangkok  /  Location collection')
  self.c.drawRightString(W-42,H-821,f'{n:02} / 07')
def photos_for(v,extra):
 original={'file':'assets/'+v['slug']+'.jpg','caption':'Exterior' if v['slug']!='central-embassy' else 'Around the address','author':v['photoAuthor'],'license':v['photoLicense'],'licenseUrl':v['licenseUrl'],'url':v['photoPage']}
 found=[p for p in extra if p['slug']==v['slug']]
 return found if v['slug'] in ['centralworld','siam-paragon'] else [original,found[0]]
A=('The retail character','character');B=('Around the address','neighbourhood');C=('Getting here','access');D=('A fashion business perspective','business');E=('Beyond fashion','beyond')
def centralworld(p,ph):
 p.brand();p.rect(0,77,8,687,p.accent)
 p.label(p.v['area']+' · Bangkok',42,88,450)
 p.title(e(p.v['name']),42,108,490,40)
 p.text(e(p.v['intro']),42,162,490,'Body',12,16)
 p.text(e(p.v['line']),42,207,490,'TitleItalic',14,17,col=p.accent)
 p.photo(ph[0],42,240,326,145);p.photo(ph[1],380,240,W-422,145)
 p.facts(42,402,W-84)
 p.stack([A,D],42,453,245);p.stack([B,C,E],309,453,W-351)
def siam_center(p,ph):
 p.brand();p.rect(28,81,270,259,p.pale);p.rect(28,81,6,259,p.accent)
 p.label('Siam · Bangkok',45,100,235);p.title('Siam<br/>Center',45,126,235,39)
 p.text(e(p.v['line']),45,223,230,'TitleItalic',14,18,col=p.accent)
 p.text(e(p.v['intro']),45,265,225,'Body',11.5,15)
 p.photo(ph[0],315,81,W-357,197);p.facts(315,295,W-357,True)
 p.photo(ph[1],42,361,256,150)
 p.stack([D,E],42,534,256)
 p.stack([A,B,C],323,420,W-365)
def terminal(p,ph):
 p.rect(0,0,22,H,p.ink);p.brand()
 p.label(p.v['area']+' · Bangkok',42,89,500)
 p.title(e(p.v['name']),42,111,510,35)
 p.text(e(p.v['line']),42,161,500,'TitleItalic',14,18,col=p.accent)
 p.photo(ph[0],42,197,178,220);p.photo(ph[1],236,197,W-278,131)
 p.text(e(p.v['intro']),236,348,W-278,'Body',12,16)
 p.rect(42,435,W-84,53,p.pale);p.facts(55,447,W-110)
 p.stack([A,D],42,509,245);p.stack([B,C,E],309,509,W-351)
def paragon(p,ph):
 p.rect(0,0,W,H,p.pale);p.brand()
 p.label('Siam · Bangkok',42,87,W-84)
 p.title(e(p.v['name']),42,110,W-84,37,1)
 p.text(e(p.v['line']),42,160,W-84,'TitleItalic',14,18,col=p.accent,align=1)
 p.text(e(p.v['intro']),66,194,W-132,'Body',12,16,align=1)
 p.line(42,239,W-84,p.accent,1)
 p.photo(ph[0],42,251,250,143);p.photo(ph[1],304,251,W-346,143)
 p.facts(42,414,W-84)
 p.stack([A,D],42,469,245);p.stack([B,C,E],309,469,W-351)
def embassy(p,ph):
 p.rect(0,0,W,H,p.pale);p.brand()
 p.label('Ploen Chit · Bangkok',42,95,247)
 p.title('Central<br/>Embassy',42,124,246,38)
 p.text(e(p.v['line']),42,221,245,'TitleItalic',14,19,col=p.accent)
 p.text(e(p.v['intro']),42,278,245,'Body',12,16)
 p.facts(42,352,245,True)
 p.photo(ph[1],316,94,W-358,270)
 p.photo(ph[0],316,378,W-358,100)
 p.stack([A,D],42,500,245);p.stack([B,C,E],309,500,W-351)
def cover(c,root,data):
 p=Page(c,root);p.brand();p.label('The location collection',42,89,W-84)
 p.title('Your brand.<br/>Bangkok’s next chapter.',42,111,W-84,33)
 p.text('Bring your business to Bangkok. Discover five shopping destinations for international fashion and retail brands.',42,198,W-84,'Body',12,16)
 p.text('Brands Bangkok brings the city closer to overseas fashion and retail businesses. Our guide introduces five centres, from local fashion and Thai design to international and luxury brands.',42,250,W-84,'Body',11,14.6)
 p.text('Rail access map · page 2',42,286,W-84,'BodyBold',9,12,col=p.accent)
 y=307
 for v in data['venues']:
  a,ink,pale=PALETTES[v['slug']]
  p.rect(42,y,4,39,a);p.rect(46,y,W-88,39,pale)
  p.text(e(v['name']),57,y+7,160,'BodyBold',11,14,col=ink)
  p.text(e(v['rail']),57,y+24,160,'Body',8,10,col=ink)
  p.text(e(v['type']),230,y+10,W-287,'Body',10,13,col=ink)
  y+=44
 p.label('Business services',42,550,W-84)
 left=572;right=572
 for i,(title,text) in enumerate(data['services']):
  x,t,w=(42,left,245) if i<3 else (309,right,W-351)
  t=p.text(e(title),x,t,w,'BodyBold',10.5,13)+4
  t=p.text(e(text),x,t,w,'Body',9.5,12.3)+12
  if i<3:left=t
  else:right=t
 p.text('Short-term rates are available in the separate <i>Retail spaces &amp; rates</i> booklet.',309,right+8,W-351,'Body',9,12)
 p.footer(1)

def access_page(c,root,data):
 import pymupdf
 from reportlab.platypus import Table,TableStyle
 access=data['accessGuide']
 p=Page(c,root);p.brand();p.label('Connected addresses',42,88,W-84)
 p.title(e(access['title']),42,109,W-84,30)
 p.text('Station links and short walks to five shopping destinations.',42,155,W-84,'Body',11,14)
 p.text(e(access['note']),42,177,W-84,'Body',9,12,col='#52615c')
 with pymupdf.open(root/'assets/bangkok-access-map.svg') as document:
  pix=document[0].get_pixmap(matrix=pymupdf.Matrix(1.8,1.8),alpha=False)
  c.drawImage(ImageReader(BytesIO(pix.tobytes('png'))),42,H-201-(W-84)*665/1200,width=W-84,height=(W-84)*665/1200)
 p.text('<b>BTS Skytrain:</b> '+e(access['bts']),42,494,W-84,'Body',10,13)
 p.text('<b>MRT:</b> '+e(access['mrt']),42,519,W-84,'Body',10,13)
 p.text('From the station exit',42,559,W-84,'BodyBold',12,16)
 normal=ParagraphStyle('walk',fontName='Body',fontSize=10.5,leading=13,textColor=colour(p.ink))
 bold=ParagraphStyle('walk-heading',parent=normal,fontName='BodyBold')
 rows=[['Location','Approximate walk from the station exit']]+[[v['name'],access['venues'][v['slug']]['mapWalk']]for v in data['venues']]
 cells=[[Paragraph(e(s),bold if i==0 else normal)for s in row]for i,row in enumerate(rows)]
 table=Table(cells,colWidths=[145,W-84-145],hAlign='LEFT')
 table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),colour('#edf1ea')),('LINEABOVE',(0,0),(-1,0),.8,colour(p.ink)),('LINEBELOW',(0,0),(-1,-1),.4,colour('#c6cbbb')),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
 _,height=table.wrap(W-84,H)
 if 584+height>785:raise ValueError('Access table overflows')
 table.drawOn(c,42,H-584-height)
 p.footer(2)

def build(Book,data,root):
 c=canvas.Canvas(str(root/'print/brands-bangkok-locations.pdf'),pagesize=A4,pageCompression=1,invariant=1)
 c.setTitle('Location guide | Brands Bangkok');c.setAuthor('Brands Bangkok')
 extra=json.loads((root/'print/additional-photos.json').read_text(encoding='utf-8'))
 cover(c,root,data);c.showPage()
 access_page(c,root,data);c.showPage()
 layouts={'centralworld':centralworld,'siam-center':siam_center,'terminal-21-asok':terminal,'siam-paragon':paragon,'central-embassy':embassy}
 for i,v in enumerate(data['venues'],3):
  p=Page(c,root,v);ph=photos_for(v,extra)
  layouts[v['slug']](p,ph);p.footer(i,ph);c.showPage()
 c.save()
