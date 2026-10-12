from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
S='/tmp/claude-0/-home-user/f19a087c-4085-5aef-b35a-89b81156bb55/scratchpad/'
IM=S.replace('scratchpad/','images/'); F=S+'fonts/'; OUT=S+'carrossel/'
REG,ITA,BLK,B8,CUR=F+'Merriweather-400-normal.ttf',F+'Merriweather-400-italic.ttf',F+'Merriweather-900-normal.ttf',F+'Merriweather-800-normal.ttf',F+'Satisfy-400-normal.ttf'
ROXO,ROSE,BRANCO,FRAMB,AMEIXA='#241751','#e29f8e','#eae8ec','#b53b70','#623079'
W,H=1080,1350; M=90
f=lambda p,s: ImageFont.truetype(p,s)

def base(): return Image.new('RGB',(W,H),ROXO)
def assina(d,n):
    d.text((M,H-70),'@giselehedler',font=f(ITA,24),fill='#c3bad6',anchor='ls')
    d.text((W-M,H-70),f'{n}/10',font=f(REG,22),fill='#8f83b3',anchor='rs')

def wrap(d,txt,font,maxw):
    out=[]
    for par in txt.split('\n'):
        words=par.split(' '); line=''
        for w_ in words:
            t=(line+' '+w_).strip()
            if d.textlength(t,font=font)<=maxw: line=t
            else: out.append(line); line=w_
        out.append(line)
    return out

def bloco(d,y,txt,font,cor,maxw=W-2*M,lh=1.38,align='center'):
    for l in wrap(d,txt,font,maxw):
        if align=='center': d.text((W/2,y),l,font=font,fill=cor,anchor='ms')
        else: d.text((M,y),l,font=font,fill=cor,anchor='ls')
        y+=int(font.size*lh)
    return y

def titulo_cursiva(d,y,linhas,cursiva,tsz=72,csz=92,cor=BRANCO,cc=ROSE):
    ft=f(BLK,tsz)
    for l in linhas:
        d.text((W/2,y),l,font=ft,fill=cor,anchor='ms'); last=y; y+=int(tsz*1.16)
    if cursiva:
        d.text((W/2,last+int(csz*0.62)),cursiva,font=f(CUR,csz),fill=cc,anchor='ms')
        return last+int(csz*0.62)+int(csz*0.55)
    return y

def gradiente(img,de=0.35,forca=235):
    g=Image.new('L',(1,H))
    for y in range(H):
        t=max(0,(y/H-de)/(1-de)); g.putpixel((0,y),int(forca*min(1,t*1.25)))
    preto=Image.new('RGB',(W,H),'#000'); img.paste(preto,(0,0),g.resize((W,H)))
    return img

def foto(path,foco_y=0.3):
    im=Image.open(path).convert('RGB'); r=max(W/im.width,H/im.height)
    im=im.resize((int(im.width*r),int(im.height*r)),Image.LANCZOS)
    x=(im.width-W)//2; y=int((im.height-H)*foco_y)
    return im.crop((x,y,x+W,y+H))

# 1 capa
img=gradiente(foto(IM+'12.jpg',0.0),de=0.40); d=ImageDraw.Draw(img)
y=titulo_cursiva(d,930,['POR QUE FILHAS','DE PAIS AUSENTES'],'se atraem',tsz=74,csz=100)
bloco(d,y+40,'pelos homens que vão abandoná-las?',f(REG,40),BRANCO)
d.text((W/2,H-55),'@giselehedler',font=f(ITA,24),fill='#d8d2e0',anchor='ms')
img.save(OUT+'01.png')

# 2 teste 1
img=base(); d=ImageDraw.Draw(img)
y=titulo_cursiva(d,200,['SEU PAI ERA'],'presente, mas',tsz=66,csz=90)
itens=['Nunca perguntou como foi o seu dia de verdade','Só te procurava quando precisava de algo','Estava sempre "ocupado demais" para você','Você competia com o trabalho ou a TV pela atenção dele','Elogiava mais os outros do que você','Você sentia que incomodava quando precisava dele','A única vez que te abraçou foi num momento extremo']
y+=30; fi=f(REG,33)
for it in itens:
    d.rounded_rectangle((M,y-30,M+30,y),5,outline=ROSE,width=3)
    yy=y
    for l in wrap(d,it,fi,W-2*M-55):
        d.text((M+52,yy),l,font=fi,fill=BRANCO,anchor='ls'); yy+=44
    y=yy+22
y+=20
y=bloco(d,y,'Marcou 3 ou mais?',f(B8,40),ROSE)
bloco(d,y,'Seu pai era ausente. Mesmo estando em casa.',f(REG,36),BRANCO)
assina(d,2); img.save(OUT+'02.png')

