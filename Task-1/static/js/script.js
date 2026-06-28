/**
 * AI Language Translator — Frontend Logic
 * ========================================
 * Handles translation API calls, clipboard, Web Speech API TTS,
 * history sidebar, theme toggling, character counter, and keyboard shortcuts.
 */

(() => {
    "use strict";

    // ------------------------------------------------------------------ //
    // DOM References                                                      //
    // ------------------------------------------------------------------ //
    const $ = (sel) => document.querySelector(sel);
    const $$ = (sel) => document.querySelectorAll(sel);

    const sourceText     = $("#source-text");
    const outputText     = $("#output-text");
    const sourceLang     = $("#source-lang");
    const targetLang     = $("#target-lang");
    const translateBtn   = $("#translate-btn");
    const clearBtn       = $("#clear-btn");
    const copyBtn        = $("#copy-btn");
    const speakBtn       = $("#speak-btn");
    const swapBtn        = $("#swap-btn");
    const charCounter    = $("#char-counter");
    const detectedBadge  = $("#detected-badge");
    const detectedLang   = $("#detected-lang");
    const statsRow       = $("#stats-row");
    const statTime       = $("#stat-time");
    const statChars      = $("#stat-chars");
    const loadingOverlay = $("#loading-overlay");
    const themeToggle    = $("#theme-toggle");
    const themeIcon      = $("#theme-icon");
    const historyToggle  = $("#history-toggle");
    const historySidebar = $("#history-sidebar");
    const sidebarClose   = $("#sidebar-close");
    const sidebarOverlay = $("#sidebar-overlay");
    const historyList    = $("#history-list");
    const historyEmpty   = $("#history-empty");
    const historyBadge   = $("#history-badge");
    const clearHistoryBtn = $("#clear-history-btn");
    const toastContainer = $("#toast-container");

    const MAX_CHARS = 5000;

    // ------------------------------------------------------------------ //
    // State                                                               //
    // ------------------------------------------------------------------ //
    let currentTranslation = "";
    let currentTargetLang  = "";
    let isSpeaking         = false;
    let serverAudio        = null;

    // ------------------------------------------------------------------ //
    // Init                                                                //
    // ------------------------------------------------------------------ //
    function init() {
        loadTheme();
        loadHistory();
        bindEvents();
        updateCharCounter();
    }

    // ------------------------------------------------------------------ //
    // Event Binding                                                       //
    // ------------------------------------------------------------------ //
    function bindEvents() {
        translateBtn.addEventListener("click", translateText);
        clearBtn.addEventListener("click", clearInput);
        copyBtn.addEventListener("click", copyToClipboard);
        speakBtn.addEventListener("click", speakText);
        swapBtn.addEventListener("click", swapLanguages);
        sourceText.addEventListener("input", updateCharCounter);
        themeToggle.addEventListener("click", toggleTheme);
        historyToggle.addEventListener("click", openHistory);
        sidebarClose.addEventListener("click", closeHistory);
        sidebarOverlay.addEventListener("click", closeHistory);
        clearHistoryBtn.addEventListener("click", clearAllHistory);

        // Keyboard shortcut: Ctrl+Enter to translate
        document.addEventListener("keydown", (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
                e.preventDefault();
                translateText();
            }
            // Escape to close sidebar
            if (e.key === "Escape") {
                closeHistory();
            }
        });
    }

    // ------------------------------------------------------------------ //
    // Translation                                                         //
    // ------------------------------------------------------------------ //
    function stopSpeaking() {
        if (isSpeaking) {
            if ("speechSynthesis" in window) {
                window.speechSynthesis.cancel();
            }
            if (serverAudio) {
                serverAudio.pause();
                serverAudio = null;
            }
            isSpeaking = false;
            speakBtn.querySelector(".btn-icon").textContent = "🔊";
        }
    }

    async function translateText() {
        const text = sourceText.value.trim();
        if (!text) {
            showToast("⚠️ Please enter text to translate.", "error");
            sourceText.focus();
            return;
        }

        const source = sourceLang.value;
        const target = targetLang.value;

        stopSpeaking();
        showLoading(true);
        translateBtn.disabled = true;
        clearBtn.disabled = true;
        swapBtn.disabled = true;
        sourceText.disabled = true;

        try {
            const res = await fetch("/translate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text, source, target }),
            });

            const data = await res.json();

            if (data.success) {
                // Display translation
                currentTranslation = data.translated_text;
                currentTargetLang  = data.target_language;
                outputText.textContent = data.translated_text;
                outputText.classList.add("fade-in-up");
                setTimeout(() => outputText.classList.remove("fade-in-up"), 500);

                // Enable action buttons
                copyBtn.disabled  = false;
                speakBtn.disabled = false;

                // Detected language badge
                if (data.detected_language) {
                    detectedLang.textContent = data.detected_language;
                    detectedBadge.style.display = "inline-flex";
                } else {
                    detectedBadge.style.display = "none";
                }

                // Stats
                const timeClass = data.elapsed_ms < 2000 ? "stat-badge success" : "stat-badge error";
                statTime.className = timeClass;
                statTime.textContent = `⚡ ${Math.round(data.elapsed_ms)} ms`;
                statChars.textContent = `📊 ${text.length.toLocaleString()} chars`;
                statsRow.style.display = "flex";

                showToast("✅ Translation complete!", "success");
                loadHistory(); // Refresh history badge
            } else {
                showToast(`❌ ${data.error || data.error_message || "Translation failed."}`, "error");
            }
        } catch (err) {
            showToast("❌ Network error. Please check your connection.", "error");
            console.error("Translation error:", err);
        } finally {
            showLoading(false);
            translateBtn.disabled = false;
            clearBtn.disabled = false;
            swapBtn.disabled = false;
            sourceText.disabled = false;
            sourceText.focus();
        }
    }

    // ------------------------------------------------------------------ //
    // Clear                                                               //
    // ------------------------------------------------------------------ //
    function clearInput() {
        stopSpeaking();
        sourceText.value = "";
        outputText.innerHTML = '<span class="placeholder-text">Translation will appear here…</span>';
        currentTranslation = "";
        copyBtn.disabled  = true;
        speakBtn.disabled = true;
        detectedBadge.style.display = "none";
        statsRow.style.display = "none";
        updateCharCounter();
        sourceText.focus();
    }

    // ------------------------------------------------------------------ //
    // Copy to Clipboard                                                   //
    // ------------------------------------------------------------------ //
    async function copyToClipboard() {
        if (!currentTranslation) return;

        try {
            await navigator.clipboard.writeText(currentTranslation);
            showToast("📋 Copied to clipboard!", "success");
        } catch {
            // Fallback: select text
            const range = document.createRange();
            range.selectNodeContents(outputText);
            const sel = window.getSelection();
            sel.removeAllRanges();
            sel.addRange(range);
            showToast("💡 Text selected — press Ctrl+C to copy.", "info");
        }
    }

    // ------------------------------------------------------------------ //
    // Text-to-Speech (Web Speech API + server fallback)                   //
    // ------------------------------------------------------------------ //
    function speakText() {
        if (!currentTranslation) return;

        // Stop if already speaking
        if (isSpeaking) {
            stopSpeaking();
            return;
        }

        // Try Web Speech API first
        if ("speechSynthesis" in window) {
            const utterance = new SpeechSynthesisUtterance(currentTranslation);

            // Try to find a matching voice
            const voices = window.speechSynthesis.getVoices();
            const langCode = getLangCode(currentTargetLang);
            
            // Set lang so standard fallback matches correctly
            utterance.lang = langCode;

            const matchVoice = voices.find(v => {
                const voiceLang = v.lang.toLowerCase().replace("_", "-");
                const targetLangCode = langCode.toLowerCase().replace("_", "-");
                return voiceLang.startsWith(targetLangCode) || targetLangCode.startsWith(voiceLang);
            });
            if (matchVoice) utterance.voice = matchVoice;

            utterance.rate = 1.0;
            utterance.onstart = () => {
                isSpeaking = true;
                speakBtn.querySelector(".btn-icon").textContent = "⏹️";
            };
            utterance.onend = () => {
                isSpeaking = false;
                speakBtn.querySelector(".btn-icon").textContent = "🔊";
            };
            utterance.onerror = () => {
                isSpeaking = false;
                speakBtn.querySelector(".btn-icon").textContent = "🔊";
                // Fallback to server-side TTS
                speakViaServer();
            };

            window.speechSynthesis.cancel();
            window.speechSynthesis.speak(utterance);
        } else {
            speakViaServer();
        }
    }

    async function speakViaServer() {
        try {
            showToast("🔊 Generating audio…", "info");
            const res = await fetch("/tts", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    text: currentTranslation,
                    lang: currentTargetLang,
                    slow: false,
                }),
            });

            if (!res.ok) {
                const errData = await res.json().catch(() => ({}));
                throw new Error(errData.error || "Text-to-speech is unavailable.");
            }

            const blob = await res.blob();
            const url = URL.createObjectURL(blob);

            if (serverAudio) {
                serverAudio.pause();
            }

            serverAudio = new Audio(url);

            serverAudio.onplay = () => {
                isSpeaking = true;
                speakBtn.querySelector(".btn-icon").textContent = "⏹️";
            };

            serverAudio.onended = () => {
                isSpeaking = false;
                speakBtn.querySelector(".btn-icon").textContent = "🔊";
                URL.revokeObjectURL(url);
                serverAudio = null;
            };

            serverAudio.onerror = () => {
                isSpeaking = false;
                speakBtn.querySelector(".btn-icon").textContent = "🔊";
                URL.revokeObjectURL(url);
                serverAudio = null;
                showToast("❌ Failed to play audio.", "error");
            };

            await serverAudio.play();
        } catch (err) {
            showToast(`❌ ${err.message}`, "error");
        }
    }

    // Map display name to ISO code for Web Speech API voice matching
    function getLangCode(langName) {
        if (!window.__langMap) {
            const appData = document.getElementById("app-data");
            try {
                window.__langMap = appData ? JSON.parse(appData.getAttribute("data-languages")) : {};
            } catch (e) {
                window.__langMap = {};
            }
        }
        return window.__langMap[langName] || "en";
    }

    // Ensure voices are loaded
    if ("speechSynthesis" in window) {
        window.speechSynthesis.onvoiceschanged = () => {
            window.speechSynthesis.getVoices();
        };
    }

    // ------------------------------------------------------------------ //
    // Swap Languages                                                      //
    // ------------------------------------------------------------------ //
    function swapLanguages() {
        const src = sourceLang.value;
        const tgt = targetLang.value;

        if (src === "Auto-Detect") {
            showToast("⚠️ Can't swap when source is Auto-Detect.", "error");
            return;
        }

        stopSpeaking();

        sourceLang.value = tgt;
        targetLang.value = src;
        currentTargetLang = src; // Update the voice target language

        // Also swap text content if there's a translation
        if (currentTranslation && sourceText.value.trim()) {
            const oldSource = sourceText.value;
            sourceText.value = currentTranslation;
            outputText.textContent = oldSource;
            currentTranslation = oldSource;
            updateCharCounter();
        }

        // Rotate animation
        swapBtn.style.transform = "rotate(180deg)";
        setTimeout(() => { swapBtn.style.transform = ""; }, 350);

        showToast("🔄 Languages swapped!", "info");
    }

    // ------------------------------------------------------------------ //
    // Character Counter                                                   //
    // ------------------------------------------------------------------ //
    function updateCharCounter() {
        const len = sourceText.value.length;
        charCounter.textContent = `${len.toLocaleString()} / ${MAX_CHARS.toLocaleString()}`;

        const ratio = len / MAX_CHARS;
        charCounter.classList.remove("warning", "danger");
        if (ratio > 0.9) charCounter.classList.add("danger");
        else if (ratio > 0.75) charCounter.classList.add("warning");

        // Clear output if input is cleared manually
        if (len === 0) {
            outputText.innerHTML = '<span class="placeholder-text">Translation will appear here…</span>';
            currentTranslation = "";
            copyBtn.disabled  = true;
            speakBtn.disabled = true;
            detectedBadge.style.display = "none";
            statsRow.style.display = "none";
            stopSpeaking();
        }
    }

    // ------------------------------------------------------------------ //
    // History                                                             //
    // ------------------------------------------------------------------ //
    async function loadHistory() {
        try {
            const res = await fetch("/history?limit=30");
            if (!res.ok) throw new Error("History fetch failed");
            const data = await res.json();
            const entries = data.history || [];

            historyBadge.textContent = entries.length;

            if (entries.length === 0) {
                historyEmpty.style.display = "block";
                return;
            }

            historyEmpty.style.display = "none";

            // Clear existing items (keep the empty message)
            historyList.querySelectorAll(".history-item").forEach(el => el.remove());

            entries.forEach((entry) => {
                const item = document.createElement("div");
                item.className = "history-item";
                item.innerHTML = `
                    <div class="history-meta">
                        <span class="history-langs">${escapeHtml(entry.source_language)} → ${escapeHtml(entry.target_language)}</span>
                        <span class="history-time">${escapeHtml(entry.created_at || "")}</span>
                    </div>
                    <div class="history-source-text">${escapeHtml(truncate(entry.source_text, 60))}</div>
                    <div class="history-translated-text">${escapeHtml(truncate(entry.translated_text, 60))}</div>
                `;
                item.addEventListener("click", () => reuseTranslation(entry));
                historyList.appendChild(item);
            });
        } catch (err) {
            console.error("Failed to load history:", err);
        }
    }

    function reuseTranslation(entry) {
        stopSpeaking();
        sourceText.value = entry.source_text;

        // Set languages if available in dropdowns
        if (entry.source_language && entry.source_language !== "Auto-Detect") {
            sourceLang.value = entry.source_language;
        }
        targetLang.value = entry.target_language;

        // Show previous translation
        outputText.textContent = entry.translated_text;
        currentTranslation = entry.translated_text;
        currentTargetLang  = entry.target_language;
        copyBtn.disabled  = false;
        speakBtn.disabled = false;

        // Hide stale badges
        detectedBadge.style.display = "none";
        statsRow.style.display = "none";

        updateCharCounter();
        closeHistory();
        showToast("♻️ Previous translation loaded.", "info");
    }

    async function clearAllHistory() {
        try {
            const res = await fetch("/history", { method: "DELETE" });
            if (!res.ok) throw new Error("Failed to clear history");
            historyList.querySelectorAll(".history-item").forEach(el => el.remove());
            historyEmpty.style.display = "block";
            historyBadge.textContent = "0";
            showToast("🗑️ History cleared.", "success");
        } catch {
            showToast("❌ Failed to clear history.", "error");
        }
    }

    function openHistory() {
        historySidebar.classList.add("open");
        sidebarOverlay.classList.add("visible");
        loadHistory(); // Refresh on open
    }

    function closeHistory() {
        historySidebar.classList.remove("open");
        sidebarOverlay.classList.remove("visible");
    }

    // ------------------------------------------------------------------ //
    // Theme                                                               //
    // ------------------------------------------------------------------ //
    function toggleTheme() {
        const html = document.documentElement;
        const current = html.getAttribute("data-theme");
        const next = current === "dark" ? "light" : "dark";
        html.setAttribute("data-theme", next);
        themeIcon.textContent = next === "dark" ? "🌙" : "☀️";
        localStorage.setItem("theme", next);
    }

    function loadTheme() {
        const saved = localStorage.getItem("theme") || "dark";
        document.documentElement.setAttribute("data-theme", saved);
        themeIcon.textContent = saved === "dark" ? "🌙" : "☀️";
    }

    // ------------------------------------------------------------------ //
    // Loading Overlay                                                     //
    // ------------------------------------------------------------------ //
    function showLoading(visible) {
        if (visible) {
            loadingOverlay.classList.add("visible");
        } else {
            loadingOverlay.classList.remove("visible");
        }
    }

    // ------------------------------------------------------------------ //
    // Toast                                                               //
    // ------------------------------------------------------------------ //
    function showToast(message, type = "info") {
        const toast = document.createElement("div");
        toast.className = `toast ${type}`;
        toast.textContent = message;
        toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.classList.add("fade-out");
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    // ------------------------------------------------------------------ //
    // Helpers                                                             //
    // ------------------------------------------------------------------ //
    function escapeHtml(str) {
        const div = document.createElement("div");
        div.textContent = str;
        return div.innerHTML;
    }

    function truncate(str, max) {
        if (!str) return "";
        return str.length <= max ? str : str.substring(0, max - 1) + "…";
    }

    // ------------------------------------------------------------------ //
    // Boot                                                                //
    // ------------------------------------------------------------------ //
    document.addEventListener("DOMContentLoaded", init);

})();
