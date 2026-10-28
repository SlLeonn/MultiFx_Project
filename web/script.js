"use strict";

(() => {
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const header = document.querySelector(".site-header");
  const stageButtons = [...document.querySelectorAll("[data-stage]")];
  const stagePanels = [...document.querySelectorAll("[data-stage-panel]")];

  function selectStage(index, moveFocus = false) {
    if (!stageButtons[index] || !stagePanels[index]) return;
    stageButtons.forEach((button, position) => {
      const active = position === index;
      button.classList.toggle("is-active", active);
      button.setAttribute("aria-pressed", String(active));
      stagePanels[position].hidden = !active;
    });
    if (moveFocus) stageButtons[index].focus();
  }

  stageButtons.forEach((button, index) => {
    button.addEventListener("click", () => selectStage(index));
    button.addEventListener("keydown", (event) => {
      let next;
      if (event.key === "ArrowRight") next = (index + 1) % stageButtons.length;
      if (event.key === "ArrowLeft") next = (index - 1 + stageButtons.length) % stageButtons.length;
      if (event.key === "Home") next = 0;
      if (event.key === "End") next = stageButtons.length - 1;
      if (next !== undefined) {
        event.preventDefault();
        selectStage(next, true);
      }
    });
  });
  if (stageButtons.length && stageButtons.length === stagePanels.length) selectStage(0);

  const revealElements = [...document.querySelectorAll("[data-reveal]")];
  let revealObserver;
  if (!reducedMotion.matches && "IntersectionObserver" in window) {
    revealObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        revealObserver.unobserve(entry.target);
      });
    }, { threshold: 0.08 });
    revealElements.forEach((element) => {
      element.classList.add("will-reveal");
      revealObserver.observe(element);
    });
  }

  const hero = document.querySelector(".hero");
  const product = document.querySelector(".product-stage");
  const finePointer = window.matchMedia("(hover: hover) and (pointer: fine)");
  let scheduled = false;

  function updateScroll() {
    scheduled = false;
    header?.classList.toggle("is-scrolled", window.scrollY > 12);
    if (hero && product) {
      const progress = Math.min(window.scrollY / Math.max(hero.offsetHeight, 1), 1);
      product.style.setProperty("--scroll-shift", reducedMotion.matches ? "0px" : String(-18 * progress) + "px");
    }
  }

  window.addEventListener("scroll", () => {
    if (!scheduled) {
      scheduled = true;
      window.requestAnimationFrame(updateScroll);
    }
  }, { passive: true });
  updateScroll();

  function resetTilt() {
    product?.style.setProperty("--tilt-x", "0deg");
    product?.style.setProperty("--tilt-y", "0deg");
  }

  product?.addEventListener("pointermove", (event) => {
    if (reducedMotion.matches || !finePointer.matches) return;
    const bounds = product.getBoundingClientRect();
    const x = (event.clientX - bounds.left) / Math.max(bounds.width, 1) - 0.5;
    const y = (event.clientY - bounds.top) / Math.max(bounds.height, 1) - 0.5;
    product.style.setProperty("--tilt-x", String(x * 5) + "deg");
    product.style.setProperty("--tilt-y", String(-y * 4) + "deg");
  });
  product?.addEventListener("pointerleave", resetTilt);

  reducedMotion.addEventListener("change", () => {
    if (reducedMotion.matches) {
      revealObserver?.disconnect();
      revealElements.forEach((element) => element.classList.add("is-visible"));
      resetTilt();
    }
    updateScroll();
  });
})();
