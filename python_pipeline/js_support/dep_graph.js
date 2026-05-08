import madge from "madge";
import path from "path";

async function buildDependencyGraph(sourcePath, outputPath = "dependency_graph.png") {
  const result = await madge(sourcePath, {
    fileExtensions: ["js", "jsx", "ts", "tsx", "mjs", "cjs"],
    excludeRegExp: [/node_modules/, /\.test\./, /\.spec\./],
  });

  const out = path.resolve(outputPath);
  await result.image(out);
  console.log(`Graph saved → ${out}`);
  return out;
}

// Example usage

buildDependencyGraph("../input_code", "../my_graph.png");