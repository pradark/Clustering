"""
Customer Segmentation PDF — original purple gradient style + radar/spider charts on segment slides.
"""
import os, math
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, PageBreak, HRFlowable)
from reportlab.platypus.flowables import Flowable
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon, Circle
from reportlab.graphics.charts.piecharts import Pie

# ── Fonts ──────────────────────────────────────────────────────────────────────
FD = '/tmp/Inter/extras/ttf/'
for nm, fn in [('Inter','Inter-Regular.ttf'),('Inter-Bold','Inter-Bold.ttf'),
               ('Inter-SemiBold','Inter-SemiBold.ttf')]:
    try: pdfmetrics.registerFont(TTFont(nm, FD+fn))
    except: pass

# ── Colours ────────────────────────────────────────────────────────────────────
PURPLE    = colors.HexColor('#667eea')
DARK_PUR  = colors.HexColor('#764ba2')
LIGHT_BG  = colors.HexColor('#f0f4ff')
YELLOW    = colors.HexColor('#ffc107')
RED       = colors.HexColor('#d32f2f')
GREEN     = colors.HexColor('#2ecc71')
ORANGE    = colors.HexColor('#ff9800')
BLUE      = colors.HexColor('#2196f3')
PINK      = colors.HexColor('#9c27b0')
WHITE     = colors.white
DARK      = colors.HexColor('#333333')
GREY      = colors.HexColor('#666666')
LG        = colors.HexColor('#dddddd')

# ── Page geometry ──────────────────────────────────────────────────────────────
PAGE_W, PAGE_H = landscape(A4)
LEFT = RIGHT = 0.5*inch
TOP  = 0.35*inch
BOT  = 0.35*inch
CW   = PAGE_W - LEFT - RIGHT

# ── Styles ─────────────────────────────────────────────────────────────────────
def PS(name, font='Helvetica', size=9, color=DARK, leading=13, **kw):
    return ParagraphStyle(name, fontName=font, fontSize=size,
                          textColor=color, leading=leading, **kw)

sH2   = PS('sH2',  'Helvetica-Bold', 12, DARK_PUR, 15, spaceBefore=2, spaceAfter=2)
sBody = PS('sBody','Helvetica',       9,  DARK,     13, spaceAfter=2)
sSmall= PS('sSm',  'Helvetica',       8,  GREY,     11)
sCB   = PS('sCB',  'Helvetica-Bold',  9,  DARK,     13, alignment=TA_CENTER)
sNote = PS('sN',   'Helvetica',       8,  WHITE,    12)

