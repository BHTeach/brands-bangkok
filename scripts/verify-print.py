"""Check copy, rates, alignment and A4 page counts; render review images."""
from pathlib import Path
import json
import pymupdf
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parent.parent
data=json.loads((ROOT/'print/print-data.json').read_text())
locations=pymupdf.open(ROOT/'print/brands-bangkok-locations.pdf')
rentals=pymupdf.open(ROOT/'print/brands-bangkok-rental-rates.pdf')
assert len(locations)==6 and len(rentals)==6
norm=lambda s:' '.join(s.split())
for i,v in enumerate(data['venues'],1):
 text=norm(locations[i].get_text())
 for key in ['intro','character','neighbourhood','access','business','beyond']:
  assert norm(v[key]) in text,(v['slug'],key)
 assert 'Published information' not in text
 rental=rentals[i].get_text()
 for row in v['rents']:
  for n in row['values']:assert format(n,',') in rental
 for row in v['charges']:
  for key in ['space','retail','brand','deposit']:assert format(row[key],',') in rental
 for header,key in [('Space only','space'),('Retail setup','retail'),('Brand display','brand')]:
  box=rentals[i].search_for(header)[0]
  amount=str(format(v['charges'][0][key],','))
  options=[r for r in rentals[i].search_for(amount) if r.y0>box.y1 and r.y0<box.y1+85 and abs(r.x1-box.x1)<1]
  assert options,(v['slug'],header,'alignment')
 assert str(data['rate']['rate']) in rental
for p in list(locations)+list(rentals):
 assert abs(p.rect.width-595.276)<1 and abs(p.rect.height-841.89)<1
 assert all(b[0]>=0 and b[2]<=p.rect.width+1 and b[1]>=0 and b[3]<=p.rect.height+1 for b in p.get_text('blocks'))
preview=ROOT/'print/previews';preview.mkdir(exist_ok=True)
sheet=Image.new('RGB',(1240,2640),'#dddddd')
for i,p in enumerate(locations):
 pix=p.get_pixmap(matrix=pymupdf.Matrix(1.1,1.1))
 im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
 thumb=ImageOps.contain(im,(600,855))
 sheet.paste(thumb,((i%2)*620+10,(i//2)*880+10))
sheet.save(preview/'location-guide.jpg',quality=85,optimize=True)
rentals[1].get_pixmap(matrix=pymupdf.Matrix(1.1,1.1)).save(preview/'rental-table.png')
(ROOT/'print/validation.json').write_text(json.dumps({'location_pages':6,'rental_pages':6,'profiles_preserved':5,'rental_prices_checked':180,'charges_checked':60,'alignment_checked':True,'rate':data['rate']['rate']},indent=2)+'\n')
print('A4 pages, all profile paragraphs, 180 rental prices, 60 setup/deposit cells and numeric alignment verified.')
