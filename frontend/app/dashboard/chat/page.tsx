"use client";
import React from "react";
import Link from "next/link";

export default function DashboardChatPage() {
  const chatUrl =
    (typeof window !== "undefined" && process?.env?.NEXT_PUBLIC_CHAT_URL) ||
    "/chat";

  return (
    <div className="h-full w-full p-4 md:p-6">
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-xl md:text-2xl font-semibold">Chatbot</h1>
        <Link
          href={chatUrl}
          target="_blank"
          rel="noreferrer"
          className="rounded-2xl px-4 py-2 border hover:bg-gray-50 transition"
        >
          Open in new tab
        </Link>
      </div>

      <div className="w-full rounded-2xl overflow-hidden border">
        <div className="h-[calc(100vh-10rem)] w-full">
          <iframe
            src={chatUrl}
            title="Zimmer Shop Chatbot"
            className="h-full w-full"
            allow="clipboard-read; clipboard-write"
          />
        </div>
      </div>
    </div>
  );
}