def TS():
    return TableStyle([
        ('BACKGROUND',(0,0),(-1,0),PURPLE),('TEXTCOLOR',(0,0),(-1,0),WHITE),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
        ('FONTSIZE',(0,0),(-1,-1),8),('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[WHITE,LIGHT_BG]),
        ('GRID',(0,0),(-1,-1),0.4,LG),
        ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
        ('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),
    ])

# ── Custom Flowables ───────────────────────────────────────────────────────────
class Hdr(Flowable):
    def __init__(self, title, sub='', num=''):
        super().__init__()
        self.title=title; self.sub=sub; self.num=num
        self.height=0.82*inch
    def wrap(self, availW, availH):
        self.width=availW; return (availW, self.height)
    def draw(self):
        c=self.canv; W=self.width
        c.setFillColor(PURPLE);  c.rect(0,0,W,self.height,fill=1,stroke=0)
        c.setFillColor(DARK_PUR);c.rect(W*0.68,0,W*0.32,self.height,fill=1,stroke=0)
        c.setFillColor(WHITE); c.setFont('Helvetica-Bold',16)
        c.drawString(0.22*inch,0.47*inch,self.title)
        if self.sub:
            c.setFont('Helvetica',8.5); c.drawString(0.22*inch,0.23*inch,self.sub)
        if self.num:
            c.setFont('Helvetica-Bold',8)
            c.drawRightString(W-6,0.37*inch,self.num)

class Pill(Flowable):
    def __init__(self,lbl,val,col=PURPLE,w=1.33*inch,h=0.65*inch):
        super().__init__(); self.lbl=lbl;self.val=val;self.col=col;self.width=w;self.height=h
    def draw(self):
        c=self.canv
        c.setFillColor(self.col)
        c.roundRect(0,0,self.width,self.height,5,fill=1,stroke=0)
        c.setFillColor(WHITE); c.setFont('Helvetica-Bold',13)
        c.drawCentredString(self.width/2,self.height*0.42,self.val)
        c.setFont('Helvetica',6.5)
        c.drawCentredString(self.width/2,self.height*0.14,self.lbl)

class Cover(Flowable):
    def __init__(self):
        super().__init__()
    def wrap(self, availW, availH):
        self.width=availW; self.height=availH; return (availW, availH)
    def draw(self):
        c=self.canv; W=self.width; H=self.height
        c.setFillColor(PURPLE); c.rect(0,0,W,H,fill=1,stroke=0)
        c.setFillColor(DARK_PUR); c.rect(0,0,W,H*0.33,fill=1,stroke=0)
        c.setFillColor(WHITE); c.setFont('Helvetica-Bold',32)
        c.drawString(0.25*inch,H*0.56,'Customer Segmentation Analysis')
        c.setFont('Helvetica',13); c.setFillColor(colors.HexColor('#ddddff'))
        c.drawString(0.25*inch,H*0.47,
                     'Data-Driven Portfolio Strategy  |  5 Customer Segments  |  Confidential')
        # Stat box accent colours — dark enough to contrast with white text
        box_cols = [colors.HexColor('#1e0a45'),   # Customers  — deep indigo
                    colors.HexColor('#0d2e52'),   # Features   — dark navy
                    colors.HexColor('#0a3a2e'),   # k=5        — dark teal (highlight)
                    colors.HexColor('#3a0e38')]   # ROI        — deep plum
        stats=[('9,417','Customers'),('18','Raw Features'),
               ('k = 5','Optimal Clusters'),('2.5-3.5x','Expected ROI')]
        for i,(val,lbl) in enumerate(stats):
            x=0.3*inch+i*1.8*inch
            c.setFillColor(box_cols[i])
            c.roundRect(x,0.17*inch,1.65*inch,0.66*inch,6,fill=1,stroke=0)
            # subtle bright border
            c.setStrokeColor(colors.HexColor('#8888cc'))
            c.setLineWidth(0.6)
            c.roundRect(x,0.17*inch,1.65*inch,0.66*inch,6,fill=0,stroke=1)
            c.setFillColor(WHITE); c.setFont('Helvetica-Bold',17)
            c.drawCentredString(x+0.82*inch,0.51*inch,val)
            c.setFont('Helvetica',7.5); c.setFillColor(colors.HexColor('#ccddff'))
            c.drawCentredString(x+0.82*inch,0.28*inch,lbl)
        c.setFont('Helvetica',7.5); c.setFillColor(colors.HexColor('#aaaacc'))
        c.drawRightString(W-0.1*inch,0.09*inch,
                          'ABC Debt Relief  |  Prepared June 2026')

# ── Chart helpers ──────────────────────────────────────────────────────────────
def radar_chart(metrics, values, col, w=2.65*inch, h=2.45*inch, max_val=100):
    """Spider / radar chart for segment profile (4 axes)."""
    d = Drawing(w, h)
    cx = w/2; cy = h/2 - 4
    r  = min(w, h) * 0.30          # radius leaving room for labels

    n    = len(metrics)
    angs = [math.pi/2 - 2*math.pi*i/n for i in range(n)]

    # ── concentric background rings ──
    ring_bg = [colors.HexColor('#f0f4ff'),
               colors.HexColor('#dde5fa'),
               colors.HexColor('#ccd5f5')]
    for level, bg in zip([1.0, 0.66, 0.33], ring_bg):
        pts = []
        for a in angs:
            pts += [cx + r*level*math.cos(a), cy + r*level*math.sin(a)]
        d.add(Polygon(pts, fillColor=bg, strokeColor=LG, strokeWidth=0.6))

    # ── axis lines ──
    for a in angs:
        d.add(Line(cx, cy, cx+r*math.cos(a), cy+r*math.sin(a),
                   strokeColor=LG, strokeWidth=0.8))

    # ── ring level labels (on top axis) ──
    ta = angs[0]
    for level, txt in [(0.33,'33%'),(0.66,'66%'),(1.0,'100%')]:
        lx = cx + r*level*math.cos(ta)
        ly = cy + r*level*math.sin(ta)
        d.add(String(lx+2, ly+1, txt, fontSize=5.5,
                     fillColor=GREY, fontName='Helvetica'))

    # ── data polygon ──
    data_pts = []
    for v, a in zip(values, angs):
        frac = min(v/max_val, 1.0)
        data_pts += [cx + r*frac*math.cos(a), cy + r*frac*math.sin(a)]

    fill = colors.Color(col.red, col.green, col.blue, 0.25)
    d.add(Polygon(data_pts, fillColor=fill, strokeColor=col, strokeWidth=2.0))

    # ── dots at vertices ──
    for v, a in zip(values, angs):
        frac = min(v/max_val, 1.0)
        px = cx + r*frac*math.cos(a)
        py = cy + r*frac*math.sin(a)
        d.add(Circle(px, py, 3.8, fillColor=col, strokeColor=WHITE, strokeWidth=1.2))

    # ── axis labels (name + value) ──
    short = {
        'Utilization Rate': 'Utilization',
        'Payment Quality':  'Pmt Quality',
        'Engagement':       'Engagement',
        'Financial Health': 'Fin. Health',
    }
    lbl_r = r + 16
    for m, v, a in zip(metrics, values, angs):
        lx = cx + lbl_r*math.cos(a)
        ly = cy + lbl_r*math.sin(a)
        ca, sa = math.cos(a), math.sin(a)
        lbl = short.get(m, m[:12])

        if sa > 0.4:           # top
            tx, ty = lx - 18, ly + 5
        elif sa < -0.4:        # bottom
            tx, ty = lx - 18, ly - 16
        elif ca > 0.4:         # right
            tx, ty = lx + 3,  ly - 4
        else:                  # left
            tx, ty = lx - 50, ly - 4

        d.add(String(tx, ty + 7, lbl, fontSize=6.5,
                     fillColor=GREY, fontName='Helvetica'))
        d.add(String(tx, ty - 2, f'{v}%', fontSize=7,
                     fillColor=col, fontName='Helvetica-Bold'))
    return d

def hbars(metrics, vals, col):
    rows=[]
    for m,v in zip(metrics,vals):
        d=Drawing(2.4*inch,12)
        d.add(Rect(0,1,2.35*inch,9,fillColor=LIGHT_BG,strokeColor=None))
        d.add(Rect(0,1,max(v/100,0.01)*2.35*inch,9,fillColor=col,strokeColor=None))
        rows.append([Paragraph(m,sSmall),d,Paragraph(f'<b>{v}%</b>',sCB)])
    t=Table(rows,colWidths=[1.35*inch,2.5*inch,0.55*inch])
    t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                            ('TOPPADDING',(0,0),(-1,-1),1),
                            ('BOTTOMPADDING',(0,0),(-1,-1),1)]))
    return t

