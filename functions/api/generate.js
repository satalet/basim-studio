export async function onRequestPost(context) {
  try {
    const { request, env } = context;
    const apiKey = env.GEMINI_API_KEY;

    if (!apiKey) {
      return new Response(JSON.stringify({ error: "مفتاح API غير معرف في إعدادات Cloudflare" }), {
        status: 500,
        headers: { "Content-Type": "application/json" }
      });
    }

    const body = await request.json();
    const promptText = body.prompt || "";

    const systemInstruction = `أنت رسام كرتون رقمي متخصص للأطفال ومحترف في تحويل أفكار الشخصيات إلى خطوط SVG بيضاء وسوداء نظيفة جداً كصفحات كتب التلوين (Coloring Book Line Art).
المطلوب منك: رسم شخصية كرتونية مبسطة بناءً على الفكرة، بخطوط خارجية سوداء عريضة ومغلقة تماماً (Closed paths) بدون أي تظليل أو ألوان داخلية، وبأشكال هندسية واضحة ليسهل تلوينها.
يجب أن ترجع فقط كود <svg viewBox="0 0 500 500" ...>...</svg> نقي داخل وسم svg بدون نصوص إضافية أو markdown. استخدم stroke="black" و stroke-width="4" و fill="white".`;

    const geminiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${apiKey}`;

    const geminiResponse = await fetch(geminiUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [
          {
            parts: [
              { text: `${systemInstruction}\n\nفكرة الشخصية: ${promptText}` }
            ]
          }
        ]
      })
    });

    const data = await geminiResponse.json();
    const rawText = data?.candidates?.[0]?.content?.parts?.[0]?.text || "";

    // استخراج كود الـ SVG
    const svgMatch = rawText.match(/<svg[\s\S]*?<\/svg>/i);
    const svgCode = svgMatch ? svgMatch[0] : null;

    if (!svgCode) {
      return new Response(JSON.stringify({ error: "لم يتمكن النموذج من توليد كود SVG صالح" }), {
        status: 400,
        headers: { "Content-Type": "application/json" }
      });
    }

    return new Response(JSON.stringify({ svg: svgCode }), {
      headers: { "Content-Type": "application/json" }
    });

  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), {
      status: 500,
      headers: { "Content-Type": "application/json" }
    });
  }
}
