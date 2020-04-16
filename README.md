django-xterm
============
Django-pohjainen Xterm.JS-pääteyhteys


Asennusvaatimukset
------------------
* Django 3.2 tai uudempi
* django-pistoke


Asennus
-------
Paketin asennus näennäisympäristöön:
```bash
pip install django-xterm
```

Django-asetukset:
```python
# projekti/asetukset.py

INSTALLED_APPS = [
  ...
  'django-xterm',
]
```


Käyttö
------
Paketti toteuttaa vuorovaikutteisen pääteistunnon Web-sivun kautta käyttäjälle. Pääte on toteutettu `Xterm.js`-vimpaimen avulla. Vimpain ohjaa Websocket-yhteyden läpi palvelimella olevaa PTY-tiedostokuvaajaa, joka puolestaan ohjaa TTY-päätettä, johon voidaan liittää haluttu, vuorovaikutteinen istunto (esim. `bash`).

Ajettavan istunnon sisällön määräämiseksi käsillä olevan paketin toteuttama `XtermNakyma`-luokka on periytettävä seuraavan esimerkin tapaan:
```python
# sovellus/bash.py

import json
import subprocess

from xterm import XtermNakyma

class Komentokeskusnakyma(XtermNakyma):
  template_name = 'sovellus/bash.html'

  def prosessi(self):
    subprocess.run(['/bin/bash'])

  async def websocket(self, request, *args, **kwargs):
    data = json.loads(await request.receive())
    if not request._tarkista_csrf(data.get('csrfmiddlewaretoken')):
      return await request.send(
        '\033[31mCSRF-avain puuttuu tai se on virheellinen!\033[0m'
      )
    await super().websocket(request, *args, **kwargs)
```

```html
<!-- sovellus/bash.html -->
{% extends "xterm/xterm.html" %}

{% block sisalto %}
  <form id="avaa" method="POST">
    {% csrf_token %}
    <input type="submit" value="Suorita"/>
  </form>
  <hr/>
  {{ block.super }}
{% endblock sisalto %}

{% block skriptit %}
  {{ block.super }}
  <script>
    document.getElementById("avaa").onsubmit = function (e) {
      e.preventDefault();
      var formData = new FormData(e.target);
      var lomake = {};
      formData.forEach(function (value, key) {
        lomake[key] = value;
      });
      avaa_xterm(function (ws) { ws.send(JSON.stringify(lomake)); });
    };
  </script>
{% endblock skriptit %}
```
