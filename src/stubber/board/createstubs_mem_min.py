r='{}/{}'
q='method'
p='function'
o='bool'
n='str'
m='float'
l='int'
k=NameError
j=sorted
i=NotImplementedError
A=',\n'
a='dict'
Z='list'
Y='tuple'
X='micropython'
W=repr
U='_'
T=KeyError
S=open
R=dir
Q=True
P='family'
O=IndexError
N=ImportError
M='.'
L=len
K='board'
J=print
I=False
H=AttributeError
G='/'
F=None
E='version'
D=OSError
B=''
import gc as C,sys,uos as os
from ujson import dumps as b
try:from machine import reset
except N:pass
try:from collections import OrderedDict as c
except N:from ucollections import OrderedDict as c
__version__='v1.12.2'
s=2
t=2
class Stubber:
	def __init__(A,path=F,firmware_id=F):
		B=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise i('MicroPython 1.13.0 cannot be stubbed')
		except H:pass
		A._report=[];A.info=_info();C.collect()
		if B:A._fwid=B.lower()
		elif A.info[P]==X:A._fwid='{family}-{ver}-{port}-{board}'.format(**A.info)
		else:A._fwid='{family}-{ver}-{port}'.format(**A.info)
		A._start_free=C.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',G)
		try:d(path+G)
		except D:J('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.modules=[]
	def get_obj_attributes(L,item_instance):
		G=item_instance;A=[];J=[]
		for I in R(G):
			try:
				D=getattr(G,I)
				try:E=W(type(D)).split("'")[1]
				except O:E=B
				if E in{l,m,n,o,Y,Z,a}:F=1
				elif E in{p,q}:F=2
				elif E in'class':F=3
				else:F=4
				A.append((I,W(D),W(type(D)),D,F))
			except H as K:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(I,G,K))
		A=j([A for A in A if not A[0].startswith(U)],key=lambda x:x[4]);C.collect();return A,J
	def add_modules(A,modules):A.modules=j(set(A.modules)|set(modules))
	def create_all_stubs(A):
		C.collect()
		for B in A.modules:A.create_one_stub(B)
	def create_one_stub(A,module_name):
		B=module_name
		if B in A.problematic:return I
		if B in A.excluded:return I
		F='{}/{}.py'.format(A.path,B.replace(M,G));C.collect();E=I
		try:E=A.create_module_stub(B,F)
		except D:return I
		C.collect();return E
	def create_module_stub(H,module_name,file_name=F):
		E=file_name;A=module_name
		if C.mem_free()<8500:
			try:from machine import reset;reset()
			except N:pass
		if E is F:E=H.path+G+A.replace(M,U)+'.py'
		if G in A:A=A.replace(G,M)
		K=F
		try:K=__import__(A,F,F,'*');J('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(A,E,C.mem_free()))
		except N:return I
		d(E)
		with S(E,'w')as L:O='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(A,H._fwid,H.info,__version__);L.write(O);L.write('from typing import Any\n\n');H.write_object_stub(L,K,A,B)
		H._report.append('{{"module": "{}", "file": "{}"}}'.format(A,E.replace('\\',G)))
		if A not in{'os','sys','logging','gc'}:
			try:del K
			except (D,T):pass
			try:del sys.modules[A]
			except T:pass
		C.collect();return Q
	def write_object_stub(M,fp,object_expr,obj_name,indent,in_class=0):
		d='{0}{1} = {2} # type: {3}\n';c='bound_method';b='Any';Q=in_class;P=object_expr;O='Exception';H=fp;E=indent;C.collect()
		if P in M.problematic:return
		R,N=M.get_obj_attributes(P)
		if N:J(N)
		for (F,K,G,S,f) in R:
			if F in['classmethod','staticmethod','BaseException',O]:continue
			if G=="<class 'type'>"and L(E)<=t*4:
				U=B;V=F.endswith(O)or F.endswith('Error')or F in['KeyboardInterrupt','StopIteration','SystemExit']
				if V:U=O
				A='\n{}class {}({}):\n'.format(E,F,U)
				if V:A+=E+'    ...\n';H.write(A);return
				H.write(A);M.write_object_stub(H,S,'{0}.{1}'.format(obj_name,F),E+'    ',Q+1);A=E+'    def __init__(self, *argv, **kwargs) -> None:\n';A+=E+'        ...\n\n';H.write(A)
			elif q in G or p in G:
				W=b;X=B
				if Q>0:X='self, '
				if c in G or c in K:A='{}@classmethod\n'.format(E)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(E,F,W)
				else:A='{}def {}({}*args, **kwargs) -> {}:\n'.format(E,F,X,W)
				A+=E+'    ...\n\n';H.write(A)
			elif G=="<class 'module'>":0
			elif G.startswith("<class '"):
				I=G[8:-2];A=B
				if I in[n,l,m,o,'bytearray','bytes']:A=d.format(E,F,K,I)
				elif I in[a,Z,Y]:e={a:'{}',Z:'[]',Y:'()'};A=d.format(E,F,e[I],I)
				else:
					if I not in['object','set','frozenset']:I=b
					A='{0}{1} : {2} ## {3} = {4}\n'.format(E,F,I,G,K)
				H.write(A)
			else:H.write("# all other, type = '{0}'\n".format(G));H.write(E+F+' # type: Any\n')
		del R;del N
		try:del F,K,G,S
		except (D,T,k):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,U)
		return A
	def clean(B,path=F):
		if path is F:path=B.path
		J('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);C=os.listdir(path)
		except (D,H):return
		for E in C:
			A=r.format(path,E)
			try:os.remove(A)
			except D:
				try:B.clean(A);os.rmdir(A)
				except D:pass
	def report(A,filename='modules.json'):
		J('Created stubs for {} modules on board {}\nPath: {}'.format(L(A._report),A._fwid,A.path));F=r.format(A.path,filename);C.collect()
		try:
			with S(F,'w')as B:
				A.write_json_header(B);E=Q
				for G in A._report:A.write_json_node(B,G,E);E=I
				A.write_json_end(B)
			H=A._start_free-C.mem_free()
		except D:J('Failed to create the report.')
	def write_json_header(C,f):B='firmware';f.write('{');f.write(b({B:C.info})[1:-1]);f.write(A);f.write(b({'stubber':{E:__version__},'stubtype':B})[1:-1]);f.write(A);f.write('"modules" :[\n')
	def write_json_node(B,f,n,first):
		if not first:f.write(A)
		f.write(n)
	def write_json_end(A,f):f.write('\n]}')
def d(path):
	A=C=0
	while A!=-1:
		A=path.find(G,C)
		if A!=-1:
			B=path[0]if A==0 else path[:A]
			try:H=os.stat(B)
			except D as E:
				if E.args[0]==s:
					try:os.mkdir(B)
					except D as F:J('failed to create folder {}'.format(B));raise F
		C=A+1
def V(s):
	A=' on '
	if not s:return B
	if A in s:s=s.split(A,1)[0]
	return s.split('-')[1]if'-'in s else B
def _info():
	j='ev3-pybricks';i='pycom';h='pycopy';g='GENERIC';d='arch';b='cpu';a='ver';W='with';I='mpy';G='build';A=c({P:sys.implementation.name,E:B,G:B,a:B,'port':'stm32'if sys.platform.startswith('pyb')else sys.platform,K:g,b:B,I:B,d:B})
	try:A[E]=M.join([str(A)for A in sys.implementation.version])
	except H:pass
	try:Y=sys.implementation._machine if'_machine'in R(sys.implementation)else os.uname().machine;A[K]=Y.strip();A[b]=Y.split(W)[1].strip();A[I]=sys.implementation._mpy if'_mpy'in R(sys.implementation)else sys.implementation.mpy if I in R(sys.implementation)else B
	except (H,O):pass
	C.collect()
	try:
		for Q in ['board_info.csv','lib/board_info.csv']:
			if f(Q):
				J=A[K].strip()
				if e(A,J,Q):break
				if W in J:
					J=J.split(W)[0].strip()
					if e(A,J,Q):break
				A[K]=g
	except (H,O,D):pass
	A[K]=A[K].replace(' ',U);C.collect()
	try:
		A[G]=V(os.uname()[3])
		if not A[G]:A[G]=V(os.uname()[2])
		if not A[G]and';'in sys.version:A[G]=V(sys.version.split(';')[1])
	except (H,O):pass
	if A[G]and L(A[G])>5:A[G]=B
	if A[E]==B and sys.platform not in('unix','win32'):
		try:k=os.uname();A[E]=k.release
		except (O,H,TypeError):pass
	for (l,m,n) in [(h,h,'const'),(i,i,'FAT'),(j,'pybricks.hubs','EV3Brick')]:
		try:o=__import__(m,F,F,n);A[P]=l;del o;break
		except (N,T):pass
	if A[P]==j:A['release']='2.0.0'
	if A[P]==X:
		if A[E]and A[E].endswith('.0')and A[E]>='1.10.0'and A[E]<='1.20.0':A[E]=A[E][:-2]
	if I in A and A[I]:
		S=int(A[I]);Z=[F,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][S>>10]
		if Z:A[d]=Z
		A[I]='v{}.{}'.format(S&255,S>>8&3)
	A[a]=f"v{A[E]}-{A[G]}"if A[G]else f"v{A[E]}";return A
def e(info,board_descr,filename):
	with S(filename,'r')as B:
		while 1:
			A=B.readline()
			if not A:break
			C,D=A.split(',')[0].strip(),A.split(',')[1].strip()
			if C==board_descr:info[K]=D;return Q
	return I
def get_root():
	try:A=os.getcwd()
	except (D,H):A=M
	B=A
	for B in [A,'/sd','/flash',G,M]:
		try:C=os.stat(B);break
		except D:continue
	return B
def f(filename):
	try:os.stat(filename);return Q
	except D:return I
def g():sys.exit(1)
def read_path():
	path=B
	if L(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:g()
	elif L(sys.argv)==2:g()
	return path
def h():
	try:A=bytes('abc',encoding='utf8');B=h.__module__;return I
	except (i,H):return Q
def main():
	stubber=Stubber(path=read_path());stubber.clean();stubber.modules=[X]
	for A in [B,G,'/lib/']:
		try:
			with S(A+'modulelist'+'.txt')as E:stubber.modules=[A.strip()for A in E.read().split('\n')if L(A.strip())and A.strip()[0]!='#'];break
		except D:pass
	C.collect();stubber.create_all_stubs();stubber.report()
if __name__=='__main__'or h():
	try:logging.basicConfig(level=logging.INFO)
	except k:pass
	if not f('no_auto_stubber.txt'):main()