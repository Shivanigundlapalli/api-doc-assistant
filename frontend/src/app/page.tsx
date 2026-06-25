"use client";

import { useState } from "react";

// Professional SVG Icons
const Icons = {
  Plus: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>,
  Search: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>,
  Settings: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>,
  Paperclip: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l8.57-8.57A4 4 0 1 1 18 8.84l-8.59 8.57a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>,
  Mic: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" x2="12" y1="19" y2="22"/></svg>,
  Send: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></svg>,
  CheckCircle: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="m9 11 3 3L22 4"/></svg>,
  Code: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>,
  AlertTriangle: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>,
  Book: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/></svg>,
  Folder: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z"/></svg>,
  ChevronDown: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m6 9 6 6 6-6"/></svg>,
  ChevronRight: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m9 18 6-6-6-6"/></svg>
};

// Advanced React Tabs
const TabsUI = ({ parsed }: { parsed: any }) => {
  const [activeTab, setActiveTab] = useState("Overview");
  
  const hasCode = !!parsed.CODE_EXAMPLE;
  const hasActions = !!parsed.DEVELOPER_ACTIONS;
  const hasWarnings = !!parsed.EDGE_CASES_AND_WARNINGS;
  const hasReferences = !!parsed.RELATED_DOCUMENTATION || !!parsed.RELATED_QUESTIONS;
  
  if (!hasCode && !hasActions && !hasWarnings && !hasReferences) return null;

  return (
    <div className="mt-6 border border-[#E2E8F0] rounded-md overflow-hidden bg-white">
      <div className="flex border-b border-[#E2E8F0] bg-[#F8FAFC]">
        <button 
          onClick={() => setActiveTab("Overview")}
          className={`px-6 py-3 text-sm font-medium transition ${activeTab === 'Overview' ? 'bg-white border-t-2 border-t-[#0F172A] text-[#0F172A]' : 'text-[#64748B] hover:text-[#0F172A]'}`}
        >
          Overview
        </button>
        {(hasCode || hasActions) && (
          <button 
            onClick={() => setActiveTab("Implementation")}
            className={`px-6 py-3 text-sm font-medium transition ${activeTab === 'Implementation' ? 'bg-white border-t-2 border-t-[#0F172A] text-[#0F172A]' : 'text-[#64748B] hover:text-[#0F172A]'}`}
          >
            Implementation
          </button>
        )}
        {hasWarnings && (
          <button 
            onClick={() => setActiveTab("Warnings")}
            className={`px-6 py-3 text-sm font-medium transition ${activeTab === 'Warnings' ? 'bg-white border-t-2 border-t-[#0F172A] text-[#0F172A]' : 'text-[#64748B] hover:text-[#0F172A]'}`}
          >
            Warnings
          </button>
        )}
        {hasReferences && (
          <button 
            onClick={() => setActiveTab("References")}
            className={`px-6 py-3 text-sm font-medium transition ${activeTab === 'References' ? 'bg-white border-t-2 border-t-[#0F172A] text-[#0F172A]' : 'text-[#64748B] hover:text-[#0F172A]'}`}
          >
            References
          </button>
        )}
      </div>

      <div className="p-6">
        {activeTab === "Overview" && (
          <div className="space-y-4 text-[15px] leading-relaxed text-[#334155]">
            {parsed.KEY_DETAILS ? parsed.KEY_DETAILS : <span className="text-[#94A3B8] italic">No additional details available.</span>}
          </div>
        )}
        {activeTab === "Implementation" && (
          <div className="space-y-6">
            {hasCode && (
              <div>
                <h4 className="font-semibold text-sm text-[#0F172A] mb-3 flex items-center gap-2"><Icons.Code /> Code Example</h4>
                <div className="bg-[#18181B] text-[#F8FAFC] p-4 rounded-md font-mono text-sm whitespace-pre-wrap">
                  {parsed.CODE_EXAMPLE}
                </div>
              </div>
            )}
            {hasActions && (
              <div>
                <h4 className="font-semibold text-sm text-[#0F172A] mb-3">Developer Actions</h4>
                <div className="text-[15px] leading-relaxed whitespace-pre-wrap text-[#334155]">{parsed.DEVELOPER_ACTIONS}</div>
              </div>
            )}
          </div>
        )}
        {activeTab === "Warnings" && hasWarnings && (
          <div className="bg-[#FEF2F2] border border-[#FECDD3] p-4 rounded-md text-[#9F1239] text-[15px] leading-relaxed whitespace-pre-wrap">
            <span className="font-bold flex items-center gap-2 mb-2"><Icons.AlertTriangle /> Important</span>
            {parsed.EDGE_CASES_AND_WARNINGS}
          </div>
        )}
        {activeTab === "References" && hasReferences && (
          <div className="space-y-6">
            {parsed.RELATED_DOCUMENTATION && (
              <div>
                <h4 className="font-semibold text-sm text-[#0F172A] mb-3 flex items-center gap-2"><Icons.Book /> Related Documentation</h4>
                <div className="text-[15px] leading-relaxed whitespace-pre-wrap text-[#334155]">{parsed.RELATED_DOCUMENTATION}</div>
              </div>
            )}
            {parsed.RELATED_QUESTIONS && (
              <div>
                <h4 className="font-semibold text-sm text-[#0F172A] mb-3">Related Questions</h4>
                <div className="text-[15px] leading-relaxed whitespace-pre-wrap text-[#334155]">{parsed.RELATED_QUESTIONS}</div>
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
  const [expandedSnippetIdx, setExpandedSnippetIdx] = useState<number | null>(null);

  const parseMessage = (text: string) => {
    const sections: Record<string, string> = {};
    let currentHeader = "explanation";
    const lines = text.split('\n');
    let currentContent: string[] = [];
    
    for (const line of lines) {
      if (line.match(/^#{2,4}\s+/)) {
        if (currentContent.length > 0) sections[currentHeader] = currentContent.join('\n').trim();
        currentHeader = line.replace(/^#{2,4}\s+/, '').trim().toUpperCase().replace(/ /g, '_');
        currentContent = [];
      } else {
        currentContent.push(line);
      }
    }
    if (currentContent.length > 0) sections[currentHeader] = currentContent.join('\n').trim();
    return sections;
  };

  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
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
              console.error(e);
            }
          }
        }
      }
    } catch (err) {
      console.error(err);
      setIsStreaming(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="flex h-screen bg-[#FAFAFA] text-[#0F172A] font-inter">
      {/* 1. LEFT SIDEBAR */}
      <div className="w-[260px] bg-[#0F172A] text-[#F8FAFC] flex flex-col flex-shrink-0">
        <div className="p-4 border-b border-[#1E293B]">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-8 h-8 rounded-md bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center font-bold">D</div>
            <span className="font-semibold text-[15px]">DocuMind AI</span>
          </div>
          <button className="w-full bg-[#1E293B] hover:bg-[#334155] text-sm font-medium py-2 px-3 rounded-md flex items-center gap-2 transition">
            <Icons.Plus /> New Chat
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-6">
          <div>
            <div className="text-xs font-semibold text-[#94A3B8] mb-3 uppercase tracking-wider">Today</div>
            <ul className="space-y-1">
              <li className="text-[13px] text-[#CBD5E1] hover:text-white hover:bg-[#1E293B] px-2 py-1.5 rounded cursor-pointer truncate">Rate limits and errors</li>
              <li className="text-[13px] text-[#CBD5E1] hover:text-white hover:bg-[#1E293B] px-2 py-1.5 rounded cursor-pointer truncate">OAuth2 Setup Guide</li>
            </ul>
          </div>
          <div>
            <div className="text-xs font-semibold text-[#94A3B8] mb-3 uppercase tracking-wider">Previous 7 Days</div>
            <ul className="space-y-1">
              <li className="text-[13px] text-[#CBD5E1] hover:text-white hover:bg-[#1E293B] px-2 py-1.5 rounded cursor-pointer truncate">Pagination parameters</li>
              <li className="text-[13px] text-[#CBD5E1] hover:text-white hover:bg-[#1E293B] px-2 py-1.5 rounded cursor-pointer truncate">Webhooks security</li>
            </ul>
          </div>
          <div>
            <div className="text-xs font-semibold text-[#94A3B8] mb-3 uppercase tracking-wider flex items-center justify-between">
              Collections <Icons.Plus />
            </div>
            <ul className="space-y-1">
              <li className="text-[13px] text-[#CBD5E1] hover:text-white hover:bg-[#1E293B] px-2 py-1.5 rounded cursor-pointer flex items-center gap-2"><Icons.Folder /> Core API V2</li>
              <li className="text-[13px] text-[#CBD5E1] hover:text-white hover:bg-[#1E293B] px-2 py-1.5 rounded cursor-pointer flex items-center gap-2"><Icons.Folder /> Admin Dashboard</li>
            </ul>
          </div>
        </div>

        <div className="p-4 border-t border-[#1E293B] space-y-2">
          <button className="w-full text-left text-[13px] text-[#CBD5E1] hover:text-white hover:bg-[#1E293B] px-2 py-2 rounded flex items-center gap-2 transition">
            <Icons.Search /> Search Chats
          </button>
          <button className="w-full text-left text-[13px] text-[#CBD5E1] hover:text-white hover:bg-[#1E293B] px-2 py-2 rounded flex items-center gap-2 transition">
            <Icons.Settings /> Settings
          </button>
        </div>
      </div>

      {/* 2. MAIN CONTENT */}
      <div className="flex-1 flex flex-col min-w-0 border-r border-[#E2E8F0]">
        
        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-8">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center max-w-xl mx-auto">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 mb-6 flex items-center justify-center shadow-lg">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
              </div>
              <h2 className="text-2xl font-bold text-[#0F172A] mb-2">How can I help you build?</h2>
              <p className="text-[#64748B] mb-8 text-sm">Ask anything about the documentation, SDKs, or API architecture.</p>
              
              <div className="grid grid-cols-2 gap-4 w-full">
                <div className="p-4 border border-[#E2E8F0] rounded-xl hover:border-[#94A3B8] hover:bg-white cursor-pointer transition text-left text-sm text-[#334155] shadow-sm">
                  <span className="font-semibold block mb-1">Authentication</span>
                  How do I implement OAuth2?
                </div>
                <div className="p-4 border border-[#E2E8F0] rounded-xl hover:border-[#94A3B8] hover:bg-white cursor-pointer transition text-left text-sm text-[#334155] shadow-sm">
                  <span className="font-semibold block mb-1">Rate Limits</span>
                  What are the API thresholds?
                </div>
              </div>
            </div>
          ) : (
            <div className="max-w-3xl mx-auto space-y-10">
              {messages.map((msg, i) => {
                if (msg.role === 'user') {
                  return (
                    <div key={i} className="flex gap-4">
                      <div className="w-8 h-8 rounded-full bg-[#0F172A] text-white flex items-center justify-center text-xs font-bold flex-shrink-0">JD</div>
                      <div className="font-medium text-[17px] text-[#0F172A] pt-1">{msg.content}</div>
                    </div>
                  );
                }

                const parsed = parseMessage(msg.content);
                const isLowConfidence = parsed.QUICK_ANSWER?.includes("could not find") || parsed.explanation?.includes("could not find");

                return (
                  <div key={i} className="flex gap-4">
                    <div className="w-8 h-8 rounded-md bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center flex-shrink-0 shadow-sm text-white">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
                    </div>
                    <div className="flex-1 min-w-0">
                      {/* Telemetry Header */}
                      {msg.metadata && (
                        <div className="flex items-center gap-4 text-[13px] text-[#64748B] mb-3">
                          <span className={`font-semibold flex items-center gap-1 ${msg.metadata.confidence >= 90 ? 'text-[#16A34A]' : msg.metadata.confidence > 0 ? 'text-[#D97706]' : 'text-[#DC2626]'}`}>
                            <Icons.CheckCircle /> Confidence: {msg.metadata.confidence}%
                          </span>
                          <span className="flex items-center gap-1"><Icons.Book /> {msg.metadata.sources} Sources</span>
                          <span>{msg.metadata.chunks} Chunks</span>
                          <span>{msg.metadata.latency}</span>
                        </div>
                      )}
                      
                      {isLowConfidence ? (
                        <div className="text-[#0F172A] text-[16px] leading-relaxed">
                          I could not find this information in the available documentation.
                        </div>
                      ) : (
                        <div>
                          <div className="text-[16px] leading-relaxed whitespace-pre-wrap text-[#334155]">
                            {parsed.QUICK_ANSWER || parsed.explanation || "Generating response..."}
                          </div>
                          {Object.keys(parsed).length > 1 && <TabsUI parsed={parsed} />}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
        
        {/* Input Area */}
        <div className="p-6 bg-white border-t border-[#E2E8F0]">
          <div className="max-w-3xl mx-auto">
            <form onSubmit={handleSubmit} className="relative bg-[#F8FAFC] border border-[#CBD5E1] rounded-2xl shadow-sm focus-within:ring-2 focus-within:ring-[#0F172A] focus-within:border-transparent transition-all">
              <textarea 
                className="w-full bg-transparent p-4 pr-32 rounded-2xl resize-none focus:outline-none min-h-[56px] text-[15px] leading-relaxed text-[#0F172A] placeholder:text-[#94A3B8]"
                placeholder="Ask a question about your documentation..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={isStreaming}
                rows={1}
                style={{ overflow: 'hidden' }}
              />
              <div className="absolute right-2 bottom-2 flex items-center gap-1">
                <button type="button" className="p-2 text-[#64748B] hover:text-[#0F172A] hover:bg-[#F1F5F9] rounded-lg transition" title="Attach File">
                  <Icons.Paperclip />
                </button>
                <button type="button" className="p-2 text-[#64748B] hover:text-[#0F172A] hover:bg-[#F1F5F9] rounded-lg transition" title="Voice Input">
                  <Icons.Mic />
                </button>
                <button 
                  type="submit" 
                  disabled={isStreaming || !query.trim()}
                  className="p-2 ml-1 bg-[#0F172A] text-white hover:bg-[#334155] disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition shadow-sm" 
                  title="Send"
                >
                  <Icons.Send />
                </button>
              </div>
            </form>
            <div className="text-center mt-3 text-xs text-[#94A3B8]">
              DocuMind AI can make mistakes. Verify critical code before deploying.
            </div>
          </div>
        </div>
      </div>

      {/* 3. RIGHT SIDEBAR (Sources Transparency) */}
      <div className="w-[300px] p-6 bg-white flex flex-col flex-shrink-0">
        <h2 className="font-semibold text-[13px] text-[#64748B] uppercase tracking-wider mb-6 flex items-center gap-2">
          <Icons.Book /> Retrieved Context
        </h2>
        <div className="flex-1 overflow-y-auto space-y-4 pr-2">
          {messages.length > 0 && messages[messages.length - 1].sources?.map((src: any, i: number) => (
            <div key={i} className="border border-[#E2E8F0] rounded-md overflow-hidden hover:border-[#CBD5E1] transition shadow-sm">
              <div 
                className="p-3 cursor-pointer bg-[#FAFAFA] flex items-start justify-between"
                onClick={() => setExpandedSnippetIdx(expandedSnippetIdx === i ? null : i)}
              >
                <div className="min-w-0 pr-2">
                  <div className="font-medium text-[13px] text-[#0F172A] truncate" title={src.source}>{src.source}</div>
                  <div className="text-[11px] text-[#64748B] mt-1 truncate">Section: {src.section || "General"}</div>
                </div>
                <div className="text-[#94A3B8] mt-1 flex-shrink-0">
                  {expandedSnippetIdx === i ? <Icons.ChevronDown /> : <Icons.ChevronRight />}
                </div>
              </div>
              
              {expandedSnippetIdx === i && (
                <div className="p-3 bg-white border-t border-[#E2E8F0]">
                  <div className="text-[12px] font-mono text-[#334155] leading-relaxed break-words">
                    {src.text}
                  </div>
                </div>
              )}
            </div>
          ))}
          {(!messages.length || !messages[messages.length - 1].sources?.length) && (
            <div className="text-[13px] text-[#94A3B8] italic text-center mt-10">
              No context retrieved yet.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
