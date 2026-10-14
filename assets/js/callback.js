// farazisgiannis.com — «Πάρτε με τηλέφωνο» (ideas track 8, 14 Oct 2026).
// A call-back request goes to avrastro.com's contact endpoint (the advisor's own system), which stores it, e-mails the
// advisor and puts it in the CRM inbox as a call task at the time of day chosen here. Nothing is stored in this browser,
// no cookies are sent (credentials: 'omit'), and nothing is fetched from avrastro.com until the visitor starts filling
// in the form. Without JavaScript the form says to call instead.
(function () {
  var form = document.getElementById('callback');
  if (!form || !window.fetch) return;
  var PAGE_LANG = form.getAttribute('data-lang') || 'el', RU = PAGE_LANG === 'ru', el = PAGE_LANG === 'el';
  var API = form.getAttribute('data-api'), LANG = el ? 'el' : 'en';
  var txt = el ? {
    missing: 'Γράψτε το όνομά σας και ένα τηλέφωνο, και τσεκάρετε τη συγκατάθεση.',
    phone: 'Το τηλέφωνο δεν φαίνεται σωστό. Χρησιμοποιήστε μόνο αριθμούς, κενά και +.',
    rate: 'Έχουν σταλεί πολλά αιτήματα. Δοκιμάστε ξανά σε μία ώρα ή καλέστε στο +357 97 840941.',
    failed: 'Το αίτημα δεν στάλθηκε. Καλέστε στο +357 97 840941 ή στείλτε μήνυμα στο WhatsApp.',
    sending: 'Αποστολή…',
  } : RU ? {
    missing: 'Укажите имя и телефон и отметьте согласие.',
    phone: 'Похоже, телефон указан неверно. Используйте только цифры, пробелы и +.',
    rate: 'Отправлено слишком много запросов. Попробуйте через час или позвоните по номеру +357 97 840941.',
    failed: 'Запрос не отправлен. Позвоните по номеру +357 97 840941 или напишите в WhatsApp.',
    sending: 'Отправляем…',
  } : {
    missing: 'Please give your name and a phone number, and tick the consent box.',
    phone: 'That phone number does not look right. Use only digits, spaces and +.',
    rate: 'Too many requests have been sent. Try again in an hour or call +357 97 840941.',
    failed: 'The request was not sent. Please call +357 97 840941 or send a WhatsApp message.',
    sending: 'Sending…',
  };
  var status = form.querySelector('.status'), submit = form.querySelector('button[type=submit]');
  var done = document.querySelector('[data-callback-done]');
  var state = { token: '', at: 0, loading: null };
  function show(kind, text) { status.className = 'status ' + kind; status.textContent = text; }
  function call(path, body) {
    var headers = { 'X-Vero-Lang': LANG };
    if (body) headers['Content-Type'] = 'application/json';
    return fetch(API + path, { method: body ? 'POST' : 'GET', headers: headers, body: body ? JSON.stringify(body) : undefined, credentials: 'omit', cache: 'no-store', mode: 'cors' })
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (b) { return { ok: r.ok, status: r.status, b: b }; }); });
  }
  function token() {
    state.loading = call('/form-token').then(function (r) { if (!r.ok || !r.b.token) throw new Error('token'); state.token = r.b.token; state.at = Date.now(); });
    return state.loading;
  }
  // the signed form token is fetched only once the visitor starts filling in the form
  form.addEventListener('focusin', function () { if (!state.loading) token().catch(function () { state.loading = null; }); });

  function send(data, retried) {
    var wait = Math.max(0, 2500 - (Date.now() - state.at));
    return new Promise(function (ok) { setTimeout(ok, wait); }).then(function () {
      data.form_token = state.token;
      return call('/contact', data);
    }).then(function (r) {
      if (r.ok && r.b.ok) {
        form.hidden = true;
        if (done) { done.hidden = false; done.focus(); }
        return;
      }
      var code = r.b && r.b.code;
      if (!retried && (code === 'vero_form_expired' || code === 'vero_too_fast')) return token().then(function () { return send(data, true); });
      if (r.status === 429) return show('err', txt.rate);
      var f = r.b && r.b.data && r.b.data.fields;
      if (f && f.phone) return show('err', txt.phone);
      show('err', txt.failed);
    });
  }
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var f = form.elements, when = form.querySelector('input[name=best_time]:checked');
    var data = {
      kind: 'callback', name: f.name.value.trim(), phone: f.phone.value.trim(), topic: f.topic.value, best_time: when ? when.value : '',
      privacy: f.privacy.checked, vc_hp_x: f.vc_hp_x.value, source: location.origin + location.pathname,
    };
    if (data.name.length < 2 || !data.phone || !data.privacy) return show('err', txt.missing);
    if (!/^[+()\d\s.-]{6,40}$/.test(data.phone)) return show('err', txt.phone);
    var label = submit.innerHTML; submit.disabled = true; submit.textContent = txt.sending; status.className = 'status';
    (state.token ? Promise.resolve() : (state.loading || token())).then(function () { return send(data, false); })
      .catch(function () { show('err', txt.failed); })
      .then(function () { submit.disabled = false; submit.innerHTML = label; });
  });
})();
