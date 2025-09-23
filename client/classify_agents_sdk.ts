// client/classify_agents_sdk.ts
import { hostedMcpTool, ResponsesClient } from "@openai/agents";
import dotenv from "dotenv";
dotenv.config();

const client = new ResponsesClient({ apiKey: process.env.OPENAI_API_KEY! });

async function run() {
  const mcpTool = hostedMcpTool({
    serverUrl: process.env.MCP_SERVER_URL || "http://localhost:8080",
    label: "skos-taxonomy"
  });

  const res = await client.responses.create({
    model: "o4-mini",
    input: "Clasifica: leche descremada 1L sin lactosa",
    tools: [mcpTool],
    instructions:
      "Usa search_concepts y get_context para asignar un concepto SKOS y devuelve JSON con notation/prefLabel/confidence."
  });

  console.log(JSON.stringify(res.output, null, 2));
}

run().catch(console.error);
