(function () {
    const widget = document.querySelector(".chat-widget");
    if (!widget) return;

    const panel = widget.querySelector(".chat-panel");
    const toggle = widget.querySelector(".chat-toggle");
    const close = widget.querySelector(".chat-close");
    const form = widget.querySelector(".chat-form");
    const input = form.querySelector("input[name='message']");
    const messages = widget.querySelector(".chat-messages");
    const csrf = form.querySelector("input[name='csrfmiddlewaretoken']").value;
    const chatUrl = widget.dataset.chatUrl;

    function addMessage(text, type) {
        const item = document.createElement("div");
        item.className = `chat-message ${type}`;
        item.textContent = text;
        messages.appendChild(item);
        messages.scrollTop = messages.scrollHeight;
    }

    function addProducts(products) {
        if (!products || products.length === 0) return;
        const wrap = document.createElement("div");
        wrap.className = "chat-products";
        products.forEach((product) => {
            const button = document.createElement("button");
            button.className = "chat-product";
            button.type = "button";
            button.innerHTML = `<strong>${product.name}</strong><br><span>${product.price} сум / ${product.unit}, ${product.city}</span>`;
            button.addEventListener("click", () => sendMessage("", product.id));
            wrap.appendChild(button);
        });
        messages.appendChild(wrap);
        messages.scrollTop = messages.scrollHeight;
    }

    async function sendMessage(text, productId) {
        const body = new URLSearchParams();
        if (text) body.append("message", text);
        if (productId) body.append("product_id", productId);
        const response = await fetch(chatUrl, {
            method: "POST",
            headers: {"X-CSRFToken": csrf, "Content-Type": "application/x-www-form-urlencoded"},
            body,
        });
        const data = await response.json();
        addMessage(data.reply, "bot");
        addProducts(data.products);
    }

    toggle.addEventListener("click", () => {
        panel.hidden = false;
        toggle.hidden = true;
        input.focus();
    });

    close.addEventListener("click", () => {
        panel.hidden = true;
        toggle.hidden = false;
    });

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const text = input.value.trim();
        if (!text) return;
        addMessage(text, "user");
        input.value = "";
        try {
            await sendMessage(text);
        } catch (error) {
            addMessage("Не получилось отправить сообщение. Попробуйте ещё раз.", "bot");
        }
    });
})();
