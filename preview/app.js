/**
 * DESIGN WORK GALLERY — LIVE PREVIEW APPLICATION
 * Logic for dynamic hierarchy, carousel navigation, responsive preview, and copy outputs.
 */

(function () {
  let catalog = null;
  let activeBrand = "RanjeetRaj";
  let activeCategory = "carousel"; // 'carousel' | 'reelCover' | 'post' | 'logo' | 'highlights'
  let activeProject = "";
  let activeSlideIndex = 0;
  let viewportMode = "desktop"; // 'desktop' | 'tablet' | 'mobile'
  let viewMode = "collection"; // 'collection' | 'single' | 'json'
  let sourceMode = "local"; // 'local' | 'jsdelivr'

  const BASE_JSDELIVR_URL = "https://cdn.jsdelivr.net/gh/vanshdigitals/Vanshdigitals-Assets@main/optimized";

  const brandDisplayNames = {
    "Builders-Playground": "Builders Playground",
    "Cuts-and-Curves": "Cuts and Curves",
    "Keshvi-Beauty-Lounge": "Keshvi Beauty Lounge",
    "RanjeetRaj": "Ranjeet Raj",
    "WaterPlane": "WaterPlane"
  };

  const categoryLabels = {
    "carousel": "Carousel",
    "reelCover": "Reel Cover",
    "post": "Post",
    "logo": "Logo",
    "highlights": "Highlights"
  };

  // Helper to format bytes
  function formatBytes(bytes) {
    if (!bytes || bytes <= 0) return "0 KB";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
  }

  // Helper to format project titles
  function formatTitleFromSlug(slug) {
    if (!slug) return "";
    const acronyms = {
      "ai": "AI",
      "chatgpt": "ChatGPT",
      "3d": "3D",
      "partyglam": "PartyGlam",
      "texturevscakey": "TextureVsCakey",
      "bts": "BTS"
    };
    const match = slug.match(/^(RR-\d+|CC-Dark-\d+|CC-Light-\d+|CC-Light-Part2-\d+|WP-\d+|KBL-Carousel-\d+)-(.*)$/i);
    if (match) {
      const prefix = match[1].replace("Part2", "Part 2");
      const rest = match[2];
      const words = rest.split("-").map(w => {
        const low = w.toLowerCase();
        if (acronyms[low]) return acronyms[low];
        if (["and", "vs", "the", "a", "an", "is", "of", "to", "for", "in", "on", "not", "or"].includes(low)) {
          return low;
        } else if (low === "wont") return "Won't";
        else if (low === "isnt") return "Isn't";
        else if (low === "dont") return "Don't";
        else if (/^\d+$/.test(w)) return w;
        return w.charAt(0).toUpperCase() + w.slice(1).toLowerCase();
      });
      return `${prefix} — ${words.join(" ")}`;
    }
    const words = slug.split("-").map(w => acronyms[w.toLowerCase()] || (w.charAt(0).toUpperCase() + w.slice(1).toLowerCase()));
    return words.join(" ");
  }

  // Toast feedback
  function showToast(message) {
    let toast = document.getElementById("toastMsg");
    if (!toast) {
      toast = document.createElement("div");
      toast.id = "toastMsg";
      toast.className = "toast-msg";
      document.body.appendChild(toast);
    }
    toast.innerHTML = `✓ ${message}`;
    toast.classList.add("show");
    clearTimeout(toast._timer);
    toast._timer = setTimeout(() => {
      toast.classList.remove("show");
    }, 2500);
  }

  // Copy to clipboard helper
  function copyText(text, successMsg = "Copied to clipboard!") {
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(() => showToast(successMsg)).catch(() => fallbackCopy(text, successMsg));
    } else {
      fallbackCopy(text, successMsg);
    }
  }

  function fallbackCopy(text, successMsg) {
    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.style.position = "fixed";
    textarea.style.left = "-9999px";
    document.body.appendChild(textarea);
    textarea.select();
    try {
      document.execCommand("copy");
      showToast(successMsg);
    } catch (err) {
      showToast("Could not copy automatically.");
    }
    document.body.removeChild(textarea);
  }

  // Resolve Image URL based on sourceMode
  function getImageUrl(asset) {
    if (!asset || !asset.url) return "";
    if (sourceMode === "local") {
      // url looks like https://cdn.jsdelivr.net/.../optimized/...
      const relPath = asset.url.split("/optimized/")[1];
      return `optimized/${relPath}`;
    }
    return asset.url;
  }

  // Fetch or load manifest data
  async function loadData() {
    try {
      const res = await fetch("design-assets.json?t=" + Date.now());
      if (!res.ok) throw new Error("Network response not ok");
      catalog = await res.json();
    } catch (e) {
      console.warn("Could not fetch design-assets.json via fetch, trying local fallback:", e);
      // Fallback empty catalog
      catalog = {};
    }
    initApp();
  }

  function initApp() {
    setupHeaderEvents();
    setupKeyboardNav();
    setupTouchSwipe();

    const brands = Object.keys(catalog);
    if (brands.length > 0) {
      // Prioritize RanjeetRaj if available
      activeBrand = brands.includes("RanjeetRaj") ? "RanjeetRaj" : brands[0];
      setBrand(activeBrand);
    } else {
      renderEmpty("No assets found in catalog.");
    }
  }

  // Viewport Switcher
  function setupHeaderEvents() {
    document.querySelectorAll(".viewport-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".viewport-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        viewportMode = btn.dataset.viewport;
        const frame = document.getElementById("viewportFrame");
        frame.className = `viewport-frame ${viewportMode}`;
      });
    });

    // Source Toggle
    const sourceToggle = document.getElementById("sourceToggleBtn");
    if (sourceToggle) {
      sourceToggle.addEventListener("click", () => {
        sourceMode = sourceMode === "local" ? "jsdelivr" : "local";
        sourceToggle.innerHTML = sourceMode === "local" ? "⚡ Local Fast Preview" : "🌐 jsDelivr CDN";
        showToast(`Asset Source: ${sourceMode === "local" ? "Local WebP" : "jsDelivr CDN"}`);
        renderContent();
      });
    }

    // View Mode Toggle (Gallery vs JSON Data)
    document.querySelectorAll(".view-mode-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".view-mode-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        viewMode = btn.dataset.mode;
        renderContent();
      });
    });
  }

  function setBrand(brand) {
    activeBrand = brand;
    renderBrandTabs();

    // Determine available categories for this brand
    const bData = catalog[brand] || {};
    const availableCats = [];
    if (bData.carousel && Object.keys(bData.carousel).length > 0) availableCats.push("carousel");
    if (bData.reelCover && bData.reelCover.length > 0) availableCats.push("reelCover");
    if (bData.post && bData.post.length > 0) availableCats.push("post");
    if (bData.logo && bData.logo.length > 0) availableCats.push("logo");
    if (bData.highlights && bData.highlights.length > 0) availableCats.push("highlights");

    if (availableCats.length > 0) {
      if (!availableCats.includes(activeCategory)) {
        activeCategory = availableCats[0];
      }
    } else {
      activeCategory = "carousel";
    }

    renderCategoryPills(availableCats);

    // Auto select first project
    if (activeCategory === "carousel") {
      const projKeys = Object.keys(bData.carousel || {});
      activeProject = projKeys.length > 0 ? projKeys[0] : "";
    } else {
      activeProject = activeCategory;
    }
    activeSlideIndex = 0;
    viewMode = "collection";
    updateViewModeButtons();
    renderContent();
  }

  function renderBrandTabs() {
    const tabsContainer = document.getElementById("brandTabsGroup");
    if (!tabsContainer) return;
    tabsContainer.innerHTML = "";

    Object.keys(catalog).forEach(brandKey => {
      const brandData = catalog[brandKey];
      let totalCount = 0;
      if (brandData.carousel) {
        Object.values(brandData.carousel).forEach(items => totalCount += items.length);
      }
      ["reelCover", "post", "logo", "highlights"].forEach(cat => {
        if (brandData[cat]) totalCount += brandData[cat].length;
      });

      const btn = document.createElement("button");
      btn.className = `brand-tab ${brandKey === activeBrand ? "active" : ""}`;
      btn.innerHTML = `
        <span>${brandDisplayNames[brandKey] || brandKey}</span>
        <span class="tab-badge">${totalCount}</span>
      `;
      btn.addEventListener("click", () => setBrand(brandKey));
      tabsContainer.appendChild(btn);
    });
  }

  function renderCategoryPills(availableCats) {
    const catContainer = document.getElementById("categoryPills");
    if (!catContainer) return;
    catContainer.innerHTML = "";

    availableCats.forEach(catKey => {
      const bData = catalog[activeBrand];
      let count = 0;
      if (catKey === "carousel") {
        count = Object.keys(bData.carousel || {}).length;
      } else if (bData[catKey]) {
        count = bData[catKey].length;
      }

      const pill = document.createElement("button");
      pill.className = `category-pill ${catKey === activeCategory ? "active" : ""}`;
      pill.innerHTML = `
        <span>${categoryLabels[catKey] || catKey}</span>
        <span class="tab-badge">${count}</span>
      `;
      pill.addEventListener("click", () => {
        activeCategory = catKey;
        document.querySelectorAll(".category-pill").forEach(p => p.classList.remove("active"));
        pill.classList.add("active");

        if (activeCategory === "carousel") {
          const projs = Object.keys(bData.carousel || {});
          activeProject = projs.length > 0 ? projs[0] : "";
        } else {
          activeProject = activeCategory;
        }
        activeSlideIndex = 0;
        viewMode = "collection";
        updateViewModeButtons();
        renderContent();
      });
      catContainer.appendChild(pill);
    });
  }

  function updateViewModeButtons() {
    document.querySelectorAll(".view-mode-btn").forEach(btn => {
      if (btn.dataset.mode === viewMode) {
        btn.classList.add("active");
      } else {
        btn.classList.remove("active");
      }
    });
  }

  // MAIN RENDER SWITCH
  function renderContent() {
    const mainContainer = document.getElementById("contentMount");
    if (!mainContainer) return;
    mainContainer.innerHTML = "";

    if (viewMode === "json") {
      renderJsonView(mainContainer);
    } else if (viewMode === "single") {
      renderSingleProjectView(mainContainer);
    } else {
      renderCollectionView(mainContainer);
    }
  }

  // ==========================================
  // MODE A: COLLECTION VIEW
  // ==========================================
  function renderCollectionView(container) {
    const bData = catalog[activeBrand];
    if (!bData) {
      renderEmpty("No data for selected brand.");
      return;
    }

    const grid = document.createElement("div");
    grid.className = "collection-grid";

    if (activeCategory === "carousel") {
      const carousels = bData.carousel || {};
      const projKeys = Object.keys(carousels);

      if (projKeys.length === 0) {
        renderEmpty("No carousel projects found.");
        return;
      }

      projKeys.forEach(projKey => {
        const slides = carousels[projKey];
        if (!slides || slides.length === 0) return;

        const coverSlide = slides[0];
        const card = document.createElement("div");
        card.className = "project-card";

        const titleFormatted = formatTitleFromSlug(projKey);

        card.innerHTML = `
          <div class="card-media-wrapper">
            <img class="card-media-img" src="${getImageUrl(coverSlide)}" alt="${titleFormatted}" loading="lazy" />
            <div class="card-badge-overlay">
              <span class="count-badge">${slides.length} Slides</span>
              <span class="ratio-badge">${coverSlide.aspectRatio || "Auto"}</span>
            </div>
          </div>
          <div class="card-details">
            <div class="card-header-row">
              <div class="card-title">${titleFormatted}</div>
            </div>
            <div class="card-category-label">Carousel Project</div>
            <div class="card-thumbs-strip">
              ${slides.slice(0, 7).map(s => `<img class="mini-thumb" src="${getImageUrl(s)}" loading="lazy" />`).join("")}
              ${slides.length > 7 ? `<div class="mini-thumb" style="display:flex;align-items:center;justify-content:center;color:#fff;font-size:0.7rem;font-weight:700;">+${slides.length - 7}</div>` : ""}
            </div>
          </div>
        `;

        card.addEventListener("click", () => {
          activeProject = projKey;
          activeSlideIndex = 0;
          viewMode = "single";
          updateViewModeButtons();
          renderContent();
        });

        grid.appendChild(card);
      });
    } else {
      // Non-carousel categories: reelCover, post, logo, highlights
      const items = bData[activeCategory] || [];
      if (items.length === 0) {
        renderEmpty(`No ${categoryLabels[activeCategory]} assets found.`);
        return;
      }

      items.forEach((item, idx) => {
        const card = document.createElement("div");
        card.className = "project-card";
        const titleFormatted = `${categoryLabels[activeCategory]} #${item.order}`;

        card.innerHTML = `
          <div class="card-media-wrapper">
            <img class="card-media-img" src="${getImageUrl(item)}" alt="${titleFormatted}" loading="lazy" />
            <div class="card-badge-overlay">
              <span class="count-badge">#${item.order}</span>
              <span class="ratio-badge">${item.aspectRatio || "Auto"}</span>
            </div>
          </div>
          <div class="card-details">
            <div class="card-header-row">
              <div class="card-title">${titleFormatted}</div>
            </div>
            <div class="card-category-label">${item.width} × ${item.height} px • ${formatBytes(item.sizeBytes)}</div>
          </div>
        `;

        card.addEventListener("click", () => {
          activeProject = activeCategory;
          activeSlideIndex = idx;
          viewMode = "single";
          updateViewModeButtons();
          renderContent();
        });

        grid.appendChild(card);
      });
    }

    container.appendChild(grid);
  }

  // ==========================================
  // MODE B: SINGLE PROJECT VIEW
  // ==========================================
  function renderSingleProjectView(container) {
    const bData = catalog[activeBrand];
    let slides = [];
    let projectTitle = "";

    if (activeCategory === "carousel") {
      slides = (bData.carousel && bData.carousel[activeProject]) || [];
      projectTitle = formatTitleFromSlug(activeProject);
    } else {
      slides = bData[activeCategory] || [];
      projectTitle = `${categoryLabels[activeCategory]} Collection`;
    }

    if (!slides || slides.length === 0) {
      renderEmpty("No assets in this project.");
      return;
    }

    if (activeSlideIndex >= slides.length) activeSlideIndex = 0;
    const currentAsset = slides[activeSlideIndex];

    const singleContainer = document.createElement("div");
    singleContainer.className = "single-project-container";

    // Header with Breadcrumb & Back Button
    const headerNav = document.createElement("div");
    headerNav.className = "single-header-nav";
    headerNav.innerHTML = `
      <div class="project-title-meta">
        <h2>${projectTitle}</h2>
        <div class="project-breadcrumb">
          <span>${brandDisplayNames[activeBrand] || activeBrand}</span>
          <span>/</span>
          <span>${categoryLabels[activeCategory] || activeCategory}</span>
          <span>/</span>
          <span>Slide ${activeSlideIndex + 1} of ${slides.length}</span>
        </div>
      </div>
      <button class="back-to-collection-btn" id="backToCollectionBtn">
        ← Back to Collection
      </button>
    `;
    singleContainer.appendChild(headerNav);

    // Stage Layout: Main Carousel (Left) + Inspector (Right)
    const stageLayout = document.createElement("div");
    stageLayout.className = "stage-layout";

    // Carousel Stage
    const carouselStage = document.createElement("div");
    carouselStage.className = "main-carousel-stage";

    carouselStage.innerHTML = `
      <div class="large-image-frame" id="largeImageFrame">
        <button class="nav-arrow-btn prev" id="slidePrevBtn" aria-label="Previous Slide">‹</button>
        <img id="mainSlideImg" src="${getImageUrl(currentAsset)}" alt="Slide ${activeSlideIndex + 1}" />
        <button class="nav-arrow-btn next" id="slideNextBtn" aria-label="Next Slide">›</button>
        <div class="stage-counter-badge">${activeSlideIndex + 1} / ${slides.length}</div>
      </div>
      <div class="carousel-thumb-track" id="thumbTrack">
        ${slides.map((s, idx) => `
          <div class="carousel-thumb-item ${idx === activeSlideIndex ? "active" : ""}" data-idx="${idx}">
            <img src="${getImageUrl(s)}" alt="Thumb ${idx + 1}" loading="lazy" />
          </div>
        `).join("")}
      </div>
    `;

    // Inspector Panel
    const inspector = document.createElement("div");
    inspector.className = "inspector-panel";

    const allProjectUrls = slides.map(s => `${s.order}.webp:\n${s.url}`).join("\n\n");

    inspector.innerHTML = `
      <div class="inspector-section-title">
        <span>⚡</span> Asset Information
      </div>
      <div class="meta-table">
        <div class="meta-row">
          <span class="meta-label">Slide / Order</span>
          <span class="meta-val">#${currentAsset.order}</span>
        </div>
        <div class="meta-row">
          <span class="meta-label">Dimensions</span>
          <span class="meta-val">${currentAsset.width} × ${currentAsset.height} px</span>
        </div>
        <div class="meta-row">
          <span class="meta-label">Aspect Ratio</span>
          <span class="meta-val">${currentAsset.aspectRatio || "N/A"}</span>
        </div>
        <div class="meta-row">
          <span class="meta-label">File Size</span>
          <span class="meta-val">${formatBytes(currentAsset.sizeBytes)}</span>
        </div>
        <div class="meta-row">
          <span class="meta-label">Format</span>
          <span class="meta-val">WEBP (Lossless/High Q)</span>
        </div>
      </div>

      <div class="inspector-section-title">
        <span>🌐</span> jsDelivr Direct Link
      </div>
      <div class="cdn-url-box">
        <div class="cdn-url-text">${currentAsset.url}</div>
        <button class="btn-action-primary" id="copyUrlBtn">
          📋 Copy Direct URL
        </button>
      </div>

      <div class="inspector-section-title">
        <span>📦</span> Website Copy-Paste Output
      </div>
      <div class="project-links-box">
        <div class="project-links-preview">${allProjectUrls}</div>
        <div class="btn-group-row">
          <button class="btn-action-primary" id="copyAllUrlsBtn">
            Copy All URLs
          </button>
          <button class="btn-action-secondary" id="copyJsonBtn">
            Copy JSON
          </button>
        </div>
      </div>
    `;

    stageLayout.appendChild(carouselStage);
    stageLayout.appendChild(inspector);
    singleContainer.appendChild(stageLayout);
    container.appendChild(singleContainer);

    // Wire up events
    document.getElementById("backToCollectionBtn").addEventListener("click", () => {
      viewMode = "collection";
      updateViewModeButtons();
      renderContent();
    });

    document.getElementById("slidePrevBtn").addEventListener("click", (e) => {
      e.stopPropagation();
      prevSlide(slides.length);
    });

    document.getElementById("slideNextBtn").addEventListener("click", (e) => {
      e.stopPropagation();
      nextSlide(slides.length);
    });

    // Thumbnails click
    document.querySelectorAll(".carousel-thumb-item").forEach(thumb => {
      thumb.addEventListener("click", () => {
        activeSlideIndex = parseInt(thumb.dataset.idx, 10);
        updateSingleSlideView(slides);
      });
    });

    // Copy actions
    document.getElementById("copyUrlBtn").addEventListener("click", () => {
      copyText(currentAsset.url, "Direct jsDelivr URL copied!");
    });

    document.getElementById("copyAllUrlsBtn").addEventListener("click", () => {
      const urlsOnly = slides.map(s => s.url).join("\n");
      copyText(urlsOnly, `Copied ${slides.length} URLs for ${projectTitle}!`);
    });

    document.getElementById("copyJsonBtn").addEventListener("click", () => {
      const projectData = {
        brand: brandDisplayNames[activeBrand] || activeBrand,
        category: categoryLabels[activeCategory] || activeCategory,
        project: projectTitle,
        assets: slides
      };
      copyText(JSON.stringify(projectData, null, 2), "Project JSON copied!");
    });
  }

  function prevSlide(total) {
    activeSlideIndex = (activeSlideIndex - 1 + total) % total;
    const bData = catalog[activeBrand];
    const slides = activeCategory === "carousel" ? bData.carousel[activeProject] : bData[activeCategory];
    updateSingleSlideView(slides);
  }

  function nextSlide(total) {
    activeSlideIndex = (activeSlideIndex + 1) % total;
    const bData = catalog[activeBrand];
    const slides = activeCategory === "carousel" ? bData.carousel[activeProject] : bData[activeCategory];
    updateSingleSlideView(slides);
  }

  function updateSingleSlideView(slides) {
    if (!slides || slides.length === 0) return;
    const asset = slides[activeSlideIndex];

    const img = document.getElementById("mainSlideImg");
    if (img) {
      img.style.opacity = "0.4";
      img.src = getImageUrl(asset);
      img.onload = () => { img.style.opacity = "1"; };
    }

    const counter = document.querySelector(".stage-counter-badge");
    if (counter) counter.innerText = `${activeSlideIndex + 1} / ${slides.length}`;

    // Update thumbnail highlights
    document.querySelectorAll(".carousel-thumb-item").forEach((th, idx) => {
      if (idx === activeSlideIndex) {
        th.classList.add("active");
        th.scrollIntoView({ behavior: "smooth", inline: "center", block: "nearest" });
      } else {
        th.classList.remove("active");
      }
    });

    // Update Inspector table & URL
    const metaVals = document.querySelectorAll(".meta-table .meta-val");
    if (metaVals.length >= 5) {
      metaVals[0].innerText = `#${asset.order}`;
      metaVals[1].innerText = `${asset.width} × ${asset.height} px`;
      metaVals[2].innerText = asset.aspectRatio || "N/A";
      metaVals[3].innerText = formatBytes(asset.sizeBytes);
      metaVals[4].innerText = "WEBP (Lossless/High Q)";
    }

    const cdnBox = document.querySelector(".cdn-url-text");
    if (cdnBox) cdnBox.innerText = asset.url;
  }

  // ==========================================
  // JSON VIEW (DATA MANIFEST)
  // ==========================================
  function renderJsonView(container) {
    const bData = catalog[activeBrand];
    const jsonContainer = document.createElement("div");
    jsonContainer.className = "json-view-container";

    const title = document.createElement("h2");
    title.innerText = `Website-Ready JSON: ${brandDisplayNames[activeBrand] || activeBrand}`;
    jsonContainer.appendChild(title);

    const btnRow = document.createElement("div");
    btnRow.style.display = "flex";
    btnRow.style.gap = "10px";

    const copyBtn = document.createElement("button");
    copyBtn.className = "btn-action-primary";
    copyBtn.style.maxWidth = "200px";
    copyBtn.innerHTML = "📋 Copy Brand JSON";
    copyBtn.addEventListener("click", () => {
      copyText(JSON.stringify(bData, null, 2), "Brand JSON copied!");
    });
    btnRow.appendChild(copyBtn);

    const copyAllBtn = document.createElement("button");
    copyAllBtn.className = "btn-action-secondary";
    copyAllBtn.style.maxWidth = "200px";
    copyAllBtn.innerHTML = "📋 Copy Entire Catalog JSON";
    copyAllBtn.addEventListener("click", () => {
      copyText(JSON.stringify(catalog, null, 2), "Full Catalog JSON copied!");
    });
    btnRow.appendChild(copyAllBtn);

    jsonContainer.appendChild(btnRow);

    const pre = document.createElement("pre");
    pre.className = "json-code-block";
    pre.innerText = JSON.stringify(bData, null, 2);
    jsonContainer.appendChild(pre);

    container.appendChild(jsonContainer);
  }

  function renderEmpty(msg) {
    const mainContainer = document.getElementById("contentMount");
    if (!mainContainer) return;
    mainContainer.innerHTML = `
      <div class="empty-state">
        <h3>${msg}</h3>
      </div>
    `;
  }

  // Keyboard navigation for carousel
  function setupKeyboardNav() {
    window.addEventListener("keydown", (e) => {
      if (viewMode !== "single") return;
      const bData = catalog[activeBrand];
      if (!bData) return;
      const slides = activeCategory === "carousel" ? bData.carousel[activeProject] : bData[activeCategory];
      if (!slides || slides.length <= 1) return;

      if (e.key === "ArrowLeft") {
        prevSlide(slides.length);
      } else if (e.key === "ArrowRight") {
        nextSlide(slides.length);
      }
    });
  }

  // Touch swipe listener
  function setupTouchSwipe() {
    let touchStartX = 0;
    let touchEndX = 0;

    window.addEventListener("touchstart", (e) => {
      touchStartX = e.changedTouches[0].screenX;
    }, { passive: true });

    window.addEventListener("touchend", (e) => {
      if (viewMode !== "single") return;
      touchEndX = e.changedTouches[0].screenX;
      const diff = touchEndX - touchStartX;
      if (Math.abs(diff) > 40) {
        const bData = catalog[activeBrand];
        if (!bData) return;
        const slides = activeCategory === "carousel" ? bData.carousel[activeProject] : bData[activeCategory];
        if (!slides || slides.length <= 1) return;

        if (diff < 0) {
          nextSlide(slides.length); // Swipe left -> next
        } else {
          prevSlide(slides.length); // Swipe right -> prev
        }
      }
    }, { passive: true });
  }

  // Initialize once DOM is loaded
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", loadData);
  } else {
    loadData();
  }
})();
