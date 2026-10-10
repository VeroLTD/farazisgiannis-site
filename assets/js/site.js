// farazisgiannis.com — the phone menu and the contact form. No tracking, no third-party code.
(function () {
  var btn = document.querySelector('.menu-btn'), nav = document.getElementById('nav');
  if (btn && nav) btn.addEventListener('click', function () {
    var open = nav.classList.toggle('open');
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  });

  var form = document.getElementById('enquiry');
  if (!form) return;
  var el = form.getAttribute('data-lang') !== 'en';
  var msg = {
    missing: el ? 'Γράψτε το όνομά σας και ένα τηλέφωνο ή e-mail για να σας απαντήσω.' : 'Please give your name and a phone number or e-mail so I can reply.',
    email: el ? 'Το e-mail δεν φαίνεται σωστό. Ελέγξτε το και ξαναδοκιμάστε.' : 'That e-mail address does not look right. Please check it.',
    phone: el ? 'Το τηλέφωνο δεν φαίνεται σωστό. Χρησιμοποιήστε μόνο αριθμούς, κενά και +.' : 'That phone number does not look right. Use only digits, spaces and +.',
    consent: el ? 'Τσεκάρετε τη συγκατάθεση ώστε να μπορώ να επικοινωνήσω μαζί σας.' : 'Please tick the consent box so I can contact you.',
    rate_limited: el ? 'Έχουν σταλεί πολλά μηνύματα. Δοκιμάστε ξανά σε μία ώρα ή καλέστε στο +357 97 840941.' : 'Too many messages have been sent. Try again in an hour or call +357 97 840941.',
    failed: el ? 'Το μήνυμα δεν στάλθηκε. Καλέστε στο +357 97 840941 ή στείλτε μήνυμα στο WhatsApp.' : 'The message was not sent. Please call +357 97 840941 or send a WhatsApp message.',
    ok: el ? 'Ευχαριστώ. Το μήνυμά σας στάλθηκε και θα σας καλέσω σύντομα.' : 'Thank you. Your message has been sent and I will call you soon.',
    sending: el ? 'Αποστολή…' : 'Sending…',
  };
  var status = form.querySelector('.status'), submit = form.querySelector('button[type=submit]');
  function show(kind, text) { status.className = 'status ' + kind; status.textContent = text; }
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var f = form.elements;
    var data = {
      name: f.name.value.trim(), phone: f.phone.value.trim(), email: f.email.value.trim(), topic: f.topic.value,
      message: f.message.value.trim(), website: f.website.value, consent: f.consent.checked, lang: el ? 'el' : 'en',
    };
    if (!data.name || (!data.phone && !data.email)) return show('err', msg.missing);
    if (data.email && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(data.email)) return show('err', msg.email);
    if (data.phone && !/^[+()\d\s.-]{6,40}$/.test(data.phone)) return show('err', msg.phone);
    if (!data.consent) return show('err', msg.consent);
    var label = submit.textContent; submit.disabled = true; submit.textContent = msg.sending;
    fetch(form.action, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(data) })
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (b) { return { ok: r.ok, b: b }; }); })
      .then(function (r) {
        if (r.ok) { form.reset(); show('ok', msg.ok); }
        else show('err', msg[r.b && r.b.error] || msg.failed);
      })
      .catch(function () { show('err', msg.failed); })
      .then(function () { submit.disabled = false; submit.textContent = label; });
  });
})();
