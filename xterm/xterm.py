# -*- coding: utf-8 -*-

# pylint: disable=invalid-name

import asyncio
import fcntl
import json
import os
import struct
import termios

from django import forms
from django.http import HttpResponse
from django.views import generic

from pistoke.nakyma import WebsocketNakyma

from .paate import Paateprosessi


class XtermNakyma(WebsocketNakyma, generic.TemplateView):
  '''
  Django-näkymä vuorovaikutteisen Websocket-yhteyden tarjoamiseen.

  Käyttöliittymän luontiin käytetään Xterm.JS-vimpainta.
  '''
  template_name = 'xterm/xterm.html'

  media = forms.widgets.Media(
    css={'all': [
      'https://unpkg.com/xterm@4.5.0/css/xterm.css',
    ]},
    js=[
      # pylint: disable=line-too-long
      'https://unpkg.com/xterm@4.5.0/lib/xterm.js',
      'https://unpkg.com/xterm-addon-fit@0.3.0/lib/xterm-addon-fit.js',
      'https://unpkg.com/xterm-addon-web-links@0.3.0/lib/xterm-addon-web-links.js',
      'https://unpkg.com/xterm-addon-search@0.6.0/lib/xterm-addon-search.js',
      'xterm/js/xterm.js',
    ],
  )

  class js_bool(int):
    ''' Näytetään totuusarvot javascript-muodossa: true/false. '''
    def __repr__(self):
      return repr(bool(self)).lower()
    # class js_bool

  # Xterm-ikkunan alustusparametrit.
  xterm = {
    'cursorBlink': js_bool(True),
    'macOptionIsMeta': js_bool(False),
    'scrollback': 5000,
  }

  def prosessi(self):
    ''' Päätteessä ajettava prosessi. '''
    raise NotImplementedError

  def get(self, request, *args, **kwargs):
    '''
    Varmista, että Websocket-protokolla on saatavilla.
    '''
    if getattr(request, 'websocket', None) is None:
      return HttpResponse(status=503)
    return super().get(request, *args, **kwargs)
    # def get

  @staticmethod
  async def _lahetys(send, jono):
    '''
    Asynkroninen lähetys: odota dataa jonosta ja lähetä.
    '''
    while True:
      data = await jono.get()
      await send(data.decode())
      jono.task_done()
      # while True
    # async def _lahetys

  @staticmethod
  async def _vastaanotto(receive, fd):
    '''
    Asynkroninen lukutehtävä: lue dataa ja syötä prosessille.
    '''
    while True:
      data = await receive()

      if isinstance(data, bytes):
        # Binäärisanoma: näppäinkoodi.
        # Control-C katkaisee syötteen.
        if data == b'\x03':
          break
        try:
          os.write(fd, data)
        except OSError:
          break

      elif isinstance(data, str):
        # Tekstisanoma: JSON-muotoinen IOCTL-ohjauskomento.
        data = json.loads(data, strict=False)
        if 'cols' in data and 'rows' in data:
          # Asetetaan ikkunan koko.
          fcntl.ioctl(
            fd,
            termios.TIOCSWINSZ,
            struct.pack("HHHH", data['rows'], data['cols'], 0, 0)
          )
      # while True
    # async def _vastaanotto

  async def websocket(self, request, *args, **kwargs):
    # pylint: disable=unused-argument
    lahetettava_data = asyncio.Queue()
    def tulosteen_vastaanotto(prosessi):
      '''
      Callback-tyyppinen rutiini datan lukemiseksi PTY:ltä.
      Kerää kaikki saatavilla oleva data, lisää lähetysjonoon.
      '''
      data = bytearray()
      while True:
        try:
          data += os.read(prosessi.fd, 4096)
        except (IOError, BlockingIOError):
          break
        if not data:
          return
      lahetettava_data.put_nowait(data)
      # def tulosteen_vastaanotto

    # Aloita tulostedatan lähetys itsenäisenä tehtävänä.
    lahetys_tehtava = asyncio.ensure_future(
      self._lahetys(request.send, lahetettava_data)
    )

    # Alusta pääteprosessi ja datan vastaanottotehtävä.
    paate = await Paateprosessi(self.prosessi, lukija=tulosteen_vastaanotto)
    tehtavat = {
      paate,
      asyncio.ensure_future(
        self._vastaanotto(request.receive, paate.fd)
      ),
    }

    # Odota siksi kunnes joko syöte katkaistaan
    # tai pääteprosessi on valmis.
    try:
      _, tehtavat = await asyncio.wait(
        tehtavat, return_when=asyncio.FIRST_COMPLETED
      )

    # Peruuta kesken jääneet tehtävät ja odota ne loppuun.
    finally:
      for kesken in tehtavat:
        kesken.cancel()
      await asyncio.gather(*tehtavat, return_exceptions=True)
      # Odota siksi, kunnes kaikki data on lähetetty.
      await lahetettava_data.join()
      # Peruuta lähetystehtävä ja odota se loppuun.
      lahetys_tehtava.cancel()
      await asyncio.gather(lahetys_tehtava, return_exceptions=True)

    # async def websocket

  # class XtermNakyma
