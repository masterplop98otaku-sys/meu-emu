import os, re, shutil, sys
root = sys.argv[1]
cldc = os.path.join(root, 'cldc')
# 1) os/wiiu = copia de la plantilla os/generic con el nombre cambiado
src = os.path.join(cldc, 'src', 'vm', 'os', 'generic')
dst = os.path.join(cldc, 'src', 'vm', 'os', 'wiiu')
shutil.rmtree(dst, ignore_errors=True); os.makedirs(dst)
for f in os.listdir(src):
    p = os.path.join(src, f)
    if not os.path.isfile(p) or f.endswith('.load'): continue
    data = open(p, encoding='utf8', errors='replace').read().replace('generic', 'wiiu').replace('Generic', 'Wii U')
    open(os.path.join(dst, f.replace('generic', 'wiiu')), 'w', encoding='utf8', newline='\n').write(data)
# formato de jlong en OsMisc (solo se usa en depuracion)
p = os.path.join(dst, 'OsMisc_wiiu.cpp'); t = open(p, encoding='utf8').read()
t = t.replace('return "";', 'return "%lld";', 1).replace('return "";', 'return "%llu";', 1)
open(p, 'w', encoding='utf8').write(t)
# 2) archivos propios encima
ov = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'overlay', 'cldc')
for d, _, fs in os.walk(ov):
    for f in fs:
        rel = os.path.relpath(os.path.join(d, f), ov)
        out = os.path.join(cldc, rel); os.makedirs(os.path.dirname(out), exist_ok=True)
        shutil.copyfile(os.path.join(d, f), out)
# 3) registrar el nuevo os_family en jvm.make
jm = os.path.join(cldc, 'build', 'share', 'jvm.make'); t = open(jm, encoding='utf8', errors='replace').read()
a = 'MakeDepsMain_linux    = UnixPlatform'; b = 'MakeDepsOpts_linux    = -resolveVpath true'
assert a in t and b in t, 'jvm.make cambio de formato'
t = t.replace(a, a + '\nMakeDepsMain_wiiu     = UnixPlatform', 1).replace(b, b + '\nMakeDepsOpts_wiiu     = -resolveVpath true', 1)
open(jm, 'w', encoding='utf8', newline='\n').write(t)
# 4) informacion para depurar
os.system(f'grep -n "GNU_TOOLS_DIR\\|CPP_gcc\\|CC_gcc\\|LINK_gcc" {jm} | head -30')
os.system(f'grep -rn "real_time_tick" {cldc}/src/vm | head -10')
print('overlay aplicado')
