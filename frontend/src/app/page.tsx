"use client";

import { useState } from "react";

export default function EnterpriseChat() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState<any[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setMessages((prev) => [...prev, { role: "user", content: query }]);
    setQuery("");
    setIsStreaming(true);

    try {
      // In production, include the JWT Authorization header
      const res = await fetch("http://localhost:8000/api/v1/chat/completions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });

      if (!res.body) throw new Error("No response body");
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      
      let assistantMessage = { role: "assistant", content: "", sources: [] };
      setMessages((prev) => [...prev, assistantMessage]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split("\n\n");
        
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const dataStr = line.replace("data: ", "");
            if (dataStr === "[DONE]") {
              setIsStreaming(false);
              break;
            }
            
            try {
              const data = JSON.parse(dataStr);
              if (data.type === "content") {
                assistantMessage.content += data.content;
                setMessages((prev) => [...prev.slice(0, -1), { ...assistantMessage }]);
              } else if (data.type === "sources") {
                assistantMessage.sources = data.content;
                setMessages((prev) => [...prev.slice(0, -1), { ...assistantMessage }]);
              }
            } catch (e) {
              console.error("SSE parse error", e);
            }
          }
        }
      }
    } catch (err) {
      console.error(err);
      setIsStreaming(false);
    }
  };

  return (
    <div className="flex h-screen bg-[#FFFBF5] text-[#1F1F1F] font-inter">
      {/* LEFT SIDEBAR - 20% */}
      <div className="w-1/5 bg-[#8B1E1E] text-white p-6 flex flex-col">
        <h1 className="font-bold text-xl mb-8">DocuMind AI</h1>
        <button className="bg-white/10 hover:bg-white/20 p-3 rounded-lg mb-4 text-left transition">
          ➕ New Chat
        </button>
        <div className="text-sm opacity-70 mt-8 mb-4 uppercase tracking-widest">Collections</div>
        <ul className="space-y-3">
          <li className="cursor-pointer hover:opacity-80">📁 Authentication</li>
          <li className="cursor-pointer hover:opacity-80">📁 Rate Limits</li>
        </ul>
      </div>

      {/* MAIN CONTENT - 55% */}
      <div className="w-[55%] flex flex-col p-8 border-r border-[#E5E7EB]">
        <div className="flex-1 overflow-y-auto space-y-6">
          {messages.map((msg, i) => (
            <div key={i} className={`p-6 rounded-2xl ${msg.role === 'assistant' ? 'bg-white shadow-sm border border-[#E5E7EB]' : ''}`}>
              {msg.role === 'assistant' ? (
                <div>
                  <div className="font-bold text-[#8B1E1E] mb-2">✅ Quick Answer</div>
                  <div className="whitespace-pre-wrap">{msg.content}</div>
                </div>
              ) : (
                <div className="font-semibold">{msg.content}</div>
              )}
            </div>
          ))}
        </div>
        
        <form onSubmit={handleSubmit} className="mt-4">
          <input 
            className="w-full p-4 rounded-xl border border-[#E5E7EB] shadow-sm focus:outline-none focus:ring-2 focus:ring-[#8B1E1E]"
            placeholder="Ask anything about the documentation..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={isStreaming}
          />
        </form>
      </div>

      {/* RIGHT SIDEBAR - 25% */}
      <div className="w-[25%] p-6 bg-white">
        <h2 className="font-semibold mb-6">Context Panel</h2>
        {messages.length > 0 && messages[messages.length - 1].sources?.map((src: any, i: number) => (
          <div key={i} className="mb-4 p-4 border border-[#E5E7EB] rounded-xl bg-[#FFFBF5]">
            <div className="font-semibold text-sm">📄 {src.source || "Unknown Source"}</div>
            <div className="text-xs text-green-600 mt-1">Relevance: 98%</div>
          </div>
        ))}
      </div>
    </div>
  );
}
