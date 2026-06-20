(function () {
  "use strict";

  var body = document.body;
  if (!body.classList.contains("reader-enabled")) return;

  var ch = body.dataset.ch || "00";
  var storeKey = "ielts-reader-v1";
  var state = loadState();

  var toolbar = document.querySelector(".reader-toolbar");
  var parts = Array.from(document.querySelectorAll(".story-part"));

  initMode();
  initParts();
  initBlocks();
  updatePartProgress();

  function loadState() {
    try {
      var all = JSON.parse(localStorage.getItem(storeKey) || "{}");
      return all[ch] || { mode: "both", openPart: 0, done: [], blocks: {} };
    } catch (e) {
      return { mode: "both", openPart: 0, done: [], blocks: {} };
    }
  }

  function saveState() {
    try {
      var all = JSON.parse(localStorage.getItem(storeKey) || "{}");
      all[ch] = state;
      localStorage.setItem(storeKey, JSON.stringify(all));
    } catch (e) {
      /* ignore quota errors */
    }
  }

  function initMode() {
    applyMode(state.mode || "both");
    if (!toolbar) return;
    toolbar.addEventListener("click", function (e) {
      var btn = e.target.closest("[data-mode]");
      if (!btn) return;
      state.mode = btn.dataset.mode;
      applyMode(state.mode);
      saveState();
    });
  }

  function applyMode(mode) {
    body.dataset.readMode = mode;
    if (toolbar) {
      toolbar.querySelectorAll("[data-mode]").forEach(function (btn) {
        btn.classList.toggle("is-active", btn.dataset.mode === mode);
      });
    }
    refreshZhVisibility();
  }

  function initParts() {
    parts.forEach(function (part, idx) {
      var toggle = part.querySelector(".part-toggle");
      var markBtn = part.querySelector(".part-mark");

      if (state.done.indexOf(idx) !== -1) {
        part.classList.add("is-done");
      }

      var open = state.openPart === idx;
      part.classList.toggle("is-open", open);
      if (toggle) toggle.setAttribute("aria-expanded", open ? "true" : "false");

      if (toggle) {
        toggle.addEventListener("click", function () {
          openPart(idx);
        });
      }
      if (markBtn) {
        markBtn.addEventListener("click", function (e) {
          e.stopPropagation();
          toggleDone(idx);
        });
      }
    });

    if (parts.length && state.openPart >= parts.length) {
      openPart(0);
    }
  }

  function openPart(idx) {
    state.openPart = idx;
    parts.forEach(function (part, i) {
      var isOpen = i === idx;
      part.classList.toggle("is-open", isOpen);
      var toggle = part.querySelector(".part-toggle");
      if (toggle) toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
    });
    saveState();
    var openEl = parts[idx];
    if (openEl) openEl.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function toggleDone(idx) {
    var i = state.done.indexOf(idx);
    if (i === -1) state.done.push(idx);
    else state.done.splice(i, 1);
    state.done.sort(function (a, b) {
      return a - b;
    });
    parts[idx].classList.toggle("is-done", i === -1);
    updatePartProgress();
    saveState();
  }

  function updatePartProgress() {
    var el = document.querySelector(".part-progress-text");
    if (!el) return;
    var done = state.done.length;
    var total = parts.length;
    el.textContent = done + " / " + total + " Parts 已读完";
  }

  function initBlocks() {
    document.querySelectorAll(".block").forEach(function (block) {
      var id = block.dataset.blockId;
      var sents = Array.from(block.querySelectorAll(".sent"));
      if (!sents.length) return;

      var saved = state.blocks[id];
      if (typeof saved === "number" && saved > 0) {
        revealThrough(sents, saved);
      }
      updateBlockUI(block, sents);

      var btn = block.querySelector(".btn-next");
      if (btn) {
        btn.addEventListener("click", function () {
          var next = block.querySelector(".sent.is-pending");
          if (!next) return;
          next.classList.remove("is-pending");
          next.classList.add("is-visible");
          var visible = block.querySelectorAll(".sent.is-visible").length;
          state.blocks[id] = visible - 1;
          saveState();
          updateBlockUI(block, sents);
        });
      }
    });
  }

  function revealThrough(sents, lastIdx) {
    sents.forEach(function (sent, i) {
      if (i <= lastIdx) {
        sent.classList.remove("is-pending");
        sent.classList.add("is-visible");
      }
    });
  }

  function updateBlockUI(block, sents) {
    var visible = block.querySelectorAll(".sent.is-visible").length;
    var total = sents.length;
    var pending = block.querySelector(".sent.is-pending");
    var complete = !pending;

    block.classList.toggle("block-complete", complete);

    var prog = block.querySelector(".sent-progress");
    if (prog) prog.textContent = visible + " / " + total + " 句";

    var btn = block.querySelector(".btn-next");
    if (btn) {
      btn.disabled = complete;
      btn.textContent = complete ? "本段读完 ✓" : "下一句 →";
    }

    refreshZhVisibility();
  }

  function refreshZhVisibility() {
    document.querySelectorAll(".block").forEach(function (block) {
      var zh = block.querySelector(".zh");
      if (!zh) return;
      var show =
        body.dataset.readMode !== "en" && block.classList.contains("block-complete");
      zh.hidden = !show;
    });
  }
})();
