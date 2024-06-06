"use strict";

(function () {
  // vrt. https://github.com/Om3rr/pyxtermjs/master/pyxtermjs/index.html

  let term = null;
  let websocket = null;
  let fit = null;

  function fitToScreen(){
    if (websocket && term && fit) {
      fit.fit();
      websocket.send(JSON.stringify({cols: term.cols, rows: term.rows}))
    }
  }
  function debounce(func, wait_ms) {
    let timeout
    return function(...args) {
      const context = this
      clearTimeout(timeout)
      timeout = setTimeout(function () { func.apply(context, args); }, wait_ms)
    }
  }

  window.addEventListener(
    "resize",
    debounce(fitToScreen, 50),
    {passive: true}
  );

  window.avaaXterm = function (url, asetukset) {
    return new Promise(function (resolve, reject) {
      if (term)
        term.dispose();
      if (websocket)
        websocket.close();

      term = new Terminal(asetukset);
      fit = new FitAddon.FitAddon();
      term.loadAddon(fit);
      term.loadAddon(new WebLinksAddon.WebLinksAddon());
      term.loadAddon(new SearchAddon.SearchAddon());
      term.open(document.getElementById('xterm'));
      fit.fit()
      term.onData(function (data) {
        websocket.send(new Blob(data.split()));
      });

      websocket = new WebSocket(url);
      websocket.onopen = function () {
        resolve(websocket);
        setTimeout(fitToScreen, 0);
      };
      websocket.onmessage = function (e) {
        term.write(e.data)
      };
    });
  };
})();
