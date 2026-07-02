import { ChatStateModel, ChatStatusType, SafeChatSource } from "@/types";
import { safeArray, safeNumber, safeString } from "./base.adapter";

export function adaptChatSourceItem(raw: unknown): SafeChatSource {
  if (!raw || typeof raw !== "object") {
    return { source_type: "unknown", source_id: 0, score: 0 };
  }
  const item = raw as Record<string, any>;
  return {
    source_type: safeString(item.source_type, "unknown") || "unknown",
    source_id: safeNumber(item.source_id, 0) || 0,
    score: safeNumber(item.score, 0) || 0,
  };
}

export function chatAdapter(raw: unknown): ChatStateModel {
  if (raw === undefined || raw === null || typeof raw !== "object") {
    return {
      state: "error",
      answer: "I'm sorry, I couldn't generate an answer right now.",
      sources: [],
      raw,
      isValid: false,
    };
  }

  const rawObj = raw as Record<string, any>;
  let stateStatus: ChatStatusType = "answered";
  const rawStatus = safeString(rawObj.status, "answered");

  if (rawStatus === "no_answer") {
    stateStatus = "no_answer";
  } else if (rawStatus === "error") {
    stateStatus = "error";
  } else {
    stateStatus = "answered";
  }

  let answerText = safeString(rawObj.answer, "") || "";
  if (stateStatus === "no_answer" && !answerText.trim()) {
    answerText = "No relevant answer found in the profile knowledge base.";
  } else if (stateStatus === "error" && !answerText.trim()) {
    answerText = "I'm sorry, I couldn't generate an answer right now.";
  }

  const sourcesRaw = rawObj.sources;
  const sources: SafeChatSource[] =
    stateStatus === "answered" && Array.isArray(sourcesRaw)
      ? safeArray(sourcesRaw, adaptChatSourceItem)
      : [];

  return {
    state: stateStatus,
    answer: answerText,
    sources,
    raw,
    isValid: true,
  };
}