def elbow():
    d=Drawing(3.0*inch,1.85*inch)
    ks=[2,3,4,5,6,7,8]; iv=[49005,41942,35645,30127,24443,21439,18497]
    xs=[0.27+i*0.38 for i in range(7)]; hi,lo=49005,18497
    fy=lambda v:0.13+(hi-v)/(hi-lo)*1.55
    pts=[]
    for x,v in zip(xs,iv): pts+=[x*inch,fy(v)*inch]
    pts+=[xs[-1]*inch,0.13*inch,xs[0]*inch,0.13*inch]
    d.add(Polygon(pts,fillColor=colors.HexColor('#ffdddd'),strokeColor=None))
    for i in range(6):
        d.add(Line(xs[i]*inch,fy(iv[i])*inch,xs[i+1]*inch,fy(iv[i+1])*inch,
                   strokeColor=RED,strokeWidth=1.8))
    for i,(x,v) in enumerate(zip(xs,iv)):
        d.add(Circle(x*inch,fy(v)*inch,4,fillColor=YELLOW if ks[i]==5 else RED,
                     strokeColor=WHITE,strokeWidth=0.5))
        d.add(String(x*inch-6,0.02*inch,f'k={ks[i]}',fontSize=5.5,fillColor=GREY))
    d.add(String(0.7*inch,1.75*inch,'Elbow Method — Inertia Curve',
                 fontSize=6.5,fillColor=DARK,fontName='Helvetica-Bold'))
    d.add(String(xs[3]*inch-12,fy(iv[3])*inch+6,'< ELBOW',
                 fontSize=6,fillColor=YELLOW,fontName='Helvetica-Bold'))
    d.add(Line(0.2*inch,0.11*inch,0.2*inch,1.8*inch,strokeColor=LG,strokeWidth=0.5))
    d.add(Line(0.2*inch,0.11*inch,2.9*inch,0.11*inch,strokeColor=LG,strokeWidth=0.5))
    return d

def silh():
    d=Drawing(3.0*inch,1.85*inch)
    ks=[2,3,4,5,6,7,8]; sv=[0.283,0.297,0.331,0.353,0.358,0.363,0.364]
    xs=[0.27+i*0.38 for i in range(7)]; mn,mx=0.27,0.37
    fy=lambda v:0.13+(v-mn)/(mx-mn)*1.55
    pts=[]
    for x,v in zip(xs,sv): pts+=[x*inch,fy(v)*inch]
    pts+=[xs[-1]*inch,0.13*inch,xs[0]*inch,0.13*inch]
    d.add(Polygon(pts,fillColor=colors.HexColor('#ccffcc'),strokeColor=None))
    for i in range(6):
        d.add(Line(xs[i]*inch,fy(sv[i])*inch,xs[i+1]*inch,fy(sv[i+1])*inch,
                   strokeColor=GREEN,strokeWidth=1.8))
    for i,(x,v) in enumerate(zip(xs,sv)):
        d.add(Circle(x*inch,fy(v)*inch,4,fillColor=YELLOW if ks[i]==5 else GREEN,
                     strokeColor=WHITE,strokeWidth=0.5))
        d.add(String(x*inch-6,0.02*inch,f'k={ks[i]}',fontSize=5.5,fillColor=GREY))
    d.add(String(0.7*inch,1.75*inch,'Silhouette Score by k',
                 fontSize=6.5,fillColor=DARK,fontName='Helvetica-Bold'))
    d.add(Line(0.2*inch,0.11*inch,0.2*inch,1.8*inch,strokeColor=LG,strokeWidth=0.5))
    d.add(Line(0.2*inch,0.11*inch,2.9*inch,0.11*inch,strokeColor=LG,strokeWidth=0.5))
    return d

def pie_chart():
    d=Drawing(2.75*inch,2.0*inch)
    p=Pie(); p.x=0.55*inch; p.y=0.1*inch; p.width=1.45*inch; p.height=1.45*inch
    p.data=[27.5,14.2,14.7,35.9,7.8]; p.labels=['']*5
    for i,c in enumerate([RED,GREEN,ORANGE,BLUE,PINK]): p.slices[i].fillColor=c
    d.add(p)
    for i,(lbl,col) in enumerate([('Distressed 27.5%',RED),('Prime 14.2%',GREEN),
                                    ('Engaged 14.7%',ORANGE),('Low Cap 35.9%',BLUE),
                                    ('High Risk 7.8%',PINK)]):
        y=(1.83-i*0.34)*inch
        d.add(Rect(0.03*inch,y,8,8,fillColor=col,strokeColor=None))
        d.add(String(0.18*inch,y,lbl,fontSize=6.5,fillColor=DARK))
    return d

