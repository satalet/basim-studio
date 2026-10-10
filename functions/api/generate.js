export async function onRequestPost(context) {
  try {
    const { request, env } = context;
    const apiKey = env.GEMINI_API_KEY;

    if (!apiKey) {
      return new Response(JSON.stringify({ error: "Missing GEMINI_API_KEY in server environment" }), {
        status: 500,
        headers: { "Content-Type": "application/json" }
      });
    }

    const body = await request.json();
    const prompt = body.prompt;

    if (!prompt) {
      return new Response(JSON.stringify({ error: "Prompt is required" }), {
        status: 400,
        headers: { "Content-Type": "application/json" }
      });
    }

    const systemPrompt = `You are a professional children's cartoon vector line-art artist for a talented artist and animator Basim.
The user wants a clean, cute, coloring-book style character based on: "${prompt}".
CRITICAL REQUIREMENTS:
1. Generate ONLY valid, standalone SVG code starting with <svg viewBox="0 0 500 500" xmlns="http://www.w3.org/2000/svg"> and ending with </svg>.
2. Do NOT wrap in markdown blocks, do not include explanations or extra text.
3. The SVG MUST have pure thick black outlines (stroke="#000000", stroke-width="6" to "10", stroke-linecap="round", stroke-linejoin="round").
4. ALL body parts and shapes MUST have fill="#ffffff" (pure white closed contours) so the kid can use the Flood Fill Bucket tool to color them in!
5. Center the character perfectly in the 500x500 viewport. Ensure bold, expressive cartoon features (large eyes, clear head, body, arms/legs, props).`;

    const models = ["gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.8-flash"];
    let lastError = null;

    for (const model of models) {
      try {
        const geminiUrl = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`;
        const response = await fetch(geminiUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            contents: [{ parts: [{ text: `Generate coloring-book line-art SVG for: "${prompt}"` }] }],
            systemInstruction: { parts: [{ text: systemPrompt }] }
          })
        });

        if (response.ok) {
          const data = await response.json();
          let svgText = data?.candidates?.[0]?.content?.parts?.[0]?.text || "";
          svgText = svgText.replace(/```xml/gi, '').replace(/```svg/gi, '').replace(/```/g, '').trim();

          const svgStart = svgText.indexOf('<svg');
          const svgEnd = svgText.lastIndexOf('</svg>');

          if (svgStart !== -1 && svgEnd !== -1) {
            svgText = svgText.substring(svgStart, svgEnd + 6);
            return new Response(JSON.stringify({ svgText, model }), {
              status: 200,
              headers: { "Content-Type": "application/json" }
            });
          }
        } else {
          lastError = `Model ${model} returned status: ${response.status}`;
        }
      } catch (err) {
        lastError = `Error calling ${model}: ${err.message}`;
      }
    }

    return new Response(JSON.stringify({ error: "All fallback models failed", details: lastError }), {
      status: 502,
      headers: { "Content-Type": "application/json" }
    });

  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), {
      status: 500,
      headers: { "Content-Type": "application/json" }
    });
  }
}
