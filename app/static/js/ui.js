(function () {
  /* ── Toast API ── */
  window.showToast = function (message, type) {
    type = type || 'success';
    var el = document.getElementById('toast');
    if (!el) return;
    el.textContent = message;
    el.className = 'toast toast-' + type;
    el.offsetHeight;
    el.classList.add('show');
    clearTimeout(el._hide);
    el._hide = setTimeout(function () {
      el.classList.remove('show');
    }, 3000);
  };

  /* ── Scroll-based nav glass effect ── */
  var nav = document.getElementById('site-nav');
  if (nav) {
    function updateNav() {
      if (window.scrollY > 20) {
        nav.classList.add('glass');
        nav.classList.remove('bg-transparent');
      } else {
        nav.classList.remove('glass');
        nav.classList.add('bg-transparent');
      }
    }
    updateNav();
    window.addEventListener('scroll', updateNav, { passive: true });
  }

  /* ── Scroll Reveal with IntersectionObserver ── */
  if (window.IntersectionObserver) {
    var observerOptions = { threshold: 0.08, rootMargin: '0px 0px -40px 0px' };
    document.querySelectorAll('.reveal, .reveal-left, .reveal-right, .reveal-scale').forEach(function (el) {
      new IntersectionObserver(function (e) {
        if (e[0].isIntersecting) {
          e[0].target.classList.add('visible');
        }
      }, observerOptions).observe(el);
    });
  }

  /* ── Mobile menu ── */
  var btn = document.getElementById('menu-btn'),
    menu = document.getElementById('mobile-menu'),
    icon = document.getElementById('hamburger-icon');
  if (btn && menu && icon) {
    btn.addEventListener('click', function () {
      menu.classList.toggle('hidden');
      icon.classList.toggle('open');
      var expanded = btn.getAttribute('aria-expanded') === 'true' ? 'false' : 'true';
      btn.setAttribute('aria-expanded', expanded);
    });
  }

  /* ── Scroll to top ── */
  var st = document.getElementById('scroll-top');
  if (st) {
    window.addEventListener(
      'scroll',
      function () {
        st.classList.toggle('visible', window.scrollY > 400);
      },
      { passive: true }
    );
  }

  /* ── Load More pagination ── */
  document.querySelectorAll('[data-load-more]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var container = document.querySelector(btn.getAttribute('data-container'));
      var page = parseInt(btn.getAttribute('data-page') || '1');
      var url = btn.getAttribute('data-url') || window.location.pathname + '?page=' + page;
      btn.disabled = true;
      btn.innerHTML = '<span class="loading-spinner"></span> Loading...';
      fetch(url)
        .then(function (r) {
          return r.json();
        })
        .then(function (data) {
          if (data.items && container) {
            data.items.forEach(function (item) {
              var el = document.createElement('div');
              el.innerHTML = item.html;
              container.appendChild(el.firstElementChild);
            });
          }
          if (data.has_more) {
            btn.setAttribute('data-page', page + 1);
            btn.disabled = false;
            btn.innerHTML = 'Load more';
          } else {
            btn.innerHTML = 'All loaded';
            btn.disabled = true;
          }
        })
        .catch(function () {
          btn.innerHTML = 'Error loading';
          btn.disabled = false;
        });
    });
  });

  /* ── Search debounce ── */
  document.querySelectorAll('.search-input[data-search]').forEach(function (input) {
    var timer;
    input.addEventListener('input', function () {
      clearTimeout(timer);
      timer = setTimeout(function () {
        var query = input.value.trim();
        if (query.length > 1) {
          window.location.href = input.getAttribute('data-search') + '?q=' + encodeURIComponent(query);
        }
      }, 400);
    });
  });

  /* ── 3D Tilt on .tilt-card ── */
  document.querySelectorAll('.tilt-card').forEach(function (card) {
    card.addEventListener('mousemove', function (e) {
      var rect = card.getBoundingClientRect();
      var x = e.clientX - rect.left;
      var y = e.clientY - rect.top;
      var centerX = rect.width / 2;
      var centerY = rect.height / 2;
      var rotateX = ((y - centerY) / centerY) * -8;
      var rotateY = ((x - centerX) / centerX) * 8;
      var inner = card.querySelector('.tilt-card-inner') || card;
      inner.style.transform = 'rotateX(' + rotateX + 'deg) rotateY(' + rotateY + 'deg)';
      card.style.setProperty('--mouse-x', (x / rect.width) * 100 + '%');
      card.style.setProperty('--mouse-y', (y / rect.height) * 100 + '%');
    });
    card.addEventListener('mouseleave', function () {
      var inner = card.querySelector('.tilt-card-inner') || card;
      inner.style.transform = 'rotateX(0) rotateY(0)';
    });
  });

  /* ── Feature card radial cursor glow ── */
  document.querySelectorAll('.feature-card').forEach(function (card) {
    card.addEventListener('mousemove', function (e) {
      var rect = card.getBoundingClientRect();
      var x = e.clientX - rect.left;
      var y = e.clientY - rect.top;
      card.style.setProperty('--mouse-x', x + 'px');
      card.style.setProperty('--mouse-y', y + 'px');
    });
  });

  /* ── Lightbox ── */
  var lightbox = document.getElementById('lightbox');
  if (lightbox) {
    var lightboxImg = lightbox.querySelector('img');
    document.querySelectorAll('[data-lightbox]').forEach(function (el) {
      el.addEventListener('click', function () {
        lightboxImg.src = el.getAttribute('data-lightbox') || el.src;
        lightbox.classList.add('active');
        document.body.style.overflow = 'hidden';
      });
    });
    lightbox.addEventListener('click', function (e) {
      if (e.target === lightbox || e.target.classList.contains('lightbox-close')) {
        lightbox.classList.remove('active');
        document.body.style.overflow = '';
      }
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && lightbox.classList.contains('active')) {
        lightbox.classList.remove('active');
        document.body.style.overflow = '';
      }
    });
  }

  /* ── Counter animation for .stat-number ── */
  document.querySelectorAll('.stat-number[data-count]').forEach(function (el) {
    var target = parseInt(el.getAttribute('data-count'));
    var duration = 1200;
    var start = performance.now();
    function update(now) {
      var elapsed = now - start;
      var progress = Math.min(elapsed / duration, 1);
      var eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.floor(eased * target);
      if (progress < 1) requestAnimationFrame(update);
    }
    var observer = new IntersectionObserver(function (e) {
      if (e[0].isIntersecting) {
        requestAnimationFrame(update);
        observer.unobserve(el);
      }
    });
    observer.observe(el);
  });
})();