# 3 o que ela aprende
img=base(); d=ImageDraw.Draw(img)
y=bloco(d,230,'Quando uma menina cresce com pai ausente,',f(REG,42),BRANCO)
y=titulo_cursiva(d,y+10,[],None)
d.text((W/2,y+40),'ela aprende',font=f(CUR,96),fill=ROSE,anchor='ms'); y+=150
for a,b in [('Amor precisa ser conquistado.','(não é dado naturalmente)'),('Eu não valho atenção.','(por isso ele não dava)'),('Pedir é ser um fardo.','(por isso ele fugia)'),('Homem vai embora.','(é só questão de tempo)')]:
    d.text((W/2,y),a,font=f(B8,42),fill=BRANCO,anchor='ms'); d.text((W/2,y+48),b,font=f(ITA,30),fill='#c3bad6',anchor='ms'); y+=135
y+=30
y=bloco(d,y,'Não foi escolha.',f(BLK,46),ROSE)
bloco(d,y,'Foi o que ela aprendeu.',f(REG,40),BRANCO)
assina(d,3); img.save(OUT+'03.png')

# 4 relatos
img=base(); d=ImageDraw.Draw(img)
y=bloco(d,140,'O impacto na vida adulta.',f(REG,40),BRANCO)
d.text((W/2,y+40),'relatos de seguidoras',font=f(CUR,84),fill=ROSE,anchor='ms'); y+=150
for q in ['Fui traída e perdi totalmente a minha autoestima.','Meu casamento está abalado.','Me sinto sozinha, não confio em mais ninguém.','Me envolvi com um homem que me fez muito mal.','Repito padrões que jurei nunca repetir.']:
    ls=wrap(d,'"'+q+'"',f(ITA,35),W-2*M-60); hh=len(ls)*48+44
    d.rounded_rectangle((M,y,W-M,y+hh),22,fill='#2e2063')
    yy=y+60
    for l in ls: d.text((W/2,yy),l,font=f(ITA,35),fill=BRANCO,anchor='ms'); yy+=48
    y+=hh+20
assina(d,4); img.save(OUT+'04.png')

# 5 hoje você é a mulher que
img=base(); d=ImageDraw.Draw(img)
y=titulo_cursiva(d,220,['HOJE VOCÊ É'],'a mulher que',tsz=70,csz=96)
y+=40
for it in ['Se apaixona por quem te ignora','Persegue quem está indo embora','Aceita traição porque "pelo menos ele ficou"','Entra em pânico quando ele demora a responder','Agradece migalhas','Sabota quem te trata bem']:
    y=bloco(d,y,it,f(REG,38),BRANCO,lh=1.3)+26
y+=30
y=bloco(d,y,'Você passa a vida provando',f(B8,44),ROSE)
bloco(d,y,'que merece ficar.',f(B8,44),ROSE)
assina(d,5); img.save(OUT+'05.png')

# 6 ciclo
img=base(); d=ImageDraw.Draw(img)
y=titulo_cursiva(d,200,['O CICLO QUE VOCÊ'],'repete sem perceber',tsz=62,csz=82)
y+=30
passos=['Conhece um homem emocionalmente indisponível','Se esforça demais para conquistá-lo','Recebe migalhas de atenção','Acha que é amor, porque parece com o seu pai','Se destrói tentando ser suficiente','Ele vai embora ou te trai','Você se culpa e começa de novo']
for i,p in enumerate(passos,1):
    d.ellipse((M,y-34,M+44,y+10),fill=FRAMB); d.text((M+22,y-12),str(i),font=f(B8,26),fill=BRANCO,anchor='mm')
    yy=y
    for l in wrap(d,p,f(REG,33),W-2*M-70): d.text((M+68,yy),l,font=f(REG,33),fill=BRANCO,anchor='ls'); yy+=44
    y=yy+26
y+=20
y=bloco(d,y,'Você não escolhe homens ruins.',f(REG,38),BRANCO)
y=bloco(d,y,'Você escolhe homens que fazem você',f(B8,40),ROSE)
d.text((W/2,y+30),'se sentir em casa.',font=f(CUR,86),fill=ROSE,anchor='ms')
assina(d,6); img.save(OUT+'06.png')

# 7 teste 2
img=base(); d=ImageDraw.Draw(img)
y=titulo_cursiva(d,220,['QUANDO UM HOMEM'],'te trata bem',tsz=66,csz=92)
y+=20; y=bloco(d,y,'você:',f(REG,40),BRANCO)+10
for it in ['Desconfia?','Acha que é bom demais para ser verdade?','Fica esperando ele ir embora?','Se sente desconfortável?','Sabota de propósito?']:
    y=bloco(d,y,it,f(B8,38),BRANCO,lh=1.3)+18
y+=40
y=bloco(d,y,'Se você respondeu sim, a ausência do seu pai ainda está controlando a sua vida amorosa.',f(REG,36),BRANCO)
y+=20
d.text((W/2,y+30),'Ainda. Não para sempre.',font=f(CUR,82),fill=ROSE,anchor='ms')
assina(d,7); img.save(OUT+'07.png')

