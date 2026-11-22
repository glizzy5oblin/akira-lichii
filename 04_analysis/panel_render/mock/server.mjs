// Mock backend for the carved "Akira Remote" panel. Serves the carved HTML/JS/CSS and answers
// every /api/* route with FAKE, clearly-labelled data. No real data, no outbound connections,
// no WebSockets, binds to 127.0.0.1 only.
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const here = path.dirname(fileURLToPath(import.meta.url));
const src = path.join(here, '..', '..', 'panel_source');
const read = f => fs.readFileSync(path.join(src, f), 'utf8');
const HOST = 'DESKTOP-DEMO01';

const procs = [['System',4,'0.1%','0.1 MB'],['explorer.exe',4120,'1.2%','142 MB'],['chrome.exe',6012,'8.4%','612 MB'],
 ['Code.exe',7344,'3.1%','388 MB'],['svchost.exe',1088,'0.0%','21 MB'],['lsass.exe',784,'0.0%','14 MB'],
 ['MsMpEng.exe',2640,'2.2%','231 MB'],['charmap.exe',9120,'0.6%','47 MB'],['calc.exe',9388,'0.1%','28 MB'],
 ['powershell.exe',8820,'0.3%','63 MB'],['WindowsTerminal.exe',5560,'0.2%','74 MB'],['notepad.exe',3120,'0.0%','9 MB']]
 .map(([name,pid,cpu,memory])=>({name,pid,cpu,memory}));
const dirs = n => n.map(name=>({name,isDir:true,path:'C:\\Users\\demo\\'+name,size:0,modified:'2026-11-18 14:02'}));
const files = [...dirs(['Desktop','Documents','Downloads','Pictures','Music','Videos']),
  {name:'notes.txt',size:2310,isDir:false,modified:'2026-11-20 09:12',path:'C:\\Users\\demo\\notes.txt'},
  {name:'report-FAKE.docx',size:48211,isDir:false,modified:'2026-11-19 17:40',path:'C:\\Users\\demo\\report-FAKE.docx'},
  {name:'setup.exe',size:5311200,isDir:false,modified:'2026-11-17 11:05',path:'C:\\Users\\demo\\setup.exe'}];
const J = {
 '/api/sysinfo': {computer_name:HOST,user_name:'demo',account_type:'Administrator',os:'Windows 11 Pro',os_build:'26100',
   cpu:'Demo CPU @ 3.40GHz',ram:'16 GB',gpu:'Demo GPU 8GB',local_ip:'10.0.0.5',public_ip:'203.0.113.7',country:'Exampleland',
   country_code:'XX',city:'Example City',region:'Example Region',isp:'Example ISP',mac:'<MAC>',
   hwid:'FAKE-0000-DEMO',antivirus:'Windows Defender',disks:'C: 512 GB (212 GB free)'},
 '/api/monitors': [{index:0,name:'Display 1',width:1920,height:1080,primary:true}],
 '/api/procs': procs,
 '/api/files': files,
 '/api/files/special': ['Desktop','Downloads','Documents','Pictures','Videos','Music'].map(n=>({name:n,path:'C:\\Users\\demo\\'+n})),
 '/api/startup': [{name:'OneDrive',command:'"C:\\Program Files\\OneDrive\\OneDrive.exe" /background',source:'HKCU\\Run'},
   {name:'SecurityHealth',command:'C:\\Windows\\System32\\SecurityHealthSystray.exe',source:'HKLM\\Run'},
   {name:'Updater (demo)',command:'C:\\Users\\demo\\AppData\\Roaming\\demo\\updater.exe',source:'HKCU\\Run'}],
 '/api/tcp': [['chrome.exe','10.0.0.5',51822,'198.51.100.20',443,'ESTABLISHED'],['svchost.exe','0.0.0.0',135,'0.0.0.0',0,'LISTEN'],
   ['calc.exe','10.0.0.5',51900,'198.51.100.44',7844,'ESTABLISHED'],['Code.exe','10.0.0.5',52011,'192.0.2.9',443,'TIME_WAIT']]
   .map(([process,local_addr,local_port,remote_addr,remote_port,state])=>({process,local_addr,local_port,remote_addr,remote_port,state})),
 '/api/ports': [['svchost.exe','TCP','0.0.0.0',135],['System','TCP','0.0.0.0',445],['chrome.exe','UDP','0.0.0.0',5353]].map(([process,proto,addr,port])=>({process,proto,addr,port})),
 '/api/recovery/passwords': {passwords:[
   {browser:'Chrome',url:'https://example.test/login',user:'user1@example.test',pass:'FAKE-pass-1'},
   {browser:'Edge',url:'https://shop.example.test',user:'demo.user',pass:'FAKE-pass-2'},
   {browser:'Firefox',url:'https://mail.example.test',user:'user2@example.test',pass:'FAKE-pass-3'}]},
 '/api/recovery/tokens': {tokens:[{username:'DemoUser',user_id:'000000000000000000',source:'Discord',location:'LevelDB',
   email:'demo@example.test',mfa_enabled:true,nitro:'Nitro Basic',billing:'None',token:'FAKE.TOKEN.NOT-REAL'}]},
 '/api/recovery/wifi': {networks:[{ssid:'DemoWiFi',password:'FAKE-wifi-pass',auth:'WPA2'}]},
 '/api/keys': [['09:41:02','Chrome - Example',"h"],['09:41:02','Chrome - Example','i'],['09:41:03','Chrome - Example','Enter']]
   .map(([t,a,c])=>({t,a,k:c.length>1?c:c.toUpperCase(),c:c.length>1?'':c})),
 '/api/clipboard/history': [{t:'09:40:11',text:'example text copied (demo)'}],
 '/api/miner/status': {}, '/api/socks5/status': {running:false}, '/api/defender/status': {enabled:true},
 '/api/firewall/status': {enabled:true}, '/api/rdp': {enabled:false}, '/api/users': [{name:'demo',admin:true,enabled:true}],
 '/api/sessions': [{id:1,user:'demo',state:'Active',type:'console'}],
};
const mime = {'.css':'text/css','.js':'text/javascript','.html':'text/html'};
http.createServer((req,res)=>{
  const u = new URL(req.url,'http://x'), p = u.pathname;
  const send=(b,t='application/json')=>{res.writeHead(200,{'content-type':t});res.end(typeof b==='string'?b:JSON.stringify(b));};
  if (p==='/'||p==='/index.html') return send(read('main_panel.html.txt').replaceAll('{{USER_HOST}}',HOST),'text/html');
  if (p==='/theme.css') return send(read('extra_01_1106c4e.txt'),'text/css');
  if (p==='/viewer.js') return send(read('app.js.txt'),'text/javascript');
  if (p==='/viewer.css') return send(read('theme.css.txt'),'text/css');
  if (p.startsWith('/api/')) {
    if (p==='/api/files' && u.searchParams.get('path')==='') return send([{name:'C:',path:'C:\\',isDir:true},{name:'D:',path:'D:\\',isDir:true}]);
    return send(J[p] ?? (req.method==='GET' ? {} : {ok:true}));
  }
  res.writeHead(404); res.end();
}).listen(8765,'127.0.0.1',()=>console.log('mock panel on http://127.0.0.1:8765'));
