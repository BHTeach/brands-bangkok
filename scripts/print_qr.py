"""Static, locally generated QR code. No redirect or QR hosting service."""
from pathlib import Path
import qrcode
from reportlab.lib import colors
WEBSITE_URL='https://bhteach.github.io/brands-bangkok/'
qr=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,box_size=1,border=4)
qr.add_data(WEBSITE_URL)
qr.make(fit=True)
MATRIX=qr.get_matrix()
SIDE=70
TOP=12
RIGHT=42.5
def write_qr_asset(root):
 n=len(MATRIX)
 rects=''.join(f'<rect x="{x}" y="{y}" width="1" height="1"/>' for y,row in enumerate(MATRIX) for x,dark in enumerate(row) if dark)
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {n} {n}" role="img" aria-label="QR code for the Brands Bangkok website"><rect width="{n}" height="{n}" fill="white"/><g fill="black">{rects}</g></svg>'
 (Path(root)/'assets/website-qr.svg').write_text(svg,encoding='utf-8')
def draw_website_qr(c,width,height):
 x=width-RIGHT-SIDE;y=height-TOP-SIDE;step=SIDE/len(MATRIX)
 c.saveState()
 c.setFillColor(colors.white);c.rect(x,y,SIDE,SIDE,fill=1,stroke=0)
 c.setFillColor(colors.black)
 for row,modules in enumerate(MATRIX):
  for col,dark in enumerate(modules):
   if dark:c.rect(x+col*step,y+(len(MATRIX)-row-1)*step,step,step,fill=1,stroke=0)
 c.setFont('Body',7.5);c.drawCentredString(x+SIDE/2,y-11,'Website version')
 c.linkURL(WEBSITE_URL,(x,y-15,x+SIDE,y+SIDE),relative=0,thickness=0)
 c.restoreState()
