import { Action } from "@copilotkit/shared";
import { researchWithLangGraph } from "./research";

import { NextRequest } from "next/server";
import {
  CopilotRuntime,
  LangChainAdapter,
  copilotRuntimeNextJSAppRouterEndpoint,
} from "@copilotkit/runtime";
import { ChatOpenAI } from "@langchain/openai";
import OpenAI from "openai";

const researchAction: Action<any> = {
  name: "research",
  description:
    "Call this function to conduct research on a certain topic. Respect other notes about when to call this function",
  parameters: [
    {
      name: "topic",
      type: "string",
      description: "The topic to research. 5 characters or longer.",
    },
  ],
  handler: async ({ topic }) => {
    console.log("Researching topic: ", topic);
    return await researchWithLangGraph(topic);
  },
};

const actions: Action<any>[] = [];
if (process.env["TAVILY_API_KEY"] && process.env["TAVILY_API_KEY"] !== "NONE") {
  actions.push(researchAction);
}

// 創建一個直接使用 OpenAI SDK 的適配器
const openai = new OpenAI({
  apiKey: process.env["OPENAI_API_KEY"],
});

// 使用 LangChain 的 ChatOpenAI 作為備用選項
const model = new ChatOpenAI({
  modelName: process.env["OPENAI_MODEL"] || "gpt-4o-mini",
  temperature: 0,
  apiKey: process.env["OPENAI_API_KEY"],
  baseURL: "https://api.openai.com/v1", // 添加 baseURL 以支持項目 API 密鑰
});

export const POST = async (req: NextRequest) => {
  try {
    const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
      runtime: new CopilotRuntime({
        actions: actions,
      }),
      serviceAdapter: new LangChainAdapter({
        chainFn: async ({ messages, tools }) => {
          try {
            // 嘗試使用 LangChain 的 ChatOpenAI
            return model.bindTools(tools, { strict: true }).stream(messages);
          } catch (error) {
            console.error('Error using LangChain adapter:', error);
            // 如果失敗，記錄錯誤但繼續執行（不拋出錯誤）
            // 這樣應用程序仍然可以運行，即使 AI 功能不可用
            return model.stream(messages);
          }
        },
      }),
      endpoint: req.nextUrl.pathname,
    });
    return handleRequest(req);
  } catch (error) {
    console.error('Error in POST handler:', error);
    return new Response(JSON.stringify({ error: 'Internal server error' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
};
