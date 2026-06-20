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

  function visibleCount(sents) {
    var n = 0;
    sents.forEach(function (sent) {
      if (!sent.hidden) n += 1;
    });
    return n;
  }

  function initBlocks() {
    document.querySelectorAll(".block").forEach(function (block) {
      var id = block.dataset.blockId;
      var sents = Array.from(block.querySelectorAll("p.en > .sent"));
      if (!sents.length) return;

      var saved = state.blocks[id];
      if (typeof saved === "number" && saved >= 0) {
        revealThrough(sents, saved);
      } else {
        sents.forEach(function (sent, i) {
          sent.hidden = i !== 0;
        });
      }

      updateBlockUI(block, sents);

      var btn = block.querySelector(".btn-next");
      if (btn) {
        btn.addEventListener("click", function () {
          var next = null;
          sents.forEach(function (sent) {
            if (!next && sent.hidden) next = sent;
          });
          if (!next) return;
          next.hidden = false;
          state.blocks[id] = visibleCount(sents) - 1;
          saveState();
          updateBlockUI(block, sents);
        });
      }
    });
  }

  function revealThrough(sents, lastIdx) {
    sents.forEach(function (sent, i) {
      sent.hidden = i > lastIdx;
    });
  }

  function updateBlockUI(block, sents) {
    var visible = visibleCount(sents);
    var total = sents.length;
    var complete = visible >= total;

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
    var mode = body.dataset.readMode || "both";
    document.querySelectorAll(".block .zh").forEach(function (zh) {
      zh.hidden = mode !== "both";
    });
  }
})();