def roi_chart():
    d=Drawing(5.4*inch,1.8*inch)
    segs=['Distressed','Prime','Engaged','Low Cap','High Risk']
    inv=[330,405,295,155,295]; ben=[1500,800,500,700,4000]
    bw=0.3*inch; gap=0.78*inch; mx=4000
    bh=lambda v: max(v/mx*1.52*inch,0.02*inch)
    d.add(Line(0.38*inch,0.2*inch,5.2*inch,0.2*inch,strokeColor=GREY,strokeWidth=0.5))
    for i,(s,iv,bv) in enumerate(zip(segs,inv,ben)):
        x=0.52*inch+i*gap
        d.add(Rect(x,      0.2*inch,bw,bh(iv),fillColor=PURPLE,strokeColor=None))
        d.add(Rect(x+bw+2, 0.2*inch,bw,bh(bv),fillColor=GREEN, strokeColor=None))
        d.add(String(x+bw-2,0.05*inch,s,fontSize=5.8,fillColor=GREY))
    d.add(Rect(0.5*inch,1.68*inch,8,8,fillColor=PURPLE,strokeColor=None))
    d.add(String(0.65*inch,1.68*inch,'Investment ($K)',fontSize=7,fillColor=DARK))
    d.add(Rect(1.72*inch,1.68*inch,8,8,fillColor=GREEN,strokeColor=None))
    d.add(String(1.87*inch,1.68*inch,'Expected Benefit ($K)',fontSize=7,fillColor=DARK))
    d.add(String(1.5*inch,1.8*inch,'Investment vs. Expected Benefit',
                 fontSize=7,fillColor=DARK,fontName='Helvetica-Bold'))
    return d

def HL(text):
    t=Table([[Paragraph(text,sBody)]],colWidths=[CW],
            style=TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#fff9e6')),
                               ('BOX',(0,0),(-1,-1),1,YELLOW),
                               ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
                               ('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10)]))
    return t

# ── Story helpers ──────────────────────────────────────────────────────────────
story = []
def H(title,sub='',num=''): story.append(Hdr(title,sub,num)); story.append(Spacer(1,0.13*inch))
def D(): story.append(HRFlowable(width='100%',thickness=0.5,color=LG,spaceBefore=5,spaceAfter=4))
def two_col(lc,rc,lw=3.1*inch,rw=4.6*inch):
    t=Table([[lc,rc]],colWidths=[lw,rw])
    t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),
                            ('RIGHTPADDING',(0,0),(0,0),8),
                            ('LEFTPADDING',(1,0),(1,0),0)]))
    story.append(t)

# ══════════════════════════════════════════════════════════════════════════════
# COVER
# ══════════════════════════════════════════════════════════════════════════════
story.append(Cover())
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 2 — EXECUTIVE SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
H('Executive Summary','5 Customer Segments  |  Portfolio Risk & Revenue Overview','Slide 2')
two_col(
    [Paragraph('Portfolio Distribution',sH2), pie_chart(),
     Spacer(1,4),
     Paragraph('<b>63.4%</b> of portfolio in at-risk segments (Distressed + Low Cap)',
               PS('note','Helvetica',8,GREY,11))],
    [Paragraph('Segment Financial Impact',sH2),
     Table([['Segment','Size','Avg Bal','Risk','Rev/Cust'],
            ['Distressed','2,458 (27.5%)','$2,725','HIGH','-$75-$125'],
            ['Prime','1,269 (14.2%)','$178','LOW','+$400-$500'],
            ['Engaged','1,312 (14.7%)','$3,117','MOD','+$250-$350'],
            ['Low Cap','3,210 (35.9%)','$698','LOW','$20-$50'],
            ['High Risk','701 (7.8%)','$1,068','MED-HI','$75-$125']],
           colWidths=[1.05*inch,1.12*inch,0.72*inch,0.65*inch,0.85*inch],style=TS()),
     Spacer(1,7),
     Paragraph('Strategic Priorities',sH2),
     Table([['Priority','Initiative','Investment','ROI'],
            ['1 URGENT','Distressed Intervention','$305-355K','3-5x'],
            ['2 URGENT','High Risk Prevention','$295K','3-5x'],
            ['3 HIGH',  'Prime Growth','$405K','2.4x'],
            ['4 HIGH',  'Engaged Optimization','$295K','2.5x'],
            ['5 EFF',   'Low Cap Activation','$155K','4.7x']],
           colWidths=[0.88*inch,1.5*inch,0.88*inch,0.55*inch],style=TS())])
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 3 — DATA OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
H('Data Overview','9,417 Customers  |  18 Raw Features  |  Snapshot Data','Slide 3')
pt=Table([[Pill('Total Customers','9,417',PURPLE),
           Pill('Features','18',DARK_PUR),
           Pill('After Cleaning','8,950',GREEN),
           Pill('Outliers Removed','467 (4.9%)',RED),
           Pill('Missing Imputed','313',ORANGE),
           Pill('Data Quality','99.8%',GREEN)]],
         colWidths=[1.37*inch]*6)
