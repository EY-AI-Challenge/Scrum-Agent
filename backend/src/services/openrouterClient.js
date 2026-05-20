import { logError, logEvent } from "../utils/logger.js";

const OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions";
const DEFAULT_MODEL = "openai/gpt-4o-mini";
// Increased timeout to allow slower model responses during planning
const REQUEST_TIMEOUT_MS = 120000;

export function getConfiguredModel() {
  return process.env.OPENROUTER_MODEL || DEFAULT_MODEL;
}

export async function callOpenRouter(prompt) {
  const apiKey = process.env.OPENROUTER_API_KEY;

  if (!apiKey) {
    throw new Error("OPENROUTER_API_KEY is missing. Set it in .env or enable USE_MOCK_AI=true.");
  }

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  const model = getConfiguredModel();
  try {
    logEvent("OpenRouter", "sending request", {
      model,
      prompt_length: String(prompt || "").length
    });

    const response = await fetch(OPENROUTER_URL, {
      method: "POST",
      signal: controller.signal,
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        model,
        max_tokens: 7000,
        messages: [
          {
            role: "system",
            content: "You are an AI Scrum Master. Return valid JSON only."
          },
          {
            role: "user",
            content: prompt
          }
        ],
        response_format: {
          type: "json_object"
        },
        temperature: 0.2
      })
    });

    logEvent("OpenRouter", "response received", {
      status: response.status,
      ok: response.ok,
      content_type: response.headers.get("content-type"),
      content_length: response.headers.get("content-length"),
      transfer_encoding: response.headers.get("transfer-encoding")
    });
    const respText = await response.text();
    logEvent("OpenRouter", "response body preview", respText.slice(0, 1000));

    if (!response.ok) {
      const errorText = respText;
      throw new Error(`OpenRouter request failed with ${response.status}: ${errorText}`);
    }

    const result = respText ? JSON.parse(respText) : {};
    try {
      const resultStr = JSON.stringify(result);
      logEvent("OpenRouter", "parsed result preview", resultStr.slice(0, 2000));
    } catch (err) {
      logEvent("OpenRouter", "could not stringify result");
    }
    logEvent("OpenRouter", "received choices", {
      choices: (result?.choices || []).length
    });
    return result?.choices?.[0]?.message?.content || result?.choices?.[0]?.message || "";
  } catch (error) {
    if (error && error.name === "AbortError") {
      logError("OpenRouter", `request timed out after ${REQUEST_TIMEOUT_MS}ms`, error);
      throw new Error(`OpenRouter request timed out after ${REQUEST_TIMEOUT_MS}ms`);
    }

    logError("OpenRouter", "request error", error);
    throw error;
  } finally {
    clearTimeout(timeout);
  }
}
