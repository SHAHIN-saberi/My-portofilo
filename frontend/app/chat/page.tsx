"use client";

import React, { useState } from "react";
import { queryChatbotService } from "@/services/chat.service";
import { normalizeError } from "@/lib/api";
import { SafeChatSource, UIState } from "@/types";
import { useLanguage } from "@/hooks/useLanguage";

interface MessageItem {
  id: string;
  sender: "user" | "bot";
  text: string;
  status?: UIState;
  sources?: SafeChatSource[] | null;
  rawAnswer?: string;
  onRetryQuery?: string;
}

export default function ChatPage() {
  const { lang } = useLanguage();
  const [messages, setMessages] = useState<MessageItem[]>([
    {
      id: "init-msg",
      sender: "bot",
      text:
        lang === "fa"
          ? "سلام! من دستیار هوشمند این پروفایل هستم. هر سوالی درباره سوابق کاری، مهارت‌ها، یا پروژه‌ها دارید بپرسید."
          : "Hello! I am the AI assistant for this professional profile. Feel free to ask any questions regarding experience, skills, projects, or education.",
      status: "idle",
    },
  ]);
  const [input, setInput] = useState("");
  const [chatStatus, setChatStatus] = useState<UIState>("idle");

  const executeQuery = async (queryText: string) => {
    if (!queryText || chatStatus === "loading") return;

    setChatStatus("loading");
    try {
      // Consumes ONLY adapter-processed output (ChatStateModel)
      const res = await queryChatbotService(queryText, lang);

      const statusMap: UIState = res.state;

      const botMsg: MessageItem = {
        id: `bot-${Date.now()}`,
        sender: "bot",
        text: res.answer,
        status: statusMap,
        sources: statusMap === "answered" ? res.sources : null,
        rawAnswer: res.answer,
        onRetryQuery: (statusMap === "error" || statusMap === "needs_clarification") ? queryText : undefined,
      };

      setMessages((prev) => [...prev, botMsg]);
      setChatStatus(statusMap);
    } catch (err: unknown) {
      const normErr = normalizeError(err);
      const botMsg: MessageItem = {
        id: `bot-err-${Date.now()}`,
        sender: "bot",
        text: normErr.message,
        status: "error",
        onRetryQuery: queryText,
      };
      setMessages((prev) => [...prev, botMsg]);
      setChatStatus("error");
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const queryText = input.trim();
    if (!queryText || chatStatus === "loading") return;

    const userMsg: MessageItem = {
      id: `user-${Date.now()}`,
      sender: "user",
      text: queryText,
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    await executeQuery(queryText);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 flex flex-col h-[calc(100vh-180px)] min-h-[600px]">
      <div className="border-b border-slate-200 pb-4 mb-4 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 flex items-center gap-2">
            💬 {lang === "fa" ? "چت با دستیار هوش مصنوعی (RAG)" : "Interactive AI Assistant (RAG)"}
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            {lang === "fa"
              ? "سیستم چت مبتنی بر ماشین حالت و لایه آداپتور ضد اختلال (Adapter Firewall)."
              : "State-machine RAG interface consuming drift-proof adapter firewall outputs."}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-slate-500">System State:</span>
          <span
            className={`px-2.5 py-1 rounded text-xs font-mono font-bold uppercase ${
              chatStatus === "loading"
                ? "bg-blue-100 text-blue-800 animate-pulse"
                : chatStatus === "answered"
                ? "bg-emerald-100 text-emerald-800"
                : chatStatus === "no_answer"
                ? "bg-amber-100 text-amber-800"
                : chatStatus === "unrelated"
                ? "bg-purple-100 text-purple-800"
                : chatStatus === "needs_clarification"
                ? "bg-sky-100 text-sky-800"
                : chatStatus === "error"
                ? "bg-red-100 text-red-800"
                : "bg-slate-200 text-slate-700"
            }`}
          >
            {chatStatus}
          </span>
        </div>
      </div>

      {/* Messages Window */}
      <div className="flex-1 bg-white border border-slate-200 rounded-2xl p-6 overflow-y-auto space-y-4 shadow-inner">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex flex-col ${msg.sender === "user" ? "items-end" : "items-start"}`}
          >
            <div
              className={`max-w-[85%] rounded-2xl px-5 py-3.5 text-sm leading-relaxed shadow-xs ${
                msg.sender === "user"
                  ? "bg-blue-600 text-white rounded-br-none"
                  : msg.status === "error"
                  ? "bg-red-50 text-red-800 border border-red-200 rounded-bl-none"
                  : msg.status === "no_answer"
                  ? "bg-amber-50 text-amber-900 border border-amber-200 rounded-bl-none"
                  : msg.status === "unrelated"
                  ? "bg-purple-50 text-purple-900 border border-purple-200 rounded-bl-none"
                  : msg.status === "needs_clarification"
                  ? "bg-sky-50 text-sky-900 border border-sky-200 rounded-bl-none"
                  : "bg-slate-100 text-slate-800 rounded-bl-none"
              }`}
            >
              {msg.sender === "bot" && (
                <div className="text-[10px] font-bold uppercase tracking-wider mb-1 flex items-center justify-between gap-3 opacity-75">
                  <span>🤖 AI Assistant</span>
                  {msg.status && (
                    <span
                      className={`px-1.5 py-0.5 rounded text-[9px] font-mono ${
                        msg.status === "answered" || msg.status === "idle"
                          ? "bg-emerald-200 text-emerald-900"
                          : msg.status === "no_answer"
                          ? "bg-amber-200 text-amber-900"
                          : msg.status === "unrelated"
                          ? "bg-purple-200 text-purple-900"
                          : msg.status === "needs_clarification"
                          ? "bg-sky-200 text-sky-900"
                          : "bg-red-200 text-red-900"
                      }`}
                    >
                      state: {msg.status}
                    </span>
                  )}
                </div>
              )}
              <p className="whitespace-pre-line">{msg.text}</p>

              {/* Explicit Retry UI on error or needs_clarification state */}
              {(msg.status === "error" || msg.status === "needs_clarification") && msg.onRetryQuery && (
                <div className="mt-3 pt-2 border-t border-slate-200 flex justify-end">
                  <button
                    onClick={() => executeQuery(msg.onRetryQuery!)}
                    disabled={chatStatus === "loading"}
                    className={`px-3 py-1 text-white rounded text-xs font-bold transition shadow-xs ${
                      msg.status === "error"
                        ? "bg-red-600 hover:bg-red-700"
                        : "bg-sky-600 hover:bg-sky-700"
                    }`}
                  >
                    🔄 {msg.status === "needs_clarification" ? "Rephrase & Retry" : "Retry Query"}
                  </button>
                </div>
              )}

              {/* Render sources only when status === "answered" and sources is not null/empty */}
              {msg.status === "answered" && msg.sources && msg.sources.length > 0 && (
                <div className="mt-3 pt-2 border-t border-slate-200/60 text-[11px] space-y-1">
                  <span className="font-bold opacity-80">📚 RAG Citations / Sources:</span>
                  <div className="flex flex-wrap gap-1.5 pt-0.5">
                    {msg.sources.map((src, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-0.5 rounded bg-white/80 border border-slate-300 text-slate-700 font-mono text-[10px]"
                      >
                        [{src.source_type} #{src.source_id}] (score: {typeof src.score === "number" ? src.score.toFixed(2) : src.score})
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {chatStatus === "loading" && (
          <div className="flex items-start">
            <div className="bg-slate-100 text-slate-600 rounded-2xl rounded-bl-none px-5 py-3.5 text-sm flex items-center gap-2 border border-slate-200">
              <span className="animate-spin text-base">⏳</span>
              <span className="font-medium">{lang === "fa" ? "در حال بازیابی و پردازش (RAG Adapter)..." : "Processing through RAG Adapter firewall..."}</span>
            </div>
          </div>
        )}
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="mt-4 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={
            lang === "fa"
              ? "سوال خود را بپرسید (مثلاً: مهارت‌های اصلی شاهین چیست؟)"
              : "Ask a question about the profile knowledge base..."
          }
          disabled={chatStatus === "loading"}
          className="flex-1 px-4 py-3 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm bg-white shadow-xs disabled:bg-slate-50"
        />
        <button
          type="submit"
          disabled={chatStatus === "loading" || !input.trim()}
          className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-xl font-bold text-sm transition shadow-xs flex items-center justify-center min-w-[100px]"
        >
          {chatStatus === "loading" ? (lang === "fa" ? "پردازش..." : "...") : lang === "fa" ? "ارسال" : "Send"}
        </button>
      </form>
    </div>
  );
}
