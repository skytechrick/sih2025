import OpenAI from "openai";
import { config } from "dotenv";
config({
    quiet: true,
});

const client = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY
});


export async function getFarmInsight(userInput, modelOutput) {
    const response = await client.chat.completions.create({
        model: "gpt-4.1-mini",
        messages: [
            {
                role: "system",
                content: `
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
                    `,
            },
            {
                role: "user",
                content: `Here is the user input: \n${JSON.stringify(userInput, null, 2)}\n\nHere is the model output: \n${JSON.stringify(modelOutput, null, 2)}`
            }
        ]
    });

    return response.choices[0].message.content;
}