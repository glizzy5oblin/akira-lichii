import re,sys,collections
pats={
 'discord_token':r'\b[MNO][A-Za-z\d_-]{23,27}\.[A-Za-z\d_-]{6}\.[A-Za-z\d_-]{27,40}\b',
 'discord_enc_token':r'dQw4w9WgXcQ:[A-Za-z0-9+/=]{20,}',
 'github_token':r'\bgh[pousr]_[A-Za-z0-9]{30,}\b',
 '<AI-VENDOR>_key':r'\bsk-ant-[A-Za-z0-9_-]{20,}',
 'openai_key':r'\bsk-(?:proj-)?[A-Za-z0-9_-]{30,}',
 'google_api_key':r'\bAIza[0-9A-Za-z_-]{35}\b',
 'aws_key':r'\bAKIA[0-9A-Z]{16}\b',
 'slack_token':r'\bxox[abpr]-[A-Za-z0-9-]{10,}',
 'jwt':r'\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}',
 'telegram_bot':r'\b\d{8,10}:AA[A-Za-z0-9_-]{33}\b',
 'chrome_v10_v20_blob':r'\bv(?:10|20)[A-Za-z0-9+/]{20,}',
 'encrypted_key_json':r'"(?:app_bound_)?encrypted_key"\s*:\s*"[^"]{8,}',
 'tailscale_key':r'\btskey-[A-Za-z0-9-]{10,}',
 'ssh_private':r'BEGIN (?:OPENSSH|RSA|EC) PRIVATE KEY',
 'email':r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.(?:com|net|org|io|dev|me|co)\b',
 'cookie_header':r'(?i)\bcookie:\s*[^\r\n]{10,}',
 'set_cookie':r'(?i)\bset-cookie:\s*[^\r\n]{5,}',
 'password_field':r'(?i)"(?:password|passwd|pass|pwd)"\s*:\s*"[^"]{1,}"',
 'url_user_pass':r'(?i)"(?:origin_url|url|action_url)"\s*:\s*"https?://[^"]+"\s*,\s*"(?:username|user|login)"',
 'seed_like':r'\b(?:[a-z]{3,8} ){11}[a-z]{3,8}\b',
}
data=open(sys.argv[1],'r',errors='replace').read()
for name,p in pats.items():
    ms=re.findall(p,data)
    c=collections.Counter(ms)
    print(f'{name}: {len(ms)} hits, {len(c)} unique')
    for m,n in c.most_common(8):
        m=m if isinstance(m,str) else m[0]
        shown = m if name in ('ssh_private',) else (m[:14]+'…[masked '+str(len(m))+' chars]')
        if name=='email': 
            u,d=m.split('@',1); shown=u[:2]+'***@'+d
        if name=='seed_like': shown=' '.join(m.split()[:3])+' …'
        print('   ',n,'x',shown)
