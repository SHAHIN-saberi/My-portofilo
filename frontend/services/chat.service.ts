import { apiFetch } from "@/lib/api";
import { chatAdapter } from "@/lib/adapters";
import { ChatStateModel, Lang } from "@/types";

export async function queryChatbotService(query: string, lang: Lang = "en"): Promise<ChatStateModel> {
  const raw = await apiFetch("/api/v1/chatbot/query", {
    method: "POST",
    body: JSON.stringify({
      question: query,
      query: query,
      lang,
    }),
    autoRetry: false,
  });
  return chatAdapter(raw);
}
