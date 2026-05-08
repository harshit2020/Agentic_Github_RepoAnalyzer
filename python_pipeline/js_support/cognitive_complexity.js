import { ESLint } from "eslint";
import path from "path";

async function run() {
  const targetDir = path.resolve("../input_code");

  const eslint = new ESLint({
    cwd: targetDir,
    overrideConfigFile: path.resolve("./eslint.config.mjs"), 
    ignore: false,
  });

  const results = await eslint.lintFiles(["**/*.js"]);

  for (const file of results) {
    for (const msg of file.messages) {
      if (msg.ruleId === "sonarjs/cognitive-complexity") {
        console.log({
          file: file.filePath,
          line: msg.line,
          complexity: msg.message,
        });
      }
    }
  }
  console.log("Files analyzed:", results.length);
}

run();