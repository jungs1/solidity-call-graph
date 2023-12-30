import fs from "fs";
import { CHA } from "./call-graph-cha.js";
import { RTA } from "./call-graph-rta.js";

function main() {
  const ast = JSON.parse(fs.readFileSync("ast/example.sol_json.ast", "utf8"));
  const cha = new CHA();
  const chaAnalysisResult = cha.analyze(ast);
  console.log("CHA analysis result:", chaAnalysisResult);
  const rta = new RTA(cha);
  const rtaAnalysisResult = rta.analyze(ast);
  console.log("RTA analysis result:", rtaAnalysisResult);
}

main();
