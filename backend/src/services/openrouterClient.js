const OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions";
const DEFAULT_MODEL = "openai/gpt-4o-mini";
const REQUEST_TIMEOUT_MS = 45000;

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

  try {
    const response = await fetch(OPENROUTER_URL, {
      method: "POST",
      signal: controller.signal,
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        model: getConfiguredModel(),
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

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`OpenRouter request failed with ${response.status}: ${errorText}`);
    }

    const result = await response.json();
    return result?.choices?.[0]?.message?.content || "";
  } catch (error) {
    if (error.name === "AbortError") {
      throw new Error(`OpenRouter request timed out after ${REQUEST_TIMEOUT_MS}ms`);
    }

    throw error;
  } finally {
    clearTimeout(timeout);
  }
}
