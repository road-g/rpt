import os,io,re,json,time,hashlib,html,requests
from datetime import datetime,timezone,timedelta
from bs4 import BeautifulSoup
from pypdf import PdfReader
import anthropic
B="https://finance.naver.com/research/";H={"User-Agent":"Mozilla/5.0"}
DB="data/db.json";OUT="docs";KST=timezone(timedelta(hours=9))
SITE=os.getenv("SITE_URL","").rstrip("/");ADC=os.getenv("ADSENSE_CLIENT","");ADS=os.getenv("ADSENSE_SLOT","")
TGT=os.getenv("TG_TOKEN","");TGC=os.getenv("TG_CHAT","");MX=int(os.getenv("MAX_PER_RUN","12"));MDL=os.getenv("MODEL","claude-sonnet-5")
TPL=open("tpl.html",encoding="utf-8").read()
def ld():return json.load(open(DB,encoding="utf-8")) if os.path.exists(DB) else {}
def sv(d):os.makedirs("data",exist_ok=True);json.dump(d,open(DB,"w",encoding="utf-8"),ensure_ascii=False,indent=1)
def sg(u):return hashlib.md5(u.encode()).hexdigest()[:6]
def ls(pg=1):
    r=requests.get(f"{B}company_list.naver?page={pg}",headers=H,timeout=20);r.encoding="euc-kr"
    res=[]
    for tr in BeautifulSoup(r.text,"html.parser").select("table.type_1 tr"):
        td=tr.find_all("td")
        if len(td)<5:continue
        f=td[3].find("a")
        if not f or ".pdf" not in f.get("href",""):continue
        res.append({"nm":td[0].get_text(strip=True),"ti":td[1].get_text(strip=True),"br":td[2].get_text(strip=True),"pdf":f["href"],"dt":td[4].get_text(strip=True)})
    return res
def txt(u):
    b=requests.get(u,headers=H,timeout=30).content
    return "\n".join((p.extract_text() or "") for p in PdfReader(io.BytesIO(b)).pages[:4])[:9000]
PR="""다음은 증권사 기업분석 리포트 본문 일부입니다. 개인투자자용 요약을 JSON으로만 출력하세요. 코드블록·설명 금지.
규칙: 원문 문장을 그대로 옮기지 말고 반드시 본인 표현으로 재서술. 각 항목 80자 이내.
형식: {"hl":"한줄 핵심(40자 이내)","pts":["요점1","요점2","요점3"],"op":"투자의견 또는 빈문자열","tp":"목표주가(숫자+원) 또는 빈문자열","rk":"리스크 한줄"}
종목:%s / 제목:%s / 증권사:%s
본문:
%s"""
def sm(c,it,t):
    m=c.messages.create(model=MDL,max_tokens=800,messages=[{"role":"user","content":PR%(it["nm"],it["ti"],it["br"],t)}])
    s=re.sub(r"```json|```","","".join(x.text for x in m.content if x.type=="text")).strip()
    return json.loads(s[s.find("{"):s.rfind("}")+1])
def ad():
    if not ADC:return '<div class="adph">광고 영역</div>'
    return f'<ins class="adsbygoogle" style="display:block" data-ad-client="{ADC}" data-ad-slot="{ADS}" data-ad-format="auto" data-full-width-responsive="true"></ins><script>(adsbygoogle=window.adsbygoogle||[]).push({{}});</script>'
def pg(k,it):
    e=html.escape;s=it["s"]
    li="".join(f"<li>{e(p)}</li>" for p in s.get("pts",[]))
    mt="".join(f'<div class="kv"><span>{a}</span><b>{e(b)}</b></div>' for a,b in (("투자의견",s.get("op")),("목표주가",s.get("tp"))) if b)
    r={"{{T}}":e(f'{it["nm"]} | {s.get("hl","")} - {it["br"]}'),"{{D}}":e(" ".join(s.get("pts",[]))[:150]),"{{NM}}":e(it["nm"]),"{{BR}}":e(it["br"]),"{{DT}}":e(it["dt"]),"{{TI}}":e(it["ti"]),"{{HL}}":e(s.get("hl","")),"{{PTS}}":li,"{{MT}}":mt,"{{RK}}":e(s.get("rk","")),"{{PDF}}":e(it["pdf"]),"{{AD}}":ad(),"{{ADH}}":hd(),"{{CAN}}":f"{SITE}/r/{k}.html"}
    o=TPL
    for a,b in r.items():o=o.replace(a,b)
    os.makedirs(f"{OUT}/r",exist_ok=True);open(f"{OUT}/r/{k}.html","w",encoding="utf-8").write(o)
def hd():return f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADC}" crossorigin="anonymous"></script>' if ADC else ""
def idx(d):
    e=html.escape;its=sorted(d.items(),key=lambda x:x[1]["ts"],reverse=True)[:150]
    rows="".join(f'<a class="row" href="r/{k}.html"><span class="nm">{e(v["nm"])}</span><span class="hl">{e(v["s"].get("hl",""))}</span><span class="mu">{e(v["br"])} {e(v["dt"])}</span></a>' for k,v in its)
    o=open("idx.html",encoding="utf-8").read().replace("{{ROWS}}",rows).replace("{{ADH}}",hd()).replace("{{AD}}",ad()).replace("{{UP}}",datetime.now(KST).strftime("%Y-%m-%d %H:%M"))
    open(f"{OUT}/index.html","w",encoding="utf-8").write(o)
    open(f"{OUT}/sitemap.xml","w").write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+f"<url><loc>{SITE}/</loc></url>"+"".join(f"<url><loc>{SITE}/r/{k}.html</loc></url>" for k,_ in its)+"</urlset>")
    open(f"{OUT}/robots.txt","w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    if ADC:open(f"{OUT}/ads.txt","w").write(f"google.com, {ADC.replace('ca-','')}, DIRECT, f08c47fec0942fa0\n")
    open(f"{OUT}/.nojekyll","w").close()
def tg(k,it):
    if not(TGT and TGC):return
    s=it["s"];m=f'[{it["br"]}] {it["nm"]}\n{s.get("hl","")}\n'+"\n".join("- "+p for p in s.get("pts",[]))+f"\n\n{SITE}/r/{k}.html"
    requests.post(f"https://api.telegram.org/bot{TGT}/sendMessage",json={"chat_id":TGC,"text":m,"disable_web_page_preview":False},timeout=20);time.sleep(3)
def run():
    d=ld();c=anthropic.Anthropic();nw=[]
    for p in (1,2):
        for it in ls(p):
            k=sg(it["pdf"])
            if k in d or len(nw)>=MX:continue
            try:it["s"]=sm(c,it,txt(it["pdf"]))
            except Exception as ex:print("skip",it["nm"],ex);continue
            it["ts"]=time.time();d[k]=it;pg(k,it);nw.append(k);print("ok",k,it["nm"]);time.sleep(2)
    for k in reversed(nw):tg(k,d[k])
    sv(d);idx(d);print("new",len(nw))
if __name__=="__main__":run()
