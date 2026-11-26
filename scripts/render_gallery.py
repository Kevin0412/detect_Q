import sys,csv
from pathlib import Path
sys.path.insert(0,str(Path("src").resolve()))
import cv2
from detect import detect_q
from PIL import Image,ImageDraw
out=Path("render-output");out.mkdir(exist_ok=True)
preview=Path("docs/generated");preview.mkdir(parents=True,exist_ok=True)
rows=[]
for label in ("0","1"):
    for p in sorted(Path("data",label).rglob("*.png")):
        im=cv2.imread(str(p))
        if im is not None:rows.append((label,p,float(detect_q(im)),im))
assert rows
with (out/"scores.csv").open("w") as f:
    w=csv.writer(f);w.writerow(["label","path","score"]);w.writerows((a,str(b),c) for a,b,c,d in rows)
gallery=Image.new("RGB",(800,400),"#161b22");d=ImageDraw.Draw(gallery)
for j,label in enumerate(("0","1")):
    examples=[r for r in rows if r[0]==label][:5]
    for i,(_,p,s,im) in enumerate(examples):
        tile=Image.fromarray(cv2.cvtColor(im,cv2.COLOR_BGR2RGB)).resize((140,140))
        x=i*160+10;y=j*200+10;gallery.paste(tile,(x,y));d.text((x,y+145),f"label {label} / {s:.3f}",fill="white")
gallery.save(out/"gallery.png");gallery.save(preview/"preview.webp",quality=90)
