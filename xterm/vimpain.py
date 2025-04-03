from django_sivumedia import Mediasaate


class XtermJS(Mediasaate):
  class Media:
    versio = '5.3.0'
    css = {'all': [
      f'https://cdn.jsdelivr.net/npm/xterm@{versio}/css/xterm.min.css',
    ]}
    js = [
      f'https://cdn.jsdelivr.net/npm/xterm@{versio}/lib/xterm.min.js'
    ]


class XtermAddonFit(XtermJS):
  class Media:
    versio = '0.10.0'
    js = [
      f'https://cdn.jsdelivr.net/npm/@xterm/addon-fit@{versio}'
      f'/lib/addon-fit.min.js'
    ]


class XtermAddonSearch(XtermJS):
  class Media:
    versio = '0.15.0'
    js = [
      f'https://cdn.jsdelivr.net/npm/@xterm/addon-search@{versio}'
      f'/lib/addon-search.min.js'
    ]


class XtermAddonWebLinks(XtermJS):
  class Media:
    versio = '0.11.0'
    js = [
      f'https://cdn.jsdelivr.net/npm/@xterm/addon-web-links@{versio}'
      f'/lib/addon-web-links.min.js'
    ]
