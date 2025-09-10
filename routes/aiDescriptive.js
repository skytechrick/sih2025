import { GoogleGenerativeAI } from "@google/generative-ai";
import { config } from "dotenv";
config({ quiet: true });

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

export async function getFarmInsight(userInput, modelOutput) {
    const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

    const prompt = `
You are an AI agricultural assistant.
Your task:
- Read BOTH the user input data and our processed model output.
- Generate a descriptive, farmer-friendly report.
- Output should be JSON with 3 keys:
  1. "success": true or false (based on if the data is sufficient or looks incorrect)
  2. "english": descriptive explanation in English with farming emojis 🌱🚜🌾
  3. "hindi": same explanation in Hindi with farming emojis 🌱🚜🌾
- Make the output engaging, detailed, and add insights (soil, weather, fertilizer, cost, risks, recommendations).
- If some values look unrealistic or missing, still generate a report but mark "success": false.

Here is the user input:
${JSON.stringify(userInput, null, 2)}

Here is the model output:
${JSON.stringify(modelOutput, null, 2)}

You are an AI agricultural assistant.
Return ONLY valid JSON, nothing else.
Keys: success, english, hindi.

Return ONLY valid JSON.
Do not use \`\`\`json or markdown formatting.
Return raw JSON only.

`;

    const result = await model.generateContent(prompt);

    return extractJson(result.response.text());

}

function extractJson(responseData) {
    try {
        let text = responseData;

        text = text.replace(/```json|```/g, "").trim();

        if (typeof text === "string") {
            try {
                text = JSON.parse(text);
            } catch {
            }
        }
        const obj = typeof text === "string" ? JSON.parse(text) : text;
        return obj;
    } catch (err) {
        return responseData;
    }
}
