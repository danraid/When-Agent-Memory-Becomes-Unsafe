"""New pt-BR neural scientific narration, with speech-friendly equations and tables."""
import concurrent.futures,hashlib,json,os,re,subprocess,time,urllib.request,urllib.error,wave
from pathlib import Path
import imageio_ffmpeg
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"audio/artigo_exploratorio_pt_br.md"
OUT=ROOT/"audio/generated_exploratory"
TMP=ROOT/"audio/tmp_exploratory_chunks"
VOICE=os.getenv("AUDIO_VOICE","marin")
MODEL="gpt-4o-mini-tts"
STYLE=("Narradora profissional brasileira de audiolivros científicos. "
"Voz humana, natural e acolhedora, sem teatralização ou timbre robótico. "
"Português do Brasil com pronúncia brasileira genuína, ritmo conversacional "
"em torno de 140 palavras por minuto, boa articulação, entonação orgânica "
"e pequenas pausas após frases. Preserve conceitos e números, sem acrescentar "
"explicações. Leia siglas e expressões técnicas com cuidado. "
"Use consistentemente a mesma voz em todos os trechos.")

def plain(text):
    text=text.replace("**","").replace(chr(96),"")
    text=re.sub(r"\*([^*]+)\*",r"\1",text)
    text=re.sub(r"\[([^\]]+)\]\([^)]+\)",r"\1",text)
    text=re.sub(r"https?://\S+","endereço disponível no artigo em PDF",text)
    repl={"28 × 28":"vinte e oito por vinte e oito","CHSH":"C H S H",
          "FLRW":"F L R W","U(1)":"U um","k²":"cá ao quadrado",
          "ω²":"ômega ao quadrado","α":"alfa","σ":"sigma",
          "3+1D":"três dimensões espaciais e uma temporal",
          "≥":"maior ou igual a","≤":"menor ou igual a",
          "×":" por ","≈":"aproximadamente"}
    for a,b in repl.items():text=text.replace(a,b)
    text=re.sub(r"\bN(\d)(\d)\b",r"módulo N \1 \2",text)
    return re.sub(r"\s+"," ",text).strip()

def table_speech(lines,n):
    rows=[]
    for line in lines:
        cells=[plain(c.strip()) for c in line.strip("|").split("|")]
        if all(set(x)<=set("-: ") for x in cells):continue
        rows.append(cells)
    if not rows:return []
    output=[]
    for row in rows[1:]:
        if len(row)<2:continue
        if n==1 and len(row)==4:
            output.append(f"No programa {row[0]}, foram realizados {row[1]} ciclos e {row[2]} unidades. Escopo: {row[3]}.")
        elif n==2 and len(row)==4:
            output.append(f"Na semente {row[0]}, o mundo tinha {row[1]} partículas. Houve {row[2]} células diferentes entre os modelos com e sem colisão, e variação de {row[3]} por quadrante.")
        elif n==3 and len(row)==4:
            output.append(f"Para espaçamento {row[0]}, o erro no eixo foi {row[1]}; o erro na diagonal foi {row[2]}; e o contraste de anisotropia foi {row[3]}.")
        else:
            output.append("; ".join(f"{a}: {b}" for a,b in zip(rows[0],row))+".")
    return output

def prepare():
    paragraphs=[];lines=SRC.read_text(encoding="utf8").splitlines()
    i=0;skip=False;table_num=0
    while i<len(lines):
        line=lines[i].strip();i+=1
        if not line:continue
        if line.startswith("## Abstract"):skip=True;continue
        if skip:
            if line.startswith("## 1. "):skip=False
            else:continue
        if line.startswith("## Referências"):
            paragraphs.append("Referências bibliográficas.")
            paragraphs.append("A lista completa das referências, dos títulos originais e dos identificadores está disponível no artigo escrito em PDF.")
            break
        if line.startswith("!["):continue
        if line=="$$":
            formula=[]
            while i<len(lines) and lines[i].strip()!="$$":
                formula.append(lines[i]);i+=1
            i+=1
            form=" ".join(formula)
            if "sum" in form:
                paragraphs.append("Ômega ao quadrado é igual a quatro dividido por a ao quadrado, multiplicado pelo somatório, de um a três, do seno ao quadrado de a vezes a componente do vetor de onda, dividida por dois.")
            else:
                paragraphs.append("No limite contínuo, ômega ao quadrado é igual ao módulo do vetor de onda cá, elevado ao quadrado.")
            continue
        if line.startswith("|"):
            current=[line]
            while i<len(lines) and lines[i].strip().startswith("|"):
                current.append(lines[i].strip());i+=1
            paragraphs.extend(table_speech(current,table_num))
            continue
        match=re.search(r"Tabela\s+(\d+)",line)
        if match:table_num=int(match.group(1))
        if line.startswith("## "):paragraphs.append(plain(line[3:])+".");continue
        if line.startswith("### "):paragraphs.append(plain(line[4:])+".");continue
        if line.startswith("# "):paragraphs.append(plain(line[2:])+".");continue
        if line.startswith("---"):continue
        if line.startswith("- "):line=line[2:]
        paragraphs.append(plain(line))
    OUT.mkdir(parents=True,exist_ok=True)
    text="\n\n".join(paragraphs)+"\n"
    (OUT/"roteiro_narrado.txt").write_text(text,encoding="utf8")
    if len(text)<8500:raise ValueError("Unexpectedly short narration source")
    return paragraphs,text

