const fetch = require("node-fetch");

exports.handler = async (event, context) => {
  const MAILERLITE_API_KEY = process.env.MAILERLITE_API_KEY;
  const BLOG_URL = "https://matt1085-affiliate.netlify.app";
  const MAILER_GROUP_ID = 12345678; // replace with numeric ID from get_group_id.py

  const post = {
    title: "Test Post",
    content: "This is a test post content for email summary.",
    slug: "test-post"
  };

  // Call Ollama AI for summary
  let summary = post.content.substring(0, 200); // fallback
  try {
    const aiResp = await fetch("http://localhost:11434/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: "llama3:8b",
        prompt: `Write a short, engaging email summary for:\n\n${post.content}`
      })
    });
    const data = await aiResp.json();
    if (Array.isArray(data)) {
      summary = data.map(c => c.response || "").join(" ");
    } else if (data.response) {
      summary = data.response;
    }
  } catch (err) {
    console.log("[!] AI summary fallback:", err);
  }

  // Send email via MailerLite
  try {
    const mlResp = await fetch("https://api.mailerlite.com/api/v2/campaigns", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${MAILERLITE_API_KEY}`
      },
      body: JSON.stringify({
        subject: `New Blog Post: ${post.title}`,
        from: { email: "noreply@matt1085-affiliate.netlify.app", name: "Affiliate Blog" },
        groups: [MAILER_GROUP_ID],
        html: `<p>${summary}</p><p>Read more: <a href='${BLOG_URL}/${post.slug}'>Click here</a></p>`,
        type: "regular"
      })
    });
    const result = await mlResp.json();
    return { statusCode: 200, body: JSON.stringify(result) };
  } catch (err) {
    return { statusCode: 500, body: `Error sending email: ${err}` };
  }
};

