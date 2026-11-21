// Static triage: find functions referencing malware-specific strings, decompile them and their unnamed callees.
//@category Triage
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.mem.*;
import ghidra.program.model.symbol.*;
import java.io.*;
import java.util.*;
import java.nio.charset.StandardCharsets;

public class TriageDecompile extends GhidraScript {
  static final String[] SEEDS = {
    "well-known/pki-validation","/boing","akgo.php","err.php","abe.a","qoing","qperl",
    "eth_call","0x6d4ce63c","0xF97CB22B","bsc-dataseed","wd.pid","t_id.txt","Fonts",
    "Login Data","Local State","Cookies","Local Storage","leveldb","Web Data","exodus","Exodus","metamask","Wallets","Coinomi",
    "discord","Discord","Telegram","api.telegram","sendDocument","tdata","Steam","ssfn",
    "/api/","viewer.html","theme.css","Akira","USER_HOST","socks5","miner","monero","pearl","xmrig","stratum",
    "CreateDesktop","hidden desktop","keylog","KeyLog","screenshot","webcam","clipboard",
    "schtasks","Add-MpPreference","Exclusion","netsh","powershell","cmd.exe","reg add","CurrentVersion\\Run",
    "trycloudflare","cloudflared","49912","localhost:","127.0.0.1","User-Agent","Mozilla/5.0","machineguid","MachineGuid",
    "wifi","netsh wlan","autofill","credit","history","Recent","passwords","v10","v20","DPAPI","CryptUnprotectData",
    "app_bound","elevation_service","IElevator","chrome.exe","msedge.exe","brave.exe","--remote-debugging","headless"
  };
  public void run() throws Exception {
    String[] args = getScriptArgs();
    File out = new File(args[0]); out.mkdirs();
    int maxFuncs = args.length > 1 ? Integer.parseInt(args[1]) : 700;
    Memory mem = currentProgram.getMemory();
    FunctionManager fm = currentProgram.getFunctionManager();
    ReferenceManager rm = currentProgram.getReferenceManager();
    LinkedHashMap<Function, TreeSet<String>> why = new LinkedHashMap<>();
    PrintWriter idx = new PrintWriter(new OutputStreamWriter(new FileOutputStream(new File(out, "INDEX.txt")), StandardCharsets.UTF_8));
    idx.println("# Static Ghidra triage of charmap (Go RAT). Program was never executed.");
    idx.println("# Functions: " + fm.getFunctionCount());
    for (String s : SEEDS) {
      byte[] b = s.getBytes(StandardCharsets.UTF_8);
      Address a = mem.getMinAddress(); int hits = 0, refd = 0;
      while (hits < 400 && !monitor.isCancelled()) {
        Address f = mem.findBytes(a, b, null, true, monitor);
        if (f == null) break;
        hits++;
        // exact-start reference, else nearest preceding referenced address within 256 bytes (Go literals are packed)
        Address hit = null;
        for (int back = 0; back <= 256; back++) {
          Address c; try { c = f.subtract(back); } catch (Exception e) { break; }
          if (rm.hasReferencesTo(c)) { hit = c; break; }
        }
        if (hit != null) {
          for (Reference r : rm.getReferencesTo(hit)) {
            Function fn = fm.getFunctionContaining(r.getFromAddress());
            if (fn != null) { why.computeIfAbsent(fn, k -> new TreeSet<>()).add(s + (hit.equals(f) ? "" : " (approx)")); refd++; }
          }
        }
        a = f.add(1);
      }
      idx.println("seed\t" + s + "\tbyte_hits=" + hits + "\tcode_refs=" + refd);
    }
    // add unnamed callees one level deep (likely author code)
    LinkedHashMap<Function, TreeSet<String>> all = new LinkedHashMap<>(why);
    for (Function fn : new ArrayList<>(why.keySet())) {
      for (Function c : fn.getCalledFunctions(monitor)) {
        String n = c.getName();
        if (c.isThunk() || c.isExternal()) continue;
        if (n.startsWith("FUN_") || n.isEmpty() || n.startsWith("main.") || !n.contains(".") ) {
          all.computeIfAbsent(c, k -> new TreeSet<>()).add("callee of " + fn.getEntryPoint());
        }
      }
    }
    DecompInterface di = new DecompInterface();
    di.toggleCCode(true); di.toggleSyntaxTree(false);
    di.openProgram(currentProgram);
    int n = 0;
    for (Map.Entry<Function, TreeSet<String>> e : all.entrySet()) {
      if (n >= maxFuncs || monitor.isCancelled()) break;
      Function fn = e.getKey();
      String safe = fn.getName().replaceAll("[^A-Za-z0-9_.-]", "_");
      if (safe.length() > 80) safe = safe.substring(0, 80);
      String fname = fn.getEntryPoint().toString() + "_" + safe + ".c.txt";
      DecompileResults res = di.decompileFunction(fn, 90, monitor);
      String code = (res != null && res.decompileCompleted()) ? res.getDecompiledFunction().getC() : ("/* decompile failed: " + (res == null ? "null" : res.getErrorMessage()) + " */");
      try (PrintWriter w = new PrintWriter(new OutputStreamWriter(new FileOutputStream(new File(out, fname)), StandardCharsets.UTF_8))) {
        w.println("// " + fn.getName() + " @ " + fn.getEntryPoint() + "  size=" + fn.getBody().getNumAddresses());
        w.println("// why: " + String.join("; ", e.getValue()));
        w.println("// Ghidra pseudocode from a static image rebuilt from memory; not original source.");
        w.println(code);
      }
      idx.println("func\t" + fn.getEntryPoint() + "\t" + fn.getName() + "\t" + String.join("; ", e.getValue()) + "\t" + fname);
      n++;
    }
    idx.println("# decompiled " + n + " of " + all.size() + " selected functions");
    idx.close();
    di.dispose();
  }
}