pt.setStyle(TableStyle([('LEFTPADDING',(0,0),(-1,-1),3),('RIGHTPADDING',(0,0),(-1,-1),3)]))
story.append(pt); story.append(Spacer(1,8)); D()
story.append(Paragraph('Feature Breakdown',sH2))
story.append(Table([
    ['Category','Features','Count','Business Relevance'],
    ['Balance & Capacity','BALANCE, CREDIT_LIMIT, BALANCE_FREQUENCY','3','Credit usage & capacity headroom'],
    ['Purchase Behavior','PURCHASES, ONEOFF_PURCHASES, INSTALLMENTS, PURCH_FREQ, PURCH_TRX','5','Spending activity & patterns'],
    ['Cash Advance','CASH_ADVANCE, CASH_ADV_FREQUENCY, CASH_ADV_TRX','3','Emergency borrowing signal'],
    ['Payment Behavior','PAYMENTS, MINIMUM_PAYMENTS, PRC_FULL_PAYMENT','3','Creditworthiness indicator'],
    ['Misc / Tenure','ONEOFF_FREQ, INSTALL_FREQ, TENURE','3','Behaviour & relationship age'],
],colWidths=[1.45*inch,2.9*inch,0.55*inch,2.5*inch],style=TS()))
story.append(Spacer(1,6))
story.append(Paragraph('<b>Key Stats:</b>  Avg Credit Limit $4,571  |  Avg Balance $1,564  '
    '|  Median Balance $627  |  Avg Tenure 12 months  |  Full-Payment Rate 23%  '
    '|  No date columns - snapshot / cross-sectional data',sBody))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 4 — DATA QUALITY
# ══════════════════════════════════════════════════════════════════════════════
H('Data Quality & Preparation','Cleaning  |  Imputation  |  Feature Engineering','Slide 4')
story.append(Table([
    ['Step','Action','Before','After','Quality Impact'],
    ['1  Outliers','Isolation Forest (contamination=0.05)','9,417 customers','8,950 customers','467 anomalies removed (4.9%)'],
    ['2  Missing','Mean imputation (MINIMUM_PAYMENTS)','314 missing (3.3%)','0 missing','Full dataset coverage'],
    ['3  Scaling','StandardScaler z-score normalisation','Raw $ amounts','Standardized features','Equal feature weighting'],
    ['4  Engineering','7 derived business metrics','18 raw features','7 engineered metrics','Business-aligned clustering'],
],colWidths=[0.85*inch,1.8*inch,1.42*inch,1.45*inch,1.9*inch],style=TS()))
story.append(Spacer(1,9))
story.append(Paragraph('7 Engineered Business Metrics',sH2))
story.append(Table([
    ['Metric','Formula','High = ...','Low = ...'],
    ['Utilization Rate','Balance / Credit Limit','Financial stress (>70%)','Healthy capacity (<20%)'],
    ['Payment Quality','% Full Payments','Creditworthy borrower','Default risk signal'],
    ['Engagement Score','Avg(Purchase Freq, Cash Adv Freq)','Active, loyal user','Churn risk'],
    ['Payment Consistency','Actual Payments / Minimum','Aggressive paydown','Min-only payer'],
    ['Debt-to-Limit','Balance / Credit Limit','>70% stress signal','<20% healthy'],
    ['Tenure Score','Months / 12','Long-term relationship','New account'],
    ['Transaction Volume','Purchase TRX + Cash Adv TRX','High activity','Inactive account'],
],colWidths=[1.45*inch,1.9*inch,1.9*inch,2.15*inch],style=TS()))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 5 — METHODOLOGY
# ══════════════════════════════════════════════════════════════════════════════
H('Methodology','K-Means  |  Elbow Method + Silhouette Score  =>  Optimal k = 5','Slide 5')
two_col(
    [Paragraph('Elbow Method (Inertia)',sH2), elbow(), Spacer(1,5),
     Table([['k','Inertia','% Impr',''],
            ['2','49,005','-',''],['3','41,942','14.4%',''],
            ['4','35,645','15.0%',''],['5','30,127','15.5%','< ELBOW'],
            ['6','24,443','18.9%','Post-elbow'],['7','21,439','12.3%','Diminishing']],
           colWidths=[0.35*inch,0.82*inch,0.6*inch,0.98*inch],style=TS())],
    [Paragraph('Silhouette Score',sH2), silh(), Spacer(1,5),
     Table([['k','Score','Quality'],
            ['2','0.283','Poor'],['3','0.297','Poor'],['4','0.331','Fair'],
            ['5','0.353','Good (Chosen)'],['6','0.358','Good'],['8','0.364','Peak +3%']],
           colWidths=[0.38*inch,0.65*inch,1.22*inch],style=TS()),
     Spacer(1,5),
     Table([[Paragraph('k=8 peaks at 0.364 - only +3% better than k=5 '
                        'but requires 3 extra management strategies',
                        PS('mn','Helvetica',8,GREY,11))]],
           colWidths=[2.3*inch],
           style=TableStyle([('BACKGROUND',(0,0),(-1,-1),LIGHT_BG),
                              ('TOPPADDING',(0,0),(-1,-1),5),
                              ('BOTTOMPADDING',(0,0),(-1,-1),5),
                              ('LEFTPADDING',(0,0),(-1,-1),6)]))])
