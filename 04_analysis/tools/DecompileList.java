// Static: label all recovered Go names, then disassemble + decompile a worklist. No auto-analysis, nothing executed.
//@category Triage
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.symbol.*;
import java.io.*;
import java.util.*;
import java.nio.charset.StandardCharsets;

public class DecompileList extends GhidraScript {
  String clean(String n){ String s=n.replaceAll("[^A-Za-z0-9_.:*()\\[\\]-]","_"); return s.length()>200?s.substring(0,200):s; }
  public void run() throws Exception {
    String[] a = getScriptArgs();
    File names = new File(a[0]), work = new File(a[1]), out = new File(a[2]);
    out.mkdirs();
    SymbolTable st = currentProgram.getSymbolTable();
    AddressSpace sp = currentProgram.getAddressFactory().getDefaultAddressSpace();
    int labeled=0;
    try (BufferedReader r = new BufferedReader(new InputStreamReader(new FileInputStream(names), StandardCharsets.UTF_8))) {
      String l; while ((l = r.readLine()) != null) {
        String[] p = l.split("\t", 2); if (p.length < 2 || p[1].equals("-")) continue;
        try { st.createLabel(sp.getAddress(p[0]), clean(p[1]), SourceType.IMPORTED); labeled++; } catch (Exception e) {}
      }
    }
    List<String[]> items = new ArrayList<>();
    try (BufferedReader r = new BufferedReader(new InputStreamReader(new FileInputStream(work), StandardCharsets.UTF_8))) {
      String l; while ((l = r.readLine()) != null) items.add(l.split("\t", 3));
    }
    // create functions first so calls resolve
    for (String[] it : items) {
      Address ad = sp.getAddress(it[0]);
      new DisassembleCommand(ad, null, true).applyTo(currentProgram, monitor);
      if (getFunctionAt(ad) == null) {
        String nm = it[1].equals("-") ? null : clean(it[1]);
        try { createFunction(ad, nm); } catch (Exception e) {}
      }
    }
    DecompInterface di = new DecompInterface(); di.openProgram(currentProgram);
    PrintWriter idx = new PrintWriter(new OutputStreamWriter(new FileOutputStream(new File(out, "INDEX.tsv")), StandardCharsets.UTF_8));
    idx.println("address\tname\twhy_selected\tfile\tstatus");
    int ok=0, n=0;
    for (String[] it : items) {
      if (monitor.isCancelled()) break;
      Address ad = sp.getAddress(it[0]); Function fn = getFunctionAt(ad); n++;
      String base = it[0] + "_" + (it[1].equals("-") ? "unnamed" : clean(it[1]).replaceAll("[*():\\[\\]]", "_"));
      if (base.length() > 120) base = base.substring(0, 120);
      String fname = base + ".c.txt", status;
      String code;
      if (fn == null) { code = "/* could not create function */"; status = "no_function"; }
      else {
        DecompileResults res = di.decompileFunction(fn, 60, monitor);
        if (res != null && res.decompileCompleted()) { code = res.getDecompiledFunction().getC(); status = "ok"; ok++; }
        else { code = "/* decompile failed: " + (res == null ? "null" : res.getErrorMessage()) + " */"; status = "failed"; }
      }
      try (PrintWriter w = new PrintWriter(new OutputStreamWriter(new FileOutputStream(new File(out, fname)), StandardCharsets.UTF_8))) {
        w.println("// " + it[1] + " @ " + it[0]);
        w.println("// selected because: " + it[2]);
        w.println("// Ghidra 12.2 pseudocode of an image rebuilt from charmap.DMP. Static only; never executed. Not original source.");
        w.println(code);
      }
      idx.println(it[0] + "\t" + it[1] + "\t" + it[2] + "\t" + fname + "\t" + status);
      if (n % 50 == 0) { idx.flush(); println("progress " + n + "/" + items.size()); }
    }
    idx.close(); di.dispose();
    println("labeled=" + labeled + " decompiled_ok=" + ok + " of " + items.size());
  }
}
