"use client";

import { useState } from "react";

// The new Tabs UI for "More Details"
const TabsUI = ({ parsed }: { parsed: any }) => {
  const [activeTab, setActiveTab] = useState("Overview");
  
  // Strip empty sections to prevent clutter
  const hasCode = !!parsed.CODE_EXAMPLE;
  const hasActions = !!parsed.DEVELOPER_ACTIONS;
  const hasWarnings = !!parsed.EDGE_CASES_AND_WARNINGS;
  const hasReferences = !!parsed.RELATED_DOCUMENTATION || !!parsed.RELATED_QUESTIONS;
  
  // If all are empty, don't show the tabs at all
  if (!hasCode && !hasActions && !hasWarnings && !hasReferences) return null;

  return (
    <div className="mt-8 border border-[#E5E7EB] rounded-xl overflow-hidden bg-white">
      <div className="flex border-b border-[#E5E7EB] bg-[#F8FAFC]">
        <button 
          onClick={() => setActiveTab("Overview")}
          className={`px-6 py-3 text-sm font-semibold transition ${activeTab === 'Overview' ? 'bg-white border-t-2 border-t-[#8B1E1E] text-[#8B1E1E]' : 'text-[#6B7280] hover:text-[#1F1F1F]'}`}
        >
          Overview
        </button>
        {(hasCode || hasActions) && (
          <button 
            onClick={() => setActiveTab("Implementation")}
            className={`px-6 py-3 text-sm font-semibold transition ${activeTab === 'Implementation' ? 'bg-white border-t-2 border-t-[#8B1E1E] text-[#8B1E1E]' : 'text-[#6B7280] hover:text-[#1F1F1F]'}`}
          >
            Implementation
          </button>
        )}
        {hasWarnings && (
          <button 
            onClick={() => setActiveTab("Warnings")}
            className={`px-6 py-3 text-sm font-semibold transition ${activeTab === 'Warnings' ? 'bg-white border-t-2 border-t-[#8B1E1E] text-[#8B1E1E]' : 'text-[#6B7280] hover:text-[#1F1F1F]'}`}
          >
            Warnings
          </button>
        )}
        {hasReferences && (
          <button 
            onClick={() => setActiveTab("References")}
            className={`px-6 py-3 text-sm font-semibold transition ${activeTab === 'References' ? 'bg-white border-t-2 border-t-[#8B1E1E] text-[#8B1E1E]' : 'text-[#6B7280] hover:text-[#1F1F1F]'}`}
          >
            References
          </button>
        )}
      </div>

      <div className="p-6">
        {activeTab === "Overview" && (
          <div className="space-y-4 text-[15px] leading-relaxed">
            {parsed.KEY_DETAILS ? parsed.KEY_DETAILS : <span className="text-gray-400 italic">No additional details available.</span>}
          </div>
        )}
        {activeTab === "Implementation" && (
          <div className="space-y-6">
            {hasCode && (
              <div>
                <h4 className="font-bold text-sm text-[#8B1E1E] mb-2">Code Example</h4>
                <div className="bg-[#1F1F1F] text-[#F8FAFC] p-4 rounded-lg font-mono text-sm whitespace-pre-wrap">
                  {parsed.CODE_EXAMPLE}
                </div>
              </div>
            )}
            {hasActions && (
              <div>
                <h4 className="font-bold text-sm text-[#8B1E1E] mb-2">Developer Actions</h4>
                <div className="text-[15px] leading-relaxed whitespace-pre-wrap">{parsed.DEVELOPER_ACTIONS}</div>
              </div>
            )}
          </div>
        )}
        {activeTab === "Warnings" && hasWarnings && (
          <div className="bg-[#FFF4F2] border border-[#FECDD3] p-4 rounded-lg text-[#9F1239] text-[15px] leading-relaxed whitespace-pre-wrap">
            <span className="font-bold">⚠️ Important:</span><br/>
            {parsed.EDGE_CASES_AND_WARNINGS}
          </div>
        )}
        {activeTab === "References" && hasReferences && (
          <div className="space-y-6">
            {parsed.RELATED_DOCUMENTATION && (
              <div>
                <h4 className="font-bold text-sm text-[#8B1E1E] mb-2">Related Documentation</h4>
                <div className="text-[15px] leading-relaxed whitespace-pre-wrap">{parsed.RELATED_DOCUMENTATION}</div>
              </div>
            )}
            {parsed.RELATED_QUESTIONS && (
              <div>
                <h4 className="font-bold text-sm text-[#8B1E1E] mb-2">Related Questions</h4>
                <div className="text-[15px] leading-relaxed whitespace-pre-wrap">{parsed.RELATED_QUESTIONS}</div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default function EnterpriseChat() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState<any[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  
  // Snippet state for Right Sidebar
  const [expandedSnippetIdx, setExpandedSnippetIdx] = useState<number | null>(null);

  const parseMessage = (text: string) => {
    const sections: Record<string, string> = {};
    let currentHeader = "explanation";
    
    const lines = text.split('\n');
    let currentContent: string[] = [];
    
    for (const line of lines) {
      if (line.match(/^#{2,4}\s+/)) {
        if (currentContent.length > 0) {
          sections[currentHeader] = currentContent.join('\n').trim();
        }
        currentHeader = line.replace(/^#{2,4}\s+/, '').trim().toUpperCase().replace(/ /g, '_');
        currentContent = [];
      } else {
        currentContent.push(line);
      }
    }
    if (currentContent.length > 0) {
      sections[currentHeader] = currentContent.join('\n').trim();
    }
    return sections;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setMessages((prev) => [...prev, { role: "user", content: query }]);
    setQuery("");
    setIsStreaming(true);

    try {
      const res = await fetch("http://localhost:8000/api/v1/chat/completions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });

      if (!res.body) throw new Error("No response body");
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      
      let assistantMessage: any = { role: "assistant", content: "", metadata: null, sources: [] };
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
              if (data.type === "metadata") {
                assistantMessage.metadata = data.content;
                setMessages((prev) => [...prev.slice(0, -1), { ...assistantMessage }]);
              } else if (data.type === "content") {
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
        <h1 className="font-bold text-xl mb-8 tracking-wide">DocuMind AI</h1>
        <button className="bg-white/10 hover:bg-white/20 p-3 rounded-lg mb-4 text-left transition font-medium">
          ➕ New Chat
        </button>
        <div className="text-sm opacity-60 mt-8 mb-4 uppercase tracking-widest font-semibold">Collections</div>
        <ul className="space-y-3">
          <li className="cursor-pointer hover:opacity-80 transition text-sm">📁 Authentication</li>
          <li className="cursor-pointer hover:opacity-80 transition text-sm">📁 Rate Limits</li>
        </ul>
      </div>

      {/* MAIN CONTENT - 55% */}
      <div className="w-[55%] flex flex-col p-8 border-r border-[#E5E7EB]">
        <div className="flex-1 overflow-y-auto space-y-8 pr-4">
          {messages.map((msg, i) => {
            if (msg.role === 'user') {
              return (
                <div key={i} className="p-6 rounded-2xl bg-[#FFFBF5] border border-[#E5E7EB] shadow-sm">
                  <div className="font-bold text-xl">{msg.content}</div>
                </div>
              );
            }

            const parsed = parseMessage(msg.content);
            const isLowConfidence = parsed.QUICK_ANSWER?.includes("could not find") || parsed.explanation?.includes("could not find");

            return (
              <div key={i} className="rounded-2xl bg-white shadow-sm border border-[#E5E7EB] overflow-hidden">
                {/* 10/10 Header: Telemetry & Metadata */}
                {msg.metadata && (
                  <div className="bg-[#F8FAFC] border-b border-[#E5E7EB] p-4 flex gap-6 text-sm">
                    <div className="flex items-center text-[#16A34A] font-semibold">
                      <span className="mr-2">🛡️</span> Confidence: {msg.metadata.confidence}%
                    </div>
                    <div className="flex items-center text-[#6B7280]">
                      <span className="mr-2">📄</span> {msg.metadata.sources} Sources
                    </div>
                    <div className="flex items-center text-[#6B7280]">
                      <span className="mr-2">🧩</span> {msg.metadata.chunks} Chunks
                    </div>
                    <div className="flex items-center text-[#6B7280]">
                      <span className="mr-2">⏱️</span> {msg.metadata.latency}
                    </div>
                  </div>
                )}
                
                <div className="p-8">
                  {isLowConfidence ? (
                    <div className="bg-[#FEF2F2] text-[#9F1239] p-4 rounded-lg font-medium">
                      ❌ I could not find a definitive answer in the available documentation.
                    </div>
                  ) : (
                    <>
                      {/* Progressive Disclosure: Only Quick Answer is shown immediately */}
                      <div className="mb-2">
                        <span className="font-bold text-[#8B1E1E] text-sm uppercase tracking-wide">Quick Answer</span>
                      </div>
                      <div className="text-[16px] leading-relaxed whitespace-pre-wrap text-[#1F1F1F]">
                        {parsed.QUICK_ANSWER || parsed.explanation || "Generating..."}
                      </div>

                      {/* Advanced Tabs UI for Details */}
                      <TabsUI parsed={parsed} />
                    </>
                  )}
                </div>
              </div>
            );
          })}
        </div>
        
        <form onSubmit={handleSubmit} className="mt-4">
          <input 
            className="w-full p-4 rounded-xl border border-[#E5E7EB] shadow-sm focus:outline-none focus:ring-2 focus:ring-[#8B1E1E] transition"
            placeholder="Ask anything about the documentation..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={isStreaming}
          />
        </form>
      </div>

      {/* RIGHT SIDEBAR - 25% (Source Transparency) */}
      <div className="w-[25%] p-6 bg-[#F8FAFC]">
        <h2 className="font-semibold mb-6 text-[#6B7280] uppercase tracking-wider text-sm">Retrieved Context</h2>
        {messages.length > 0 && messages[messages.length - 1].sources?.map((src: any, i: number) => (
          <div key={i} className="mb-4 bg-white border border-[#E5E7EB] rounded-xl shadow-sm overflow-hidden transition-all">
            <div 
              className="p-4 cursor-pointer hover:bg-[#F8FAFC] flex justify-between items-center"
              onClick={() => setExpandedSnippetIdx(expandedSnippetIdx === i ? null : i)}
            >
              <div>
                <div className="font-semibold text-sm text-[#8B1E1E]">📄 {src.source || "Unknown Source"}</div>
                <div className="text-xs text-[#16A34A] mt-1 font-medium">Verified Chunk</div>
              </div>
              <div className="text-[#6B7280] text-xs">{expandedSnippetIdx === i ? '▼' : '▶'}</div>
            </div>
            {/* Exactly render the raw snippet when clicked */}
            {expandedSnippetIdx === i && (
              <div className="p-4 bg-[#1F1F1F] text-[#F8FAFC] text-xs font-mono border-t border-[#E5E7EB]">
                {src.text}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