story.append(Spacer(1,5))
story.append(HL('<b>Consensus: k=5 is Optimal.</b>  Elbow Method shows clear inflection at k=5 '
    '(15.5% improvement => 12.3% drop-off at k=7).  Silhouette k=5 = 0.353 vs k=8 = 0.364 - '
    'marginal +3% does not justify 60% added operational complexity.'))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# SEGMENT SLIDE FACTORY  (slides 6–10)
# Layout:  LEFT col = radar chart + KPI snapshot
#          RIGHT col = key metrics table
#          Below = strategy phases + ROI footer
# ══════════════════════════════════════════════════════════════════════════════
def seg(num, title, sub, col,
        pm, pv,           # profile metric names + values (4 items) for radar
        kpis,             # [(label, value), ...] for KPI snapshot table
        tdata, tcols,     # full metrics table data + column widths
        strat,            # [(phase, text), ...] strategy rows
        inv, ben, roi_):
    H(title, sub, f'Slide {num}')

    # KPI snapshot table
    kr = [[Paragraph(k, sSmall), Paragraph(f'<b>{v}</b>', sBody)] for k,v in kpis]
    kt = Table(kr, colWidths=[1.25*inch, 1.60*inch])
    kt.setStyle(TableStyle([
        ('ROWBACKGROUNDS',(0,0),(-1,-1),[WHITE,LIGHT_BG]),
        ('FONTSIZE',(0,0),(-1,-1),8),
        ('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),
        ('LEFTPADDING',(0,0),(-1,-1),5),
        ('GRID',(0,0),(-1,-1),0.3,LG),
    ]))

    two_col(
        # LEFT: spider chart + KPI table
        [Paragraph('Segment Profile', sH2),
         radar_chart(pm, pv, col, w=2.55*inch, h=1.62*inch),
         Spacer(1, 5),
         Paragraph('KPI Snapshot', sH2),
         kt],
        # RIGHT: detailed metrics table
        [Paragraph('Key Metrics', sH2),
         Table(tdata, colWidths=tcols, style=TS())],
        lw=3.1*inch, rw=4.6*inch
    )

    D()
    story.append(Paragraph('Business Strategy', sH2))
    sr = [[Paragraph(f'<b>{ph}</b>', sBody), Paragraph(txt, sBody)]
          for ph, txt in strat]
    st = Table(sr, colWidths=[1.22*inch, 6.48*inch])
    st.setStyle(TableStyle([
        ('ROWBACKGROUNDS',(0,0),(-1,-1),[WHITE,LIGHT_BG]),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('FONTSIZE',(0,0),(-1,-1),8),
        ('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),
        ('LEFTPADDING',(0,0),(-1,-1),6),
        ('BOX',(0,0),(-1,-1),0.5,LG),
    ]))
    story.append(st); story.append(Spacer(1,5))

    ft = Table([[Paragraph(f'Investment: <b>{inv}</b>',    sNote),
                 Paragraph(f'Expected Benefit: <b>{ben}</b>', sNote),
                 Paragraph(f'ROI: <b>{roi_}</b>',          sNote)]],
               colWidths=[2.5*inch,3.1*inch,2.1*inch])
    ft.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),col),
        ('TEXTCOLOR',(0,0),(-1,-1),WHITE),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
    ]))
    story.append(ft)
    story.append(PageBreak())

# ── Slide 6: Distressed Revolvers ─────────────────────────────────────────────
seg(6,'Distressed Revolvers',
    '2,458 Customers (27.5%)  |  Avg Balance $2,725  |  Risk: HIGH  |  Action: Intervene',RED,
    ['Utilization Rate','Payment Quality','Engagement','Financial Health'],[83,1,23,17],
    [('Avg Balance','$2,725'),('Utilization','83%'),('Full Pmt Rate','0.9%'),
     ('Engagement','0.23'),('Default Risk','15-20%'),('Portfolio Exposure','$6.7M')],
    [['Metric','Value','Business Implication'],
     ['Utilization Rate','83%','Near credit limit — severe financial stress'],
     ['Full Payment Rate','0.9%','Minimum-only payments — default accumulation risk'],
     ['Engagement Score','0.23','Avoidance behaviour, not disinterest'],
     ['Aggregate Balance','$6.7M','Critical single-segment portfolio exposure'],
     ['Est. Default Rate','15-20%','70-90% above portfolio baseline'],
     ['Pmt Consistency','1.57x min','Barely above minimum threshold']],
    [1.58*inch,1.02*inch,3.05*inch],
    [('Phase 1 (Wk 1-2)','Risk triage: Recoverable (40%), Declining (40%), Terminal (20%). '
      'Build automated scoring dashboard. Do not treat the segment as homogeneous.'),
     ('Phase 2 (Wk 3-8)','Hardship programmes, balance transfers at lower rates, credit counselling, income verification.'),
     ('Phase 3 (Wk 9+)','Freeze limit increases; auto-payment enrolment; SMS/email alerts at 3 and 7 days pre-due.')],
    '$305-355K/yr','$1-2M loss prevention','3-5x')

