(function () {
  "use strict";

  var body = document.body;
  if (!body.classList.contains("reader-enabled")) return;

  var ch = body.dataset.ch || "00";
  var storeKey = "ielts-reader-v2";
  var state = loadState();

  ensureToolbar();
  var toolbar = document.querySelector(".reader-toolbar");
  var parts = Array.from(document.querySelectorAll(".story-part"));

  initToolbar();
  initParts();
  initBlocks();
  updatePartProgress();

  function ensureToolbar() {
    if (document.querySelector(".reader-toolbar")) return;
    var article = document.querySelector(".story-body");
    if (!article) return;
    var bar = document.createElement("div");
    bar.className = "reader-toolbar";
    bar.setAttribute("role", "toolbar");
    bar.setAttribute("aria-label", "阅读模式");
    bar.innerHTML =
      '<span class="reader-label">阅读</span>' +
      '<button type="button" class="reader-btn reader-toggle" data-toggle="zh" aria-pressed="false">显示中文</button>' +
      '<button type="button" class="reader-btn reader-toggle" data-toggle="focus" aria-pressed="false">只高亮生词</button>' +
      '<button type="button" class="reader-btn reader-toggle" data-toggle="all" aria-pressed="false">显示全部</button>' +
      '<span class="part-progress-text">0 / 0 Parts 已读完</span>';
    var anchor = article.querySelector("h2");
    if (anchor && anchor.nextSibling) {
      article.insertBefore(bar, anchor.nextSibling);
    } else {
      article.appendChild(bar);
    }
  }

  function loadState() {
    var base = {
      showZh: false,
      focus: false,
      showAll: false,
      openPart: 0,
      done: [],
      blocks: {},
    };
    try {
      var all = JSON.parse(localStorage.getItem(storeKey) || "{}");
      if (all[ch]) return Object.assign(base, all[ch]);
      var legacy = JSON.parse(localStorage.getItem("ielts-reader-v1") || "{}");
      if (legacy[ch]) {
        var old = legacy[ch];
        base.showZh = old.mode === "both";
        base.focus = old.mode === "focus";
        base.openPart = old.openPart || 0;
        base.done = old.done || [];
        base.blocks = old.blocks || {};
      }
    } catch (e) {
      /* ignore */
    }
    return base;
  }

  function saveState() {
    try {
      var all = JSON.parse(localStorage.getItem(storeKey) || "{}");
      all[ch] = state;
      localStorage.setItem(storeKey, JSON.stringify(all));
    } catch (e) {
      /* ignore */
    }
  }

  function initToolbar() {
    applySettings();
    if (state.showAll) applyShowAllMode();
    if (!toolbar) return;
    toolbar.addEventListener("click", function (e) {
      var btn = e.target.closest("[data-toggle]");
      if (!btn) return;
      var key = btn.dataset.toggle;
      if (key === "zh") state.showZh = !state.showZh;
      if (key === "focus") state.focus = !state.focus;
      if (key === "all") state.showAll = !state.showAll;
      applySettings();
      if (key === "all") applyShowAllMode();
      else syncAllZh();
      saveState();
    });
  }

  function applySettings() {
    body.classList.toggle("zh-on", !!state.showZh);
    body.classList.toggle("focus-on", !!state.focus);
    body.classList.toggle("show-all-on", !!state.showAll);
    if (!toolbar) return;
    toolbar.querySelectorAll("[data-toggle]").forEach(function (btn) {
      var key = btn.dataset.toggle;
      var on = false;
      if (key === "zh") on = state.showZh;
      if (key === "focus") on = state.focus;
      if (key === "all") on = state.showAll;
      btn.classList.toggle("is-active", on);
      btn.setAttribute("aria-pressed", on ? "true" : "false");
    });
  }

  function applyPartExpansion() {
    parts.forEach(function (part, i) {
      var open = state.showAll || i === state.openPart;
      part.classList.toggle("is-open", open);
      var toggle = part.querySelector(".part-toggle");
      if (toggle) toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  function applyShowAllMode() {
    applyPartExpansion();
    document.querySelectorAll(".block").forEach(function (block) {
      var sents = Array.from(block.querySelectorAll("p.en > .sent"));
      if (!sents.length) return;
      if (state.showAll) {
        sents.forEach(function (sent) {
          sent.hidden = false;
        });
      } else {
        restoreBlockSentences(block, sents);
      }
      updateBlockUI(block, sents);
    });
    saveState();
  }

  function restoreBlockSentences(block, sents) {
    var id = block.dataset.blockId;
    var saved = state.blocks[id];
    if (typeof saved === "number" && saved >= 0) {
      revealThrough(sents, saved);
    } else {
      sents.forEach(function (sent, i) {
        sent.hidden = i !== 0;
      });
    }
  }

  function initParts() {
    parts.forEach(function (part, idx) {
      var toggle = part.querySelector(".part-toggle");
      var markBtn = part.querySelector(".part-mark");

      if (state.done.indexOf(idx) !== -1) {
        part.classList.add("is-done");
      }

      if (toggle) {
        toggle.addEventListener("click", function () {
          if (state.showAll) return;
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

    applyPartExpansion();
    if (parts.length && state.openPart >= parts.length) {
      state.openPart = 0;
      applyPartExpansion();
    }
  }

  function openPart(idx) {
    state.openPart = idx;
    applyPartExpansion();
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
    el.textContent = state.done.length + " / " + parts.length + " Parts 已读完";
  }

  function visibleCount(sents) {
    var n = 0;
    sents.forEach(function (sent) {
      if (!sent.hidden) n += 1;
    });
    return n;
  }

  function zhCountForEn(enVisible, enTotal, zhTotal) {
    if (!state.showZh || !zhTotal || !enVisible) return 0;
    if (enVisible >= enTotal) return zhTotal;
    return Math.max(1, Math.ceil((enVisible * zhTotal) / enTotal));
  }

  function syncZh(block, enVisible) {
    var zhPara = block.querySelector(".zh");
    var zhSents = Array.from(block.querySelectorAll(".sent-zh"));
    if (!zhPara || !zhSents.length) return;

    if (!state.showZh) {
      zhPara.hidden = true;
      zhSents.forEach(function (z) {
        z.hidden = true;
      });
      return;
    }

    zhPara.hidden = false;
    var enSents = block.querySelectorAll("p.en > .sent");
    var enTotal = enSents.length;
    var showN =
      state.showAll || enVisible >= enTotal
        ? zhSents.length
        : zhCountForEn(enVisible, enTotal, zhSents.length);
    zhSents.forEach(function (z, i) {
      z.hidden = i >= showN;
    });
  }

  function syncAllZh() {
    document.querySelectorAll(".block").forEach(function (block) {
      var sents = block.querySelectorAll("p.en > .sent");
      syncZh(block, visibleCount(Array.from(sents)));
    });
  }

  function initBlocks() {
    document.querySelectorAll(".block").forEach(function (block) {
      var id = block.dataset.blockId;
      var sents = Array.from(block.querySelectorAll("p.en > .sent"));
      if (!sents.length) return;

      if (state.showAll) {
        sents.forEach(function (sent) {
          sent.hidden = false;
        });
      } else {
        restoreBlockSentences(block, sents);
      }

      updateBlockUI(block, sents);

      var btn = block.querySelector(".btn-next");
      if (btn) {
        btn.addEventListener("click", function () {
          if (state.showAll) return;
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
    var total = sents.length;
    var visible = state.showAll ? total : visibleCount(sents);
    var complete = visible >= total;

    block.classList.toggle("block-complete", complete);

    var prog = block.querySelector(".sent-progress");
    if (prog) prog.textContent = visible + " / " + total + " 句";

    var btn = block.querySelector(".btn-next");
    if (btn) {
      if (state.showAll) {
        btn.disabled = true;
        btn.textContent = "已全部显示";
      } else {
        btn.disabled = complete;
        btn.textContent = complete ? "本段读完 ✓" : "下一句 →";
      }
    }

    syncZh(block, visible);
  }
})();
