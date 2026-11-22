/* MAGNEEFY — site interactions */
(function () {
  document.documentElement.classList.add('js');

  // Sticky nav: transparent over hero, solid on scroll
  var nav = document.querySelector('.nav');
  function onScroll() { if (nav) nav.classList.toggle('scrolled', window.scrollY > 24); }
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  // Mobile menu
  var toggle = document.querySelector('.menu-toggle');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var open = document.body.classList.toggle('menu-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.querySelectorAll('.mobile-menu a').forEach(function (a) {
      a.addEventListener('click', function () {
        document.body.classList.remove('menu-open');
        toggle.setAttribute('aria-expanded', 'false');
      });
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && document.body.classList.contains('menu-open')) {
        document.body.classList.remove('menu-open');
        toggle.setAttribute('aria-expanded', 'false');
        toggle.focus();
      }
    });
  }

  // Scroll reveal
  var els = document.querySelectorAll('.reveal, .process');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    els.forEach(function (el) { io.observe(el); });
  } else {
    els.forEach(function (el) { el.classList.add('in'); });
  }

  // Founder portrait: show photo if assets/img/jeffery-odiba.jpg exists
  document.querySelectorAll('.portrait-frame img').forEach(function (img) {
    function ok() { img.parentElement.classList.add('has-img'); }
    if (img.complete && img.naturalWidth) ok();
    img.addEventListener('load', ok);
    img.addEventListener('error', function () { img.remove(); });
  });

  // Contact form
  var form = document.querySelector('#contact-form');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var valid = true;
      form.querySelectorAll('[data-required]').forEach(function (f) {
        var input = f.querySelector('input, textarea, select');
        var v = (input.value || '').trim();
        var bad = !v || (input.type === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v));
        f.classList.toggle('invalid', bad);
        if (bad && valid) { input.focus(); valid = false; }
      });
      if (!valid) return;

      var data = new FormData(form);
      var endpoint = form.getAttribute('data-endpoint');
      var wrap = form.closest('.form-wrap');
      var btn = form.querySelector('button[type="submit"]');

      if (endpoint) {
        btn.disabled = true;
        btn.firstChild.textContent = 'Sending… ';
        fetch(endpoint, { method: 'POST', body: data, headers: { Accept: 'application/json' } })
          .then(function (r) { if (!r.ok) throw new Error(); wrap.classList.add('sent'); })
          .catch(function () {
            btn.disabled = false;
            btn.firstChild.textContent = 'Try again ';
            alert('Something went wrong sending your message. Please email us directly.');
          });
      } else {
        // No form backend configured yet: hand off to the visitor's email client.
        var to = form.getAttribute('data-mailto');
        var needs = data.getAll('needs').join(', ') || 'Not specified';
        var body = [
          'Name: ' + data.get('name'),
          'Email: ' + data.get('email'),
          'Company: ' + (data.get('company') || '-'),
          'Website: ' + (data.get('website') || '-'),
          'Interested in: ' + needs,
          'Stage: ' + (data.get('stage') || '-'),
          '',
          data.get('message')
        ].join('\n');
        window.location.href = 'mailto:' + to + '?subject=' +
          encodeURIComponent('New enquiry from ' + data.get('name')) + '&body=' + encodeURIComponent(body);
        wrap.classList.add('sent');
      }
    });
    form.querySelectorAll('[data-required] input, [data-required] textarea, [data-required] select').forEach(function (i) {
      i.addEventListener('input', function () { i.closest('.field').classList.remove('invalid'); });
    });
  }

  // Newsletter (front-end only until connected to an email platform)
  document.querySelectorAll('.subscribe').forEach(function (f) {
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var input = f.querySelector('input');
      var msg = f.parentElement.querySelector('.sub-msg');
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input.value.trim())) {
        if (msg) msg.textContent = 'Please enter a valid email address.';
        return;
      }
      if (msg) msg.textContent = 'Thanks, you’re on the list.';
      input.value = '';
    });
  });

  // Year
  document.querySelectorAll('[data-year]').forEach(function (el) { el.textContent = new Date().getFullYear(); });
})();
