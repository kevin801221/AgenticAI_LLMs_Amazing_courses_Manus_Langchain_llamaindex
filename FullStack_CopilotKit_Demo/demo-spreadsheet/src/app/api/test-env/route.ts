import { NextResponse } from 'next/server';

export async function GET() {
  // 返回環境變數（注意：不要在生產環境中這樣做，這只是用於調試）
  return NextResponse.json({
    openaiApiKey: process.env.OPENAI_API_KEY ? `${process.env.OPENAI_API_KEY.substring(0, 10)}...` : 'not set',
    openaiModel: process.env.OPENAI_MODEL || 'not set',
    tavilyApiKey: process.env.TAVILY_API_KEY ? `${process.env.TAVILY_API_KEY.substring(0, 10)}...` : 'not set',
  });
}
