"""Download the credited brochure photographs and portable print fonts."""
from pathlib import Path
from urllib.request import urlopen,Request
from urllib.parse import urlencode
import json,time,shutil,io
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
ROOT=Path(__file__).resolve().parent.parent
def get(url):
 for attempt in range(3):
  try:
   with urlopen(Request(url,headers={'User-Agent':'BrandsBangkokPrint/1.0 (British Hills course materials)'}),timeout=90) as response:return response.read()
  except Exception:
   if attempt==2:raise
   time.sleep(5*(attempt+1))
for photo in json.loads((ROOT/'print/additional-photos.json').read_text()):
 dest=ROOT/photo['file']
 if dest.exists():continue
 query=urlencode({'action':'query','format':'json','prop':'imageinfo','iiprop':'url','iiurlwidth':1280,'titles':photo['title']})
 info=next(iter(json.loads(get('https://commons.wikimedia.org/w/api.php?'+query))['query']['pages'].values()))['imageinfo'][0]
 dest.write_bytes(get(info.get('thumburl') or info['url']))
 print('Downloaded',dest.name,flush=True)
font_dir=ROOT/'.print-fonts';font_dir.mkdir(exist_ok=True)
for source,target in [('LiberationSans-Regular.ttf','arial.ttf'),('LiberationSans-Bold.ttf','arialbd.ttf'),('LiberationSans-Italic.ttf','ariali.ttf')]:
 candidates=list(Path('/usr/share/fonts/truetype').rglob(source))
 if not candidates:raise RuntimeError('Install fonts-liberation')
 shutil.copyfile(candidates[0],font_dir/target)
for remote,target in [('Gelasio%5Bwght%5D.ttf','georgia.ttf'),('Gelasio-Italic%5Bwght%5D.ttf','georgiai.ttf')]:
 font=TTFont(io.BytesIO(get('https://raw.githubusercontent.com/google/fonts/main/ofl/gelasio/'+remote)))
 font=instantiateVariableFont(font,{'wght':400},inplace=True)
 font.save(font_dir/target)
print('Portable fonts ready.',flush=True)
