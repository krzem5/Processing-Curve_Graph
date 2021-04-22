import os
import re
import subprocess
import sys
import zipfile



SETUP_FUNC_REGEX=re.compile(br"(?:^|\s|;)void\s+setup\s*\([^\)]*?\)\s*\{",re.M)
FUNCTION_DECLARATION_REGEX=re.compile(br"((?:^|\s|;)\s*)((?:public|private|protected|final|static|abstract|transient|synchronized|volatile)\s+)*([a-zA-Z0-9_]+)(?:\s*\[\s*\])?\s+[a-zA-Z0-9_]+\s*\(",re.M)
IMPORT_REGEX=re.compile(br"(?:^|\s|;)(import\s+(?:static\s+)?[a-zA-Z0-9_$.]+(?:\.\*)?)")
FLOAT_REGEX=re.compile(br"[0-9]*\.[0-9]+\b")
PROCESSING_SETTING_METHODS=[b"smooth",b"noSmooth",b"size",b"pixelDensity",b"fullScreen"]
IDENTIFIER_CHARS=b"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
WHITE_SPACE_CHARS=b" \t\n\r\f\v"
KEYWORDS=[b"abstract",b"assert",B"break",b"case",b"catch",b"class",b"const",b"continue",b"default",b"do",b"else",b"enum",b"extends",b"final",b"finally",b"for",b"goto",b"implements",b"import",b"instanceof",b"interface",b"native",b"new",b"non-sealed",b"package",b"private",b"protected",b"publice",b"return",b"static",b"strictfp",b"super",b"switch",b"synchronized",b"this",b"throw",b"throws",b"transient",b"try",b"volatile",b"while"]



