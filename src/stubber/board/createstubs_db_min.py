v='{}/{}'
u='method'
t='function'
s='bool'
r='str'
q='float'
p='int'
o='port'
n=NameError
m=sorted
l=MemoryError
k=NotImplementedError
b=',\n'
a='dict'
Z='list'
Y='tuple'
X='micropython'
W=str
V=repr
T='_'
S=KeyError
R=IndexError
Q=dir
P=ImportError
O='family'
N=True
M='.'
L=len
K='board'
J=open
I=print
H=AttributeError
G='/'
F=False
E=None
D='version'
A=OSError
C=''
import gc as B,os,sys
from ujson import dumps as c
try:from machine import reset
except P:pass
try:from collections import OrderedDict as d
except P:from ucollections import OrderedDict as d
__version__='v1.14.1'
w=2
x=2
e=[M,'/lib','/sd/lib','/flash/lib','lib']
from time import sleep
class Stubber:
	def __init__(C,path=E,firmware_id=E):
		D=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise k('MicroPython 1.13.0 cannot be stubbed')
		except H:pass
		C._report=[];C.info=_info();I('Port: {}'.format(C.info[o]));I('Board: {}'.format(C.info[K]));B.collect()
		if D:C._fwid=D.lower()
		elif C.info[O]==X:C._fwid='{family}-{ver}-{port}-{board}'.format(**C.info)
		else:C._fwid='{family}-{ver}-{port}'.format(**C.info)
		C._start_free=B.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		C.path='{}/stubs/{}'.format(path,C.flat_fwid).replace('//',G)
		try:f(path+G)
		except A:I('error creating stub folder {}'.format(path))
		C.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];C.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];C.modules=[]
	def get_obj_attributes(L,item_instance):
		I=item_instance;D=[];J=[]
		for A in Q(I):
			if A.startswith(T)and not A in L.modules:continue
			try:
				E=getattr(I,A)
				try:F=V(type(E)).split("'")[1]
				except R:F=C
				if F in{p,q,r,s,Y,Z,a}:G=1
				elif F in{t,u}:G=2
				elif F in'class':G=3
				else:G=4
				D.append((A,V(E),V(type(E)),E,G))
			except H as K:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(A,I,K))
			except l as K:sleep(1);reset()
		D=m([A for A in D if not A[0].startswith('__')],key=lambda x:x[4]);B.collect();return D,J
	def add_modules(A,modules):A.modules=m(set(A.modules)|set(modules))
	def create_all_stubs(A):
		B.collect()
		for C in A.modules:A.create_one_stub(C)
	def create_one_stub(C,module_name):
		D=module_name
		if D in C.problematic:return F
		if D in C.excluded:return F
		H='{}/{}.py'.format(C.path,D.replace(M,G));B.collect();E=F
		try:E=C.create_module_stub(D,H)
		except A:return F
		B.collect();return E
	def create_module_stub(K,module_name,file_name=E):
		H=file_name;D=module_name
		if H is E:L=D.replace(M,T)+'.py';H=K.path+G+L
		else:L=H.split(G)[-1]
		if G in D:D=D.replace(G,M)
		O=E
		try:O=__import__(D,E,E,'*');R=B.mem_free();I('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(D,L,R))
		except P:return F
		f(H)
		with J(H,'w')as Q:U=W(K.info).replace('OrderedDict(',C).replace('})','}');V='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(D,K._fwid,U,__version__);Q.write(V);Q.write('from typing import Any\nfrom _typeshed import Incomplete\n\n');K.write_object_stub(Q,O,D,C)
		K._report.append('{{"module": "{}", "file": "{}"}}'.format(D,H.replace('\\',G)))
		if D not in{'os','sys','logging','gc'}:
			try:del O
			except (A,S):pass
			try:del sys.modules[D]
			except S:pass
		B.collect();return N
	def write_object_stub(M,fp,object_expr,obj_name,indent,in_class=0):
		d='{0}{1} = {2} # type: {3}\n';c='bound_method';b='Incomplete';Q=in_class;P=object_expr;O='Exception';H=fp;E=indent;B.collect()
		if P in M.problematic:return
		R,N=M.get_obj_attributes(P)
		if N:I(N)
		for (F,K,G,T,f) in R:
			if F in['classmethod','staticmethod','BaseException',O]:continue
			if F[0].isdigit():continue
			if G=="<class 'type'>"and L(E)<=x*4:
				U=C;V=F.endswith(O)or F.endswith('Error')or F in['KeyboardInterrupt','StopIteration','SystemExit']
				if V:U=O
				D='\n{}class {}({}):\n'.format(E,F,U)
				if V:D+=E+'    ...\n';H.write(D);return
				H.write(D);M.write_object_stub(H,T,'{0}.{1}'.format(obj_name,F),E+'    ',Q+1);D=E+'    def __init__(self, *argv, **kwargs) -> None:\n';D+=E+'        ...\n\n';H.write(D)
			elif any((A in G for A in[u,t,'closure'])):
				W=b;X=C
				if Q>0:X='self, '
				if c in G or c in K:D='{}@classmethod\n'.format(E)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(E,F,W)
				else:D='{}def {}({}*args, **kwargs) -> {}:\n'.format(E,F,X,W)
				D+=E+'    ...\n\n';H.write(D)
			elif G=="<class 'module'>":0
			elif G.startswith("<class '"):
				J=G[8:-2];D=C
				if J in[r,p,q,s,'bytearray','bytes']:D=d.format(E,F,K,J)
				elif J in[a,Z,Y]:e={a:'{}',Z:'[]',Y:'()'};D=d.format(E,F,e[J],J)
				else:
					if J not in['object','set','frozenset']:J=b
					D='{0}{1} : {2} ## {3} = {4}\n'.format(E,F,J,G,K)
				H.write(D)
			else:H.write("# all other, type = '{0}'\n".format(G));H.write(E+F+' # type: Incomplete\n')
		del R;del N
		try:del F,K,G,T
		except (A,S,n):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,T)
		return A
	def clean(C,path=E):
		if path is E:path=C.path
		I('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);D=os.listdir(path)
		except (A,H):return
		for F in D:
			B=v.format(path,F)
			try:os.remove(B)
			except A:
				try:C.clean(B);os.rmdir(B)
				except A:pass
	def report(C,filename='modules.json'):
		I('Created stubs for {} modules on board {}\nPath: {}'.format(L(C._report),C._fwid,C.path));G=v.format(C.path,filename);B.collect()
		try:
			with J(G,'w')as D:
				C.write_json_header(D);E=N
				for H in C._report:C.write_json_node(D,H,E);E=F
				C.write_json_end(D)
			K=C._start_free-B.mem_free()
		except A:I('Failed to create the report.')
	def write_json_header(B,f):A='firmware';f.write('{');f.write(c({A:B.info})[1:-1]);f.write(b);f.write(c({'stubber':{D:__version__},'stubtype':A})[1:-1]);f.write(b);f.write('"modules" :[\n')
	def write_json_node(A,f,n,first):
		if not first:f.write(b)
		f.write(n)
	def write_json_end(A,f):f.write('\n]}')
def f(path):
	B=D=0
	while B!=-1:
		B=path.find(G,D)
		if B!=-1:
			C=path[0]if B==0 else path[:B]
			try:H=os.stat(C)
			except A as E:
				if E.args[0]==w:
					try:os.mkdir(C)
					except A as F:I('failed to create folder {}'.format(C));raise F
		D=B+1
def U(s):
	A=' on '
	if not s:return C
	if A in s:s=s.split(A,1)[0]
	return s.split('-')[1]if'-'in s else C
def _info():
	k='ev3-pybricks';j='pycom';i='pycopy';f='GENERIC';c='arch';b='cpu';a='ver';V='with';G='mpy';F='build';A=d({O:sys.implementation.name,D:C,F:C,a:C,o:'stm32'if sys.platform.startswith('pyb')else sys.platform,K:f,b:C,G:C,c:C})
	try:A[D]=M.join([W(A)for A in sys.implementation.version])
	except H:pass
	try:Y=sys.implementation._machine if'_machine'in Q(sys.implementation)else os.uname().machine;A[K]=Y.strip();A[b]=Y.split(V)[1].strip();A[G]=sys.implementation._mpy if'_mpy'in Q(sys.implementation)else sys.implementation.mpy if G in Q(sys.implementation)else C
	except (H,R):pass
	B.collect()
	for J in [A+'/board_info.csv'for A in e]:
		if h(J):
			I=A[K].strip()
			if g(A,I,J):break
			if V in I:
				I=I.split(V)[0].strip()
				if g(A,I,J):break
			A[K]=f
	A[K]=A[K].replace(' ',T);B.collect()
	try:
		A[F]=U(os.uname()[3])
		if not A[F]:A[F]=U(os.uname()[2])
		if not A[F]and';'in sys.version:A[F]=U(sys.version.split(';')[1])
	except (H,R):pass
	if A[F]and L(A[F])>5:A[F]=C
	if A[D]==C and sys.platform not in('unix','win32'):
		try:l=os.uname();A[D]=l.release
		except (R,H,TypeError):pass
	for (m,n,p) in [(i,i,'const'),(j,j,'FAT'),(k,'pybricks.hubs','EV3Brick')]:
		try:q=__import__(n,E,E,p);A[O]=m;del q;break
		except (P,S):pass
	if A[O]==k:A['release']='2.0.0'
	if A[O]==X:
		if A[D]and A[D].endswith('.0')and A[D]>='1.10.0'and A[D]<='1.19.9':A[D]=A[D][:-2]
	if G in A and A[G]:
		N=int(A[G]);Z=[E,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][N>>10]
		if Z:A[c]=Z
		A[G]='v{}.{}'.format(N&255,N>>8&3)
	A[a]=f"v{A[D]}-{A[F]}"if A[F]else f"v{A[D]}";return A
def g(info,board_descr,filename):
	with J(filename,'r')as B:
		while 1:
			A=B.readline()
			if not A:break
			C,D=A.split(',')[0].strip(),A.split(',')[1].strip()
			if C==board_descr:info[K]=D;return N
	return F
def get_root():
	try:B=os.getcwd()
	except (A,H):B=M
	C=B
	for C in [B,'/sd','/flash',G,M]:
		try:D=os.stat(C);break
		except A:continue
	return C
def h(filename):
	try:
		if os.stat(filename)[0]>>14:return N
		return F
	except A:return F
def i():sys.exit(1)
def read_path():
	path=C
	if L(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:i()
	elif L(sys.argv)==2:i()
	return path
def j():
	try:A=bytes('abc',encoding='utf8');B=j.__module__;return F
	except (k,H):return N
def main():
	K='failed';G='modulelist.done';import machine as O
	try:C=J(G,'r+b');M=N
	except A:C=J(G,'w+b');M=F
	stubber=Stubber(path=read_path())
	if not M:stubber.clean()
	y(stubber);D={}
	try:
		with J(G)as C:
			for E in C.read().split('\n'):
				E=E.strip();B.collect()
				if L(E)>0:P,Q=E.split('=',1);D[P]=Q
	except (A,SyntaxError):pass
	B.collect();R=[A for A in stubber.modules if A not in D.keys()];B.collect()
	for H in R:
		I=F
		try:I=stubber.create_one_stub(H)
		except l:O.reset()
		B.collect();D[H]=W(stubber._report[-1]if I else K)
		with J(G,'a')as C:C.write('{}={}\n'.format(H,'ok'if I else K))
	if D:stubber._report=[A for(B,A)in D.items()if A!=K];stubber.report()
def y(stubber):
	stubber.modules=[]
	for D in e:
		try:
			with J(D+'/modulelist.txt')as E:
				for C in E.read().split('\n'):
					C=C.strip()
					if L(C)>0 and C[0]!='#':stubber.modules.append(C)
				B.collect();break
		except A:pass
	if not stubber.modules:stubber.modules=[X];_log.warn('Could not find modulelist.txt, using default modules')
	B.collect()
if __name__=='__main__'or j():
	try:logging.basicConfig(level=logging.INFO)
	except n:pass
	if not h('no_auto_stubber.txt'):
		try:B.threshold(4*1024);B.enable()
		except BaseException:pass
		main()