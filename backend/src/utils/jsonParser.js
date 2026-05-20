export function parseModelJsonResponse(rawText) {
  try {
    return JSON.parse(rawText);
  } catch (firstError) {
    const firstBrace = rawText.indexOf("{");
    const lastBrace = rawText.lastIndexOf("}");

    if (firstBrace !== -1 && lastBrace !== -1 && lastBrace > firstBrace) {
      const possibleJson = rawText.slice(firstBrace, lastBrace + 1);

      try {
        return JSON.parse(possibleJson);
      } catch (secondError) {
        return {
          parse_error: true,
          raw_output: rawText
        };
      }
    }

    return {
      parse_error: true,
      raw_output: rawText
    };
  }
}
