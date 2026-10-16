#!/usr/bin/env node
// Parse every generated OpenCode TypeScript tool using the real TypeScript parser.
const fs = require("node:fs");
const path = require("node:path");
const ts = require("typescript");
const root = process.argv[2] || "build/opencode/.opencode/tools";
if (!fs.existsSync(root)) throw new Error("Missing OpenCode tools directory: " + root);
const files = fs.readdirSync(root).filter(n => n.endsWith(".ts")).sort();
if (!files.length) throw new Error("No generated OpenCode TypeScript files found");
let bad = 0;
for (const name of files) {
  const file = path.join(root, name);
  const src = fs.readFileSync(file, "utf8");
  const syntax = ts.createSourceFile(file, src, ts.ScriptTarget.Latest, true, ts.ScriptKind.TS);
  if (syntax.parseDiagnostics.length) {
    bad++;
    for (const d of syntax.parseDiagnostics) {
      const pos = syntax.getLineAndCharacterOfPosition(d.start || 0);
      console.error(name + ":" + (pos.line + 1) + ":" + (pos.character + 1) + " " +
        ts.flattenDiagnosticMessageText(d.messageText, "\n"));
    }
  }
}
if (bad) { console.error("Invalid TypeScript tools: " + bad); process.exit(1); }
console.log("TypeScript syntax OK: " + files.length + " OpenCode tools");
