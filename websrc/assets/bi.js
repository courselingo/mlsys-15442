/* 给每个 .bi 注入「对照 / 仅中文 / English」切换按钮。
   用 MutationObserver 而不是 DOMContentLoaded —— Material 的
   navigation.instant 会替换 DOM，只挂一次会失效。 */
(function () {
  var VIEWS = [
    ['both', '对照'],
    ['zh', '仅中文'],
    ['en', 'English'],
  ];

  function init(el) {
    if (el.dataset.biReady === '1') return;
    el.dataset.biReady = '1';
    el.dataset.view = 'both';

    var bar = document.createElement('div');
    bar.className = 'bi-toolbar';

    var sw = document.createElement('div');
    sw.className = 'bi-switch';
    sw.setAttribute('role', 'group');
    sw.setAttribute('aria-label', '对照模式');

    VIEWS.forEach(function (pair, idx) {
      var b = document.createElement('button');
      b.type = 'button';
      b.textContent = pair[1];
      if (idx === 0) b.className = 'on';
      b.addEventListener('click', function () {
        el.dataset.view = pair[0];
        Array.prototype.forEach.call(sw.children, function (o) {
          o.classList.toggle('on', o === b);
        });
      });
      sw.appendChild(b);
    });

    var hint = document.createElement('span');
    hint.className = 'bi-hint';
    hint.textContent = '逐段对照 · 左侧为中文，右侧为原文';

    bar.appendChild(sw);
    bar.appendChild(hint);
    el.insertBefore(bar, el.firstChild);
  }

  function scan() {
    Array.prototype.forEach.call(document.querySelectorAll('.bi'), init);
  }

  document.addEventListener('DOMContentLoaded', scan);
  if (typeof document$ !== 'undefined' && document$.subscribe) {
    document$.subscribe(scan);
  }
  new MutationObserver(scan).observe(document.documentElement, {
    childList: true,
    subtree: true,
  });
})();
