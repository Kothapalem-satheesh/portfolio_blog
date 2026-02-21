document.addEventListener("DOMContentLoaded", () => {
  /* ── Build DOM ───────────────────────────────────── */
  const launcher = document.createElement("button");
  launcher.className = "chat-launcher";
  launcher.type = "button";
  launcher.setAttribute("aria-label", "Open AI assistant");
  launcher.innerHTML = "🤖";

  const panel = document.createElement("div");
  panel.className = "chat-panel";
  panel.innerHTML = `
    <div class="chat-header">
      <span class="chat-dot"></span>
      <strong>Portfolio AI Assistant</strong>
    </div>
    <div class="chat-log" id="chat-log"></div>
    <form class="chat-form" id="chat-form" autocomplete="off">
      <input type="text" id="chat-input" placeholder="Ask about projects, skills, or AI..." />
      <button class="btn" type="submit">Send</button>
    </form>
  `;

  document.body.appendChild(panel);
  document.body.appendChild(launcher);

  const log   = panel.querySelector("#chat-log");
  const form  = panel.querySelector("#chat-form");
  const input = panel.querySelector("#chat-input");

  /* ── Toggle ─────────────────────────────────────── */
  launcher.addEventListener("click", () => {
    const open = panel.classList.toggle("open");
    if (open && log.children.length === 0) {
      addMsg("Hi! I'm Satheesh's AI assistant. Ask me about his skills, projects, or experience.", "bot");
    }
    if (open) setTimeout(() => input.focus(), 120);
  });

  /* ── Message helper ─────────────────────────────── */
  function addMsg(text, role) {
    const row = document.createElement("div");
    row.className = `chat-row ${role}`;
    row.textContent = text;
    log.appendChild(row);
    log.scrollTop = log.scrollHeight;
    return row;
  }

  /* ── Submit ─────────────────────────────────────── */
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const message = input.value.trim();
    if (!message) return;

    addMsg(message, "user");
    input.value = "";
    input.disabled = true;

    const thinking = addMsg("Thinking…", "bot typing");

    try {
      const res  = await fetch("/chatbot/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });

      let data = {};
      try { data = await res.json(); } catch { data = { error: "Invalid response." }; }

      thinking.remove();
      addMsg(data.reply || data.error || "No response.", "bot");
    } catch {
      thinking.remove();
      addMsg("Network error. Please try again.", "bot");
    } finally {
      input.disabled = false;
      input.focus();
    }
  });
});
