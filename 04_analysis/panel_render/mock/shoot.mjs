// Drives headless Chrome over CDP: loads the mock panel, opens each tool and screenshots it.
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const out = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'screenshots');
fs.mkdirSync(out, { recursive: true });
const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'panel-chrome-'));
const chrome = spawn('google-chrome-stable', ['--headless=new','--no-sandbox','--disable-gpu','--hide-scrollbars',
  '--remote-debugging-port=9333','--window-size=1600,1000','--user-data-dir='+profile,'about:blank'],{stdio:'ignore'});
const sleep = ms => new Promise(r=>setTimeout(r,ms));
let tabs; for (let i=0;i<50;i++){ try{ tabs=await (await fetch('http://127.0.0.1:9333/json')).json(); if(tabs.length) break;}catch{} await sleep(200); }
const ws = new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);
await new Promise(r=>ws.onopen=r);
let id=0; const pend=new Map();
ws.onmessage=e=>{const m=JSON.parse(e.data); if(m.id&&pend.has(m.id)){pend.get(m.id)(m.result);pend.delete(m.id);}};
const cdp=(method,params={})=>new Promise(r=>{const i=++id;pend.set(i,r);ws.send(JSON.stringify({id:i,method,params}));});
const ev = expr => cdp('Runtime.evaluate',{expression:expr,awaitPromise:true});
await cdp('Page.enable');
const DESK = `(()=>{const a=document.getElementById('screen-area');let d=document.getElementById('mock-desk');
 if(!d){d=document.createElement('div');d.id='mock-desk';d.style.cssText='position:absolute;inset:0;background:linear-gradient(135deg,#1d3b6e,#5a2a7a);color:#fff;font:16px sans-serif;z-index:500';
 d.innerHTML='<div style="position:absolute;left:120px;top:100px;width:620px;height:360px;background:rgba(255,255,255,.92);color:#333;padding:12px">Example Window (mock desktop image)</div><div style="position:absolute;left:0;right:0;bottom:0;height:40px;background:rgba(20,20,20,.85);padding:10px;text-align:center">DEMO DESKTOP</div>';a.appendChild(d);}
 for(const [i,v] of [['fps-val','30'],['ms-val','42'],['bw-val','318']]){const e=document.getElementById(i);if(e)e.textContent=v;}
 const s=document.getElementById('conn-status');if(s){s.className='';s.innerHTML='<i class="fa-solid fa-circle" style="font-size:8px"></i> LIVE';}})()`;
const tools = [['00_main',null,null],['01_sysinfo','system','System Info'],['02_taskmgr','remote','Task Manager'],['03_files','remote','File Manager'],
 ['04_keylogger','remote','Keylogger'],['05_startup','system','Startup Manager'],['06_tcp','system','TCP Manager'],['07_ports','system','Listening Ports'],
 ['08_passwords','recovery','Passwords'],['09_discord_tokens','recovery','Discord Tokens'],['10_wifi','recovery','WiFi Passwords'],
 ['11_registry','system','Registry Editor'],['12_hidden_browsers','remote','Hidden Browsers'],['13_run_exe','misc','Run Exe'],['14_defender','misc','Defender'],
 ['15_menu_remote','remote',null],['16_menu_system','system',null],['17_menu_recovery','recovery',null],['18_menu_misc','misc',null],['19_menu_client','client',null]];
const shot = async name => { const r=await cdp('Page.captureScreenshot',{format:'png'}); fs.writeFileSync(path.join(out,name+'.png'),Buffer.from(r.data,'base64')); console.log('saved',name); };
for (const [name,menu,label] of tools) {
  await cdp('Page.navigate',{url:'http://127.0.0.1:8765/'}); await sleep(2500);
  if(name==='00_main') await ev(DESK);
  if (menu) {
    await ev(`document.querySelector('[data-tm-menu="${menu}"]').click()`); await sleep(300);
    if (label) { await ev(`[...document.querySelectorAll('#tm-menu-${menu} .tm-menu-item')].find(e=>e.textContent.includes(${JSON.stringify(label)})).click()`); await sleep(1500); }
  }
  await shot(name);
}
ws.close(); chrome.kill(); fs.rmSync(profile,{recursive:true,force:true});
