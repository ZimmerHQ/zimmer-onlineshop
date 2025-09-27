import { NextResponse } from "next/server";

export async function POST(req: Request) {
  try {
    const { message, conversation_id } = await req.json();

    if (!message) {
      return NextResponse.json({ error: "Message is required" }, { status: 400 });
    }

    // Send message to backend API with proper payload format
    const backendResponse = await fetch(
      (process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000") + "/api/chat",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          message, 
          conversation_id: conversation_id || "default" 
        }),
      }
    );

    const data = await backendResponse.json();
    return NextResponse.json(data);
  } catch (error: any) {
    console.error("Chat API error:", error);
    return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
  }
}