# ── Slide 7: Prime Customers ──────────────────────────────────────────────────
seg(7,'Prime Customers',
    '1,269 Customers (14.2%)  |  Avg Balance $178  |  Risk: LOW  |  Action: Grow & Retain',GREEN,
    ['Utilization Rate','Payment Quality','Engagement','Financial Health'],[4,78,41,95],
    [('Avg Balance','$178 (4.4%)'),('Full Pmt Rate','77.6%'),('Engagement','0.41'),
     ('Pmt Consistency','16.4x min'),('Annual Revenue','$400-500'),('Lifetime Value','$3,000-5,000')],
    [['Metric','Value','Opportunity'],
     ['Utilization','4.4%','Massive headroom for earned access expansion'],
     ['Full Payment','77.6%','Highest creditworthiness signal in portfolio'],
     ['Monthly Spending','$146','Strategic, disciplined card usage'],
     ['LTV Estimate','$3-5K','Premium long-term value — churn is structural loss'],
     ['Pmt Consistency','16.4x min','Financially disciplined; no repayment risk'],
     ['Rev/Customer','$400-500','Highest profitability in portfolio']],
    [1.5*inch,1.02*inch,3.13*inch],
    [('Phase 1 (Wk 1-2)','VIP recognition and dedicated service access before any cross-sell. '
      'Relationship anchoring reduces price sensitivity.'),
     ('Phase 2 (Wk 3-8)','Premium card tier (2-3% cashback); personal loans at 2-3% below market; '
      'credit-limit increases tested with holdouts.'),
     ('Phase 3 (Wk 9+)','Annual events; $100 referral incentives; quarterly business reviews; personalised roadmap.')],
    '$405K/yr','$600K-$1M revenue growth','3-4x first year, 6x+ sustained')

# ── Slide 8: Engaged Optimizers ───────────────────────────────────────────────
seg(8,'Engaged Optimizers',
    '1,312 Customers (14.7%)  |  Avg Balance $3,117  |  Risk: MODERATE  |  Action: Optimize',ORANGE,
    ['Utilization Rate','Payment Quality','Engagement','Financial Health'],[50,5,56,60],
    [('Monthly Spending','$242 (HIGHEST)'),('Engagement','0.56 (PEAK)'),
     ('Utilization','49.9%'),('Full Pmt Rate','4.6%'),
     ('Pmt Consistency','5.12x min'),('Annual Revenue','$250-350')],
    [['Metric','Value','Insight'],
     ['Monthly Spending','$242','Most active cohort — highest purchase frequency'],
     ['Engagement Score','0.56','Peak engagement; stickiest segment after Prime'],
     ['Balance','$3,117 (49.9%)','Deliberate balance management, not stress'],
     ['Pmt Consistency','5.12x min','Methodical repayment — not a default risk'],
     ['Churn Risk','LOW','High engagement is the strongest retention anchor'],
     ['Rev/Customer','$250-350','Reliable, recurring revenue base']],
    [1.5*inch,1.08*inch,3.07*inch],
    [('Phase 1 (Wk 1-4)','Enhanced rewards: 2x points on first $500/month; partner-merchant bonuses. '
      'Frame as a spending tool, not a debt solution.'),
     ('Phase 2 (Wk 5-8)','0% APR installment plans; balance-transfer campaigns; debt-consolidation offers. '
      'Do not apply Distressed intervention playbook here.'),
     ('Phase 3 (Wk 9+)','Business Owner Circle: community, monthly webinars, personalised spending insights.')],
    '$295K/yr','+$1.3M balance growth + improved retention','4-5x')

# ── Slide 9: Low Capacity / Disengaged ───────────────────────────────────────
seg(9,'Low Capacity / Disengaged',
    '3,210 Customers (35.9%)  |  Avg Balance $698  |  Risk: LOW  |  Action: Activate or Exit',BLUE,
    ['Utilization Rate','Payment Quality','Engagement','Financial Health'],[15,7,23,70],
    [('Monthly Spending','$48 (LOWEST)'),('Engagement','0.23 (LOWEST)'),
     ('Utilization','15.1%'),('Annual Revenue','$20-50'),
     ('Pmt Consistency','6.9x min'),('Lifetime Value','$300-600')],
    [['Metric','Value','Challenge'],
     ['Monthly Spending','$48','Portfolio floor; mostly inactive accounts'],
     ['Engagement Score','0.23','Lowest engagement — high churn vulnerability'],
     ['Utilization','15.1%','Minimal credit usage; no active relationship'],
     ['Annual Revenue','$20-50','May not cover cost-to-serve ($60-80 est.)'],
     ['Churn Risk','HIGH','Low stickiness — easy to lose without notice'],
     ['LTV','$300-600','Portfolio drag without activation']],
    [1.5*inch,1.0*inch,3.15*inch],
    [('Activate 50%','Win-back: 5% cashback on groceries/gas for 3 months; micro-incentives. '
      'Target clean dormant accounts only — suppress payment-stressed customers.'),
     ('Digitise 30%','Auto-paydown, digital servicing, automated statements to reduce cost-to-serve. '
      'Calculate account P&L before any offer.'),
     ('Exit 20%','After 90-day activation attempt: close/downgrade non-responsive accounts. '
      'Estimated $500K+ cost savings.')],
    '$155K/yr','$200K revenue + $500K cost savings','4.7x (cost reduction focus)')

