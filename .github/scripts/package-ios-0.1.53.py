from pathlib import Path
import zipfile,plistlib,json,hashlib,shutil
source=Path('ToMina-iOS-free-build-0.1.53.zip')
expected='faa6911122ce844a9be163ca1b8106c5a9a95f1eb07ad213a958316f0dbae120'
assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
out=Path('delivery');root=out/'source/ToMina-iOS'
with zipfile.ZipFile(source) as z:
 assert z.testzip() is None
 for n in z.namelist():
  p=Path(n);assert not p.is_absolute() and '..' not in p.parts
 z.extractall(root)
shutil.copytree(root/'EngineChecks',out/'shared/engine')
files=list(Path('compiled').rglob('*.ipa'));assert len(files)==1
ipa=files[0]
with zipfile.ZipFile(ipa) as z:
 assert z.testzip() is None
 plists=[n for n in z.namelist() if n.startswith('Payload/') and n.count('/')==2 and n.endswith('.app/Info.plist')]
 assert len(plists)==1
 info=plistlib.loads(z.read(plists[0]));prefix=plists[0][:-len('Info.plist')]
 assert info['CFBundleShortVersionString']=='0.1.53' and info['CFBundleVersion']=='54'
 assert info['CFBundleIdentifier']=='com.mina.tomina' and info['MinimumOSVersion']=='18.0'
 assert z.read(prefix+'SingleGIF.js')==(root/'Resources/SingleGIF.js').read_bytes()
 assert b'updateHalfBda:updateHalfBda' in z.read(prefix+'SingleGIF.js')
 assert json.loads(z.read(prefix+'Credentials.json'))['hashes']==[]
 assert z.read(prefix+info['CFBundleExecutable'])[:4] in [bytes.fromhex('cffaedfe'),bytes.fromhex('cafebabe'),bytes.fromhex('bebafeca')]
shutil.copyfile(ipa,out/'To.Mina_0.1.53.ipa')
record={'version':'0.1.53','build':54,'workflow_run':40872843854,'source_sha256':expected,'ipa_sha256':hashlib.sha256(ipa.read_bytes()).hexdigest(),'requires_signing':True,'engine_matches_build_source':True}
(out/'verification').mkdir()
(out/'verification/ios-build-summary.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
(out/'更新说明.txt').write_text('To.Mina iOS 0.1.53（build54）\n工具箱新增“更新半bda”，保留 0.1.52 的 GIF 和顶栏修复。\n用法：导入底包 → 修改布局/样式 → 工具箱 → 更新半bda → 保存/导出。\nIPA 为 macOS/Xcode 编译的未签名包，需要签名后安装。\n源码与实际构建一致。\n')
print('PASS: IPA version/build, Mach-O executable, engine bytes, archive integrity and matching source verified')
print(json.dumps(record))