def _preprocess(dt,imp):
	i=0
	s=False
	c=False
	b=0
	bf=[[b"",-1]]
	while (i<len(dt)):
		if (not c and not s and dt[i:i+1]==b"{"):
			b+=1
		elif (not c and not s and dt[i:i+1]==b"}"):
			b-=1
		elif (not c and dt[i-1:i]!=b"\\" and dt[i:i+1]==b"\""):
			s=not s
		elif (not s and dt[i-1:i]!=b"\\" and dt[i:i+1]==b"'"):
			c=not c
		elif (b==0 and not s and not c):
			if (bf[-1][1]==-1):
				bf[-1][1]=i
			bf[-1][0]+=dt[i:i+1]
		elif (bf[-1][1]!=-1):
			bf.append([b"",-1])
		if (not s and not c and dt[i:i+1]==b"#"):
			for j in range(0,6):
				if (dt[i+j+1:i+j+2] not in b"0123456789abcdefABCDEF"):
					raise RuntimeError("Invalid Color!")
			dt=dt[:i]+b"0xff"+dt[i+1:]
			i-=1
		elif (not s and not c and (i==0 or dt[i-1:i] not in IDENTIFIER_CHARS) and dt[i:i+5]==b"color" and (i+5>=len(dt) or dt[i+5:i+6] not in IDENTIFIER_CHARS)):
			j=i+0
			i+=5
			while (dt[i:i+1] in WHITE_SPACE_CHARS):
				i+=1
			if (dt[i:i+1]!=b"("):
				dt=dt[:j]+b"int "+dt[i:]
				if (b==0 and not c and not s):
					bf[-1][0]=bf[-1][0][:-1]+b"int"
			elif (b==0 and not c and not s):
				bf[-1][0]+=b"olor"+b" "*(i-j-5)
			i-=1
		elif (not s and not c and (i==0 or dt[i-1:i] not in IDENTIFIER_CHARS) and dt[i:i+4]==b"byte" and (i+4>=len(dt) or dt[i+4:i+5] not in IDENTIFIER_CHARS)):
			j=i+0
			i+=4
			while (dt[i:i+1] in WHITE_SPACE_CHARS):
				i+=1
			if (dt[i:i+1]==b"("):
				dt=dt[:j]+b"PApplet.parseByte("+dt[i+1:]
				if (b==0 and not c and not s):
					bf[-1][0]=bf[-1][0][:-1]+b"PApplet.parseByte"
				i+=12
			elif (b==0 and not c and not s):
				bf[-1][0]+=b"yte"+b" "*(i-j-4)
				i-=1
			else:
				i-=1
		elif (not s and not c and (i==0 or dt[i-1:i] not in IDENTIFIER_CHARS) and dt[i:i+4]==b"char" and (i+4>=len(dt) or dt[i+4:i+5] not in IDENTIFIER_CHARS)):
			j=i+0
			i+=4
			while (dt[i:i+1] in WHITE_SPACE_CHARS):
				i+=1
			if (dt[i:i+1]==b"("):
				dt=dt[:j]+b"PApplet.parseChar("+dt[i+1:]
				if (b==0 and not c and not s):
					bf[-1][0]=bf[-1][0][:-1]+b"PApplet.parseChar"
				i+=12
			elif (b==0 and not c and not s):
				bf[-1][0]+=b"har"+b" "*(i-j-4)
				i-=1
			else:
				i-=1
		elif (not s and not c and (i==0 or dt[i-1:i] not in IDENTIFIER_CHARS) and dt[i:i+3]==b"int" and (i+3>=len(dt) or dt[i+3:i+4] not in IDENTIFIER_CHARS)):
			j=i+0
			i+=3
			while (dt[i:i+1] in WHITE_SPACE_CHARS):
				i+=1
			if (dt[i:i+1]==b"("):
				dt=dt[:j]+b"PApplet.parseInt("+dt[i+1:]
				if (b==0 and not c and not s):
					bf[-1][0]=bf[-1][0][:-1]+b"PApplet.parseInt"
				i+=11
			elif (b==0 and not c and not s):
				bf[-1][0]+=b"nt"+b" "*(i-j-3)
				i-=1
			else:
				i-=1
		elif (not s and not c and (i==0 or dt[i-1:i] not in IDENTIFIER_CHARS) and dt[i:i+5]==b"float" and (i+5>=len(dt) or dt[i+5:i+6] not in IDENTIFIER_CHARS)):
			j=i+0
			i+=5
			while (dt[i:i+1] in WHITE_SPACE_CHARS):
				i+=1
			if (dt[i:i+1]==b"("):
				dt=dt[:j]+b"PApplet.parseFloat("+dt[i+1:]
				if (b==0 and not c and not s):
					bf[-1][0]=bf[-1][0][:-1]+b"PApplet.parseFloat"
				i+=13
			elif (b==0 and not c and not s):
				bf[-1][0]+=b"loat"+b" "*(i-j-5)
				i-=1
			else:
				i-=1
		elif (not s and not c and (i==0 or dt[i-1:i] not in IDENTIFIER_CHARS)):
			m=FLOAT_REGEX.match(dt[i:])
			if (m is not None):
				dt=dt[:i+m.end(0)]+b"f"+dt[i+m.end(0):]
		i+=1
	for k in bf:
		i=0
		while (True):
			m=IMPORT_REGEX.search(k[0][i:])
			if (m is None):
				break
			imp.append(m.group(1))
			dt=dt[:k[1]+i+m.start()]+b" "*(m.end()-m.start())+dt[k[1]+i+m.end():]
			i+=m.end()
	return dt



if (not os.path.exists("__processing_core")):
	if (os.name=="nt"):
		if (subprocess.run(["dos2unix","install_processing.sh"]).returncode!=0):
			sys.exit(1)
	if (subprocess.run(["bash","install_processing.sh"]).returncode!=0):
		sys.exit(1)
if (os.path.exists("build")):
	dl=[]
	for r,ndl,fl in os.walk("build"):
		r=r.replace("\\","/").strip("/")+"/"
		dl=[r+k for k in ndl]+dl
		for f in fl:
			os.remove(r+f)
	for k in dl:
		os.rmdir(k)
else:
	os.mkdir("build")
lib_v=("application.windows64" if os.name=="nt" else "application.linux64")
lib=None
with open("__processing_core/export.txt","r") as f:
	for k in f.read().split("\n"):
		k=k.strip()
		if (k.split("=")[0]==lib_v):
			lib=["__processing_core/"+e for e in k.split("=")[1].split(",")]
			break
if (lib is None):
	raise RuntimeError("No Processing Libraries")