# ── Slide 10: High Risk / New Customers ──────────────────────────────────────
seg(10,'High Risk / New Customers',
    '701 Customers (7.8%)  |  Avg Balance $1,068  |  Risk: MEDIUM-HIGH  |  Action: Prevent Deterioration',PINK,
    ['Utilization Rate','Payment Quality','Engagement','Financial Health'],[35,14,32,45],
    [('Tenure','0.6 yrs (NEW)'),('Balance','$1,068 (34.9%)'),
     ('Full Pmt Rate','14.1%'),('Engagement','0.32'),
     ('Deterioration Risk','50-60%'),('Prevention ROI','10:1')],
    [['Metric','Value','Risk Signal'],
     ['Tenure','0.6 yrs','Critical early-relationship window active now'],
     ['Balance','$1,068 (34.9%)','Emerging stress — early deterioration'],
     ['Full Payment','14.1%','Payment difficulty emerging; not yet acute'],
     ['Deterioration Risk','50-60%','Will migrate to Distressed without action'],
     ['Prevention ROI','10:1','Intervening now is 10x cheaper than curing later'],
     ['Default Prob.','+15-25% above base','Elevated and rising without intervention']],
    [1.5*inch,1.08*inch,3.07*inch],
    [('Phase 1 (Wk 1-2)','Early-warning scoring: flag late payments, usage spikes, balance acceleration. '
      'Daily automated alerts. Do not wait for 30+ DPD.'),
     ('Phase 2 (Wk 3-8)','Proactive financial check-ins; hardship conversations; income verification; '
      'assistance referrals. Frame as service, not surveillance.'),
     ('Phase 3 (Wk 9+)','Credit builder: auto limit-increases for consecutive on-time payments; '
      'rate reductions tied to repayment behaviour; financial literacy tools.')],
    '$295K/yr','$3-5M default prevention','3-5x')

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 11 — RECOMMENDATIONS
# ══════════════════════════════════════════════════════════════════════════════
H('Recommendations & 90-Day Plan',
  'Implementation Roadmap  |  Total Investment $1.45-1.50M  =>  Expected Benefit $2.2-4.7M',
  'Slide 11')
story.append(roi_chart()); story.append(Spacer(1,7))
story.append(Table([
    ['Initiative','Priority','Investment','Expected Benefit','ROI','Owner'],
    ['Distressed Intervention','URGENT — Month 1','$305-355K','$1-2M loss prevention','3-5x','Risk Team'],
    ['High Risk Prevention',  'URGENT — Month 1','$295K',    '$3-5M default prevention','3-5x','Risk Team'],
    ['Prime Growth',          'HIGH — Month 2',  '$405K',    '$600K-$1M revenue',       '2.4x','Product'],
    ['Engaged Optimization',  'HIGH — Month 2',  '$295K',    '$400-600K revenue',        '2.5x','Marketing'],
    ['Low Cap Activation',    'EFF — Month 3',   '$155K',    '$200K rev + $500K savings','4.7x','Operations'],
    ['TOTAL PORTFOLIO',       'Months 1-3',      '$1.45-1.50M','$2.2-4.7M benefit',    '2.5-3.5x','Leadership'],
],colWidths=[1.72*inch,1.2*inch,0.9*inch,1.42*inch,0.65*inch,0.9*inch],
style=TableStyle([
    ('BACKGROUND',(0,0),(-1,0),PURPLE),('TEXTCOLOR',(0,0),(-1,0),WHITE),
    ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
    ('BACKGROUND',(0,-1),(-1,-1),DARK_PUR),('TEXTCOLOR',(0,-1),(-1,-1),WHITE),
    ('FONTNAME',(0,-1),(-1,-1),'Helvetica-Bold'),
    ('FONTSIZE',(0,0),(-1,-1),8),('ALIGN',(0,0),(-1,-1),'CENTER'),
    ('ROWBACKGROUNDS',(0,1),(-1,-2),[WHITE,LIGHT_BG]),
    ('GRID',(0,0),(-1,-1),0.4,LG),
    ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)])))
story.append(Spacer(1,6))
story.append(Paragraph(
    '<b>Monthly KPIs:</b>  Default rate by segment  |  Early-warning detection rate (target 70%)  |  '
    'Prime upgrade rate (target 40%)  |  Engaged balance growth (+15% YoY)  |  '
    'Churn: Prime >95%, Engaged >92%  |  NPS by segment',sBody))

# ── Build ──────────────────────────────────────────────────────────────────────
OUT = '/Users/pradark/Work/Clustering/Customer_Segmentation_NDR.pdf'
doc = SimpleDocTemplate(OUT, pagesize=landscape(A4),
                        leftMargin=LEFT, rightMargin=RIGHT,
                        topMargin=TOP, bottomMargin=BOT)
doc.build(story)
import os
sz = os.path.getsize(OUT)/1024
print(f"PDF saved -> {OUT}  ({sz:.0f} KB)")