# 8 prova (comentários da Quinta, sem nome)
img=base(); d=ImageDraw.Draw(img)
y=titulo_cursiva(d,180,['O QUE ELAS ESCREVERAM'],'depois de uma quinta',tsz=52,csz=80)
y+=30
coms=['Amada, a aula de hoje foi um grande presente. Tenho muitos irmãos e problema com alguns deles, e com filhos e um ex-marido também, justamente pelo jeito de serem. Acendeu uma luz no fundo do túnel!',
      'Mais uma aula que chorei. Já perdoei quem precisava perdoar, e essa aula foi um presente que chegou na hora pra eu perceber isso!',
      'Foi muito esclarecedor! O que não aceitamos no outro muitas vezes está em nós! E perdoar e se libertar de certas mágoas familiares é primordial para viver em paz!']
fc=f(REG,29)
for c in coms:
    ls=wrap(d,c,fc,W-2*M-150); hh=len(ls)*40+70
    d.rounded_rectangle((M,y,W-M,y+hh),26,fill=BRANCO)
    d.ellipse((M+26,y+26,M+86,y+86),fill='#c9c2d6')
    d.rounded_rectangle((M+110,y+28,M+290,y+48),8,fill='#d9d4e2')
    yy=y+82
    for l in ls: d.text((M+110,yy),l,font=fc,fill='#1b1530',anchor='ls'); yy+=40
    d.text((W-M-30,y+44),'♥',font=f(REG,30),fill='#e0245e',anchor='rm') if False else None
    y+=hh+26
bloco(d,y+30,'Comentários reais de alunas da Quinta da Mente.',f(ITA,26),'#c3bad6')
assina(d,8); img.save(OUT+'08.png')

# 9 como romper
img=base(); d=ImageDraw.Draw(img)
y=titulo_cursiva(d,210,['COMO ROMPER'],'esse ciclo',tsz=72,csz=100)
y+=40
for n,t,x in [('1','Revelação','Identificar como a ausência do seu pai moldou os seus relacionamentos.'),('2','Separação','O seu pai não é todos os homens. Parar de buscar no parceiro o que ele nunca deu.'),('3','Reconexão','O seu valor real, não o valor que ele te fez acreditar.'),('4','Nova vida','Receber amor sem pânico, sem sabotagem, sem achar que vai acabar.')]:
    d.text((M,y),f'{n}. {t}',font=f(BLK,40),fill=ROSE,anchor='ls'); y+=52
    yy=y
    for l in wrap(d,x,f(REG,34),W-2*M): d.text((M,yy),l,font=f(REG,34),fill=BRANCO,anchor='ls'); yy+=46
    y=yy+40
assina(d,9); img.save(OUT+'09.png')

# 10 final com foto do palco (sem o telão)
im=Image.open(IM+'13.jpg').convert('RGB').crop((60,440,1260,1940))
r=W/im.width; im=im.resize((W,int(im.height*r)),Image.LANCZOS)
img=Image.new('RGB',(W,H),'#000'); img.paste(im.crop((0,0,W,min(H,im.height))),(0,0))
img=gradiente(img,de=0.30,forca=245); d=ImageDraw.Draw(img)
y=titulo_cursiva(d,860,['VOCÊ NÃO PRECISA PROVAR'],'que merece ficar',tsz=54,csz=88)
y+=20
y=bloco(d,y,'Na Quinta da Mente eu aprofundo isso, ao vivo e de graça. Quinta, 18:59.',f(REG,34),BRANCO)
y+=10
bloco(d,y,'Comenta 5524 que eu te mando o link.',f(B8,40),ROSE)
d.text((W/2,H-45),'@giselehedler',font=f(ITA,24),fill='#d8d2e0',anchor='ms')
img.save(OUT+'10.png')


from PIL import ImageChops
def centralizar(path):
    im=Image.open(path).convert('RGB'); area=im.crop((0,0,W,H-110))
    bg=Image.new('RGB',area.size,ROXO); bb=ImageChops.difference(area,bg).convert('L').point(lambda v:255 if v>4 else 0).getbbox()
    if not bb: return
    top,bot=bb[1],bb[3]; alvo=(H-110-(bot-top))//2
    novo=Image.new('RGB',(W,H),ROXO); novo.paste(area.crop((0,top,W,bot)),(0,alvo)); novo.paste(im.crop((0,H-110,W,H)),(0,H-110))
    novo.save(path)
for i in range(2,10): centralizar(OUT+f'{i:02d}.png')
# folha de contato
th=[Image.open(OUT+f'{i:02d}.png').resize((360,450)) for i in range(1,11)]
sheet=Image.new('RGB',(360*5+40,450*2+30),'#111')
for i,t in enumerate(th): sheet.paste(t,(10+(i%5)*364,10+(i//5)*460))
sheet.save(OUT+'contato.png')