lm=[(2,"src/Main.java")]
with open("build/main.java","wb") as f,open("src/Main.pde","rb") as mf:
	imp=[b"import processing.core.*",b"import processing.data.*",b"import processing.event.*",b"import processing.opengl.*",b"import java.util.HashMap",b"import java.util.ArrayList",b"import java.io.File",b"import java.io.BufferedReader",b"import java.io.PrintWriter",b"import java.io.InputStream",b"import java.io.OutputStream",b"import java.io.IOException"]
	o_dt=b""
	mf_dt=_preprocess(mf.read(),imp)+b"\n"
	lc=mf_dt.count(b"\n")+2
	m=SETUP_FUNC_REGEX.search(mf_dt)
	s_func=b"\n@Override public void settings(){"
	if (m is not None):
		i=m.end(0)
		bf=[[b"",-1]]
		b=0
		s=False
		c=False
		while (b>0 or s or c or mf_dt[i:i+1]!=b"}"):
			if (not c and not s and mf_dt[i:i+1]==b"{"):
				b+=1
			elif (not c and not s and mf_dt[i:i+1]==b"}"):
				b-=1
			elif (not c and mf_dt[i-1:i]!=b"\\" and mf_dt[i:i+1]==b"\""):
				s=not s
			elif (not s and mf_dt[i-1:i]!=b"\\" and mf_dt[i:i+1]==b"'"):
				c=not c
			if (b==0 and not s and not c):
				if (bf[-1][1]==-1):
					bf[-1][1]=i
				bf[-1][0]+=mf_dt[i:i+1]
			elif (bf[-1][1]!=-1):
				bf.append([b"",-1])
			i+=1
		for nm in PROCESSING_SETTING_METHODS:
			p=re.compile(br"(?:^|\s|;)"+nm+br"\s*\(([^\)]*)\)\s*;",re.M|re.S)
			for k in bf:
				i=0
				while (True):
					m=p.search(k[0][i:])
					if (m is None):
						break
					s_func+=nm+b"("+m.group(1)+b");"
					mf_dt=mf_dt[:k[1]+i+m.start()]+b" "*(m.end()-m.start())+mf_dt[k[1]+i+m.end():]
					i+=m.end()
		o_dt+=mf_dt
	for fp in os.listdir("src"):
		fp=f"src/{fp}"
		if (os.path.isfile(fp) and fp[-4:].lower()==".pde" and fp.lower()!="src/main.pde"):
			with open(fp,"rb") as rf:
				lm.append((lc,fp))
				dt=_preprocess(rf.read(),imp)
				lc+=dt.count(b"\n")+1
				o_dt+=dt+b"\n"
	i=0
	while (True):
		m=FUNCTION_DECLARATION_REGEX.search(o_dt[i:])
		if (m is None):
			break
		if (m.group(3) not in KEYWORDS):
			if (not m.group(2)):
				o_dt=o_dt[:i+m.end(1)]+b"public "+o_dt[i+m.end(1):]
				i+=8
			elif (b"public" not in m.group(2) and b"private" not in m.group(2) and b"protected" not in m.group(2)):
				o_dt=o_dt[:i+m.start(2)]+b"public "+o_dt[i+m.start(2):]
				i+=8
		i+=m.end(0)
	f.write(b";".join(imp)+b";public class main extends PApplet{\n"+o_dt.replace(b"\r\n",b"\n")+s_func+b"}static public void main(String[] a){String[] b=new String[]{\"main\"};if(a!=null){b=concat(b,a);}PApplet.main(b);}\n}")
with open("build/mapping.txt","w") as f:
	for k,v in lm:
		f.write(f"{k} {v}\n")
if (subprocess.run(["javac","-encoding","utf8","-d","build","-classpath",(";" if os.name=="nt" else ":").join(lib),"build/main.java"]).returncode!=0):
	sys.exit(1)
with zipfile.ZipFile("build/main.jar","w") as zf:
	print("Writing: META-INF/MANIFEST.MF")
	zf.writestr("META-INF/MANIFEST.MF",b"Main-Class: main\n")
	for r,_,fl in os.walk("build"):
		for f in fl:
			if (f[-6:]==".class"):
				print(f"Writing: {os.path.join(r,f)[6:].replace(chr(92),'/')}")
				zf.write(os.path.join(r,f),os.path.join(r,f)[6:])
	for nm in lib:
		with zipfile.ZipFile(nm,"r") as jf:
			for k in jf.namelist():
				if (k.upper()!="META-INF/MANIFEST.MF"):
					dt=jf.read(k)
					if (len(k)>0):
						print(f"Writing: {k}")
						zf.writestr(k,dt)
if ("--run" in sys.argv):
	subprocess.run(["java","-Dfile.encoding=UTF8","-jar","build/main.jar"])