def segments(paragraphs,limit=1600):
    result=[];current=""
    for p in paragraphs:
        sentences=re.split(r"(?<=[.!?])\s+(?=[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ0-9])",p)
        for sentence in sentences:
            if len(sentence)>limit:
                pieces=re.split(r"(?<=;)\s+",sentence)
            else:pieces=[sentence]
            for part in pieces:
                if current and len(current)+len(part)+2>limit:
                    result.append(current);current=""
                while len(part)>limit:
                    idx=part.rfind(" ",0,limit)
                    if idx<400:idx=limit
                    if current:result.append(current);current=""
                    result.append(part[:idx]);part=part[idx:].lstrip()
                current=(current+" "+part).strip()
        if len(current)>1300:result.append(current);current=""
    if current:result.append(current)
    if not result or any(len(p)>4096 for p in result):raise ValueError("Invalid chunks")
    return result

def synth(index,text,key):
    path=TMP/f"narration_{index:03d}.wav"
    req=urllib.request.Request("https://api.openai.com/v1/audio/speech",
      data=json.dumps({"model":MODEL,"voice":VOICE,"input":text,
       "response_format":"wav","instructions":STYLE,"speed":0.98},ensure_ascii=False).encode(),
      method="POST",headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"})
    error=None
    for n in range(5):
        try:
            with urllib.request.urlopen(req,timeout=240) as r:payload=r.read()
            if not payload.startswith(b"RIFF") or len(payload)<10000:raise ValueError("Invalid TTS audio")
            path.write_bytes(payload)
            with wave.open(str(path),"rb") as w:
                if w.getnframes()<4000:raise ValueError("Too short")
            return index,path
        except (urllib.error.URLError,ValueError,TimeoutError) as e:
            error=e
            if isinstance(e,urllib.error.HTTPError) and e.code in (400,401,403):break
            time.sleep(min(2**n,12))
    raise RuntimeError(f"TTS failed for segment {index} ({type(error).__name__}, status {getattr(error,'code',None)})")

def main():
    paras,text=prepare();chunks=segments(paras)
    print(json.dumps({"chars":len(text),"chunks":len(chunks),"voice":VOICE}),flush=True)
    if os.getenv("PREPARE_ONLY")=="1":return
    key=os.getenv("OPENAI_API_KEY")
    if not key:raise RuntimeError("Missing OPENAI_API_KEY")
    TMP.mkdir(parents=True,exist_ok=True)
    results={}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        futures=[pool.submit(synth,i,t,key) for i,t in enumerate(chunks)]
        for f in concurrent.futures.as_completed(futures):
            idx,path=f.result();results[idx]=path
            print(f"Segment {len(results)}/{len(chunks)} ready",flush=True)
    merged=TMP/"complete.wav"
    with wave.open(str(results[0]),"rb") as f:params=f.getparams()
    with wave.open(str(merged),"wb") as out:
        out.setnchannels(params.nchannels)
        out.setsampwidth(params.sampwidth)
        out.setframerate(params.framerate)
        for i in range(len(chunks)):
            with wave.open(str(results[i]),"rb") as f:
                if f.getnchannels()!=params.nchannels or f.getsampwidth()!=params.sampwidth or f.getframerate()!=params.framerate:
                    raise ValueError("Inconsistent WAV format")
                out.writeframes(f.readframes(f.getnframes()))
            if i<len(chunks)-1:
                out.writeframes(b"\0"*(int(params.framerate*.22)*params.nchannels*params.sampwidth))
    audio=OUT/"artigo_pt_narracao_nova.mp3"
    ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([ffmpeg,"-y","-hide_banner","-loglevel","error","-i",str(merged),
      "-af","highpass=f=65,lowpass=f=12000,loudnorm=I=-18:TP=-1.5:LRA=9",
      "-c:a","libmp3lame","-b:a","160k",str(audio)],check=True)
    preview=OUT/"previa_narracao_nova_75s.mp3"
    subprocess.run([ffmpeg,"-y","-hide_banner","-loglevel","error",
      "-i",str(audio),"-t","75","-c:a","copy",str(preview)],check=True)
    with wave.open(str(merged),"rb") as w:
        duration=w.getnframes()/w.getframerate()
    if duration<420 or audio.stat().st_size<1_000_000:raise ValueError("Incomplete audio")
    manifest={"voice":VOICE,"model":MODEL,"locale":"pt-BR","segments":len(chunks),
      "duration_seconds":round(duration,2),"source_sha256":hashlib.sha256(SRC.read_bytes()).hexdigest(),
      "fresh_synthesis":True,"prior_voice_reused":False,
      "script_adaptation":["Portuguese-only audiobook","spoken equations","narrative tables",
       "bibliography accessible in accompanying PDF"]}
    (OUT/"audio_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({"duration_seconds":duration,"chunks":len(chunks),"size":audio.stat().st_size}),flush=True)
if __name__=="__main__":main()
