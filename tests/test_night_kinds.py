"""Byte and refusal parity for the two-kind table.

Goldens were produced by running this SAME fixture module against a
``git archive cdc05e9b`` copy under /tmp (see the report for commands).
The measurement checkout stays at the base bytes on both runs, since H and
the sealed manifest pin those bytes; only the imported authoring code changes.
"""
from __future__ import annotations

import base64
from dataclasses import FrozenInstanceError
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import time
import unittest

from joulewise import evidence_night, night_gate, quiet_predicate_campaign
try:
    from joulewise.night_kinds import NIGHT_KINDS, UnknownNightKind, kind_row
except ModuleNotFoundError:  # The base archive intentionally predates the table.
    NIGHT_KINDS, UnknownNightKind, kind_row = {}, ValueError, None
from joulewise.night_plan_writer import write_night_plan
from scripts import gen_evidence_night


ROOT = Path(__file__).resolve().parents[1]
BASE_SOURCE = Path(os.environ.get("JW_KIND_BASE_SOURCE", "/tmp/jwkindbase"))
FIXTURE = Path("/tmp/jwkindfixture")
GOLDENS = {
    'chain': 'IyEvYmluL3pzaAojIEdFTkVSQVRFRCBieSBzY3JpcHRzL2dlbl9ldmlkZW5jZV9uaWdodC5weTsgZG8gbm90IGVkaXQuCnNldCAtZXVvIHBpcGVmYWlsCmV4cG9ydCBOSUdIVF9QQVlMT0FEX0tJTkQ9cXVpZXRfcHJlZGljYXRlX2V2aWRlbmNlCmV4cG9ydCBQWVRIT05ET05UV1JJVEVCWVRFQ09ERT0xCmV4cG9ydCBFVklERU5DRV9QTEFOX1BBVEg9Jy90bXAvandraW5kZml4dHVyZS9jdXN0b2R5L25pZ2h0X3BsYW4uanNvbicKZXhwb3J0IEVWSURFTkNFX01BTklGRVNUX1BBVEg9Jy90bXAvandraW5kZml4dHVyZS9jdXN0b2R5L2V2aWRlbmNlX21hbmlmZXN0Lmpzb24nCmV4cG9ydCBFVklERU5DRV9NQU5JRkVTVF9TSEEyNTY9JzNmNmIwMDM5YzA3OTliZTRmNzllNWM0YWIyYzIxZTFhYTEwYWE5ZGI4ZTNjNzdkZWQwMGRkODViNTMzMGY5YmInCmV4cG9ydCBFVklERU5DRV9DSEFJTl9TT1VSQ0VfU0hBMjU2PSc1NjhhMjc3MWIyOGRhOWQ4MDVjZDIzZmY0MDU5YmJiYzI3ZDZkZmFkMWY4ZDk2MDMzMzFhNDEyZTM3NTFiN2VhJwpleHBvcnQgUFk9Jy90bXAvandraW5kYmFzZS8udmVudi9iaW4vcHl0aG9uJwpleHBvcnQgUFlUSE9OUEFUSD0nL3RtcC9qd2tpbmRiYXNlJwpyZWZ1c2UoKSB7ICIkUFkiIC1CIC1tIGpvdWxld2lzZS5xdWlldF9wcmVkaWNhdGVfY2FtcGFpZ24gcmVmdXNlIC0tcmVhc29uICIkMSI7IGV4aXQgMjsgfQpbWyAiJHtOSUdIVF9QTEFOX0lEOi19IiA9PSAncXBlMDEtcGlsb3QtbjEtMjAyNjA5MjMtMjIwMCcgXV0gfHwgcmVmdXNlICdOSUdIVF9QTEFOX0lEIG1pc21hdGNoJwpbWyAiJHtNRUFTVVJFTUVOVF9ST09UOi19IiA9PSAnL3RtcC9qd2tpbmRiYXNlJyBdXSB8fCByZWZ1c2UgJ01FQVNVUkVNRU5UX1JPT1QgbWlzbWF0Y2gnCltbICIke01FQVNVUkVNRU5UX0hFQUQ6LX0iID09ICcwYWVkMGRhMzI1YmY2YjRiZWRmNDFlMmMwMmVmZTM0MTQzNzdhOTA2JyBdXSB8fCByZWZ1c2UgJ01FQVNVUkVNRU5UX0hFQUQgbWlzbWF0Y2gnCltbICIkKC91c3IvYmluL3NoYXN1bSAtYSAyNTYgJy90bXAvandraW5kYmFzZS9zY3JpcHRzL25pZ2h0X2NoYWlucy9xdWlldF9wcmVkaWNhdGVfZXZpZGVuY2UuenNoJyB8IC91c3IvYmluL2F3ayAne3ByaW50ICQxfScpIiA9PSAiJEVWSURFTkNFX0NIQUlOX1NPVVJDRV9TSEEyNTYiIF1dIHx8IHJlZnVzZSBjaGFpbl9zb3VyY2Vfc2hhMjU2X21pc21hdGNoCmV4ZWMgL2Jpbi96c2ggJy90bXAvandraW5kYmFzZS9zY3JpcHRzL25pZ2h0X2NoYWlucy9xdWlldF9wcmVkaWNhdGVfZXZpZGVuY2UuenNoJwo=',
    'chain_sha256': 'YjBjYWUzNDg0Y2NiZDMzYmU3YzNmM2E5ODFjYjFkZjNjNTVlYWM2Y2M4MDc3NzQ2NGI1ZTZiZmYxMGMwZDBmMiAgY2hhaW4uenNoCg==',
    'chain_source_sha256': 'NTY4YTI3NzFiMjhkYTlkODA1Y2QyM2ZmNDA1OWJiYmMyN2Q2ZGZhZDFmOGQ5NjAzMzMxYTQxMmUzNzUxYjdlYSAgcXVpZXRfcHJlZGljYXRlX2V2aWRlbmNlLnpzaAo=',
    'manifest': 'ewogICJmaWxlcyI6IHsKICAgICJjb25maWdzL2NhbXBhaWducy9xdWlldF9wcmVkaWNhdGVfZXZpZGVuY2VfMDEvcGlsb3RfcHJvdG9jb2xfdjMuanNvbiI6ICI2OTMyMWM2OTNiMzM3MGI5NDliMGE0YTFiODU0OGUzNWRkMDgxYTM2MTY1YmE4ZjY3OTlhMzg3YzJkODEzNjE2IiwKICAgICJqb3VsZXdpc2UvbmlnaHRfYWdlbnRfaW5zdGFsbC5weSI6ICI3OTQxOTRlZjcxMmVlNWJiZGM5NzNjYWYwZWNlNjZlOTZjNjA1ZGQ3Y2Q4YTUyMzZiZGJhZDA5NzhjYjc3MWNiIiwKICAgICJqb3VsZXdpc2UvbmlnaHRfZ2F0ZS5weSI6ICJhMTU4ODA4MTZlNjE1Mzc0YTFmNDkzMjA4OWZjZDg4ZWJjNzRiOWI4YzZkMTRmMGM3MjYwOTdhM2I2OGY5NmEyIiwKICAgICJqb3VsZXdpc2UvcXVpZXRfYWRtaXNzaW9uLnB5IjogIjc5ZTEyZDJiNmNlOGZlYzczOWMyM2RlZDM2ZWU3MTI3ZmMxYjIyYjRiN2RjZjc0NjgyNTNlYWViYjYzMmRiMjIiLAogICAgImpvdWxld2lzZS9xdWlldF9wcmVkaWNhdGVfY2FtcGFpZ24ucHkiOiAiMThmOGEzNDhmOTc0ZWUwZDQ2NTc5OGFmNTAwY2ZhYWZjYWI4ZTMxZTIyMzFjMzQ4YTVjZWY0YjI3ZjYyMWEwOSIsCiAgICAic2NyaXB0cy9uaWdodF9jaGFpbnMvcXVpZXRfcHJlZGljYXRlX2V2aWRlbmNlLnpzaCI6ICI1NjhhMjc3MWIyOGRhOWQ4MDVjZDIzZmY0MDU5YmJiYzI3ZDZkZmFkMWY4ZDk2MDMzMzFhNDEyZTM3NTFiN2VhIiwKICAgICJzY3JpcHRzL3J1bl9uaWdodC5weSI6ICIyYTliODQ4YWVjNjNhNzJhNTY3OTg3NjQ4OTEwY2E5NDY0MWNhN2U1NTNmMjljNzgxYjljMmQ5MzMyY2RmMDY3IiwKICAgICJzY3JpcHRzL3NhbXBsZV9xdWlldF9wcmVkaWNhdGVfZXZpZGVuY2UucHkiOiAiMGM1ZWU1NWQxNjYxOGFlNGNlZjYxYzI3YTM1NTQxYWFiOTBjYzAyNDgxYzdlYjEyZWJiN2IwNzBjMGQ4ZjkzMCIKICB9LAogICJtZWFzdXJlbWVudF9oZWFkIjogIjBhZWQwZGEzMjViZjZiNGJlZGY0MWUyYzAyZWZlMzQxNDM3N2E5MDYiLAogICJwbGFuX2lkIjogInFwZTAxLXBpbG90LW4xLTIwMjYwOTIzLTIyMDAiLAogICJzY2hlbWEiOiAiam91bGV3aXNlLm5pZ2h0X2V2aWRlbmNlX21hbmlmZXN0LnYxIgp9Cg==',
    'manifest_digest': 'M2Y2YjAwMzljMDc5OWJlNGY3OWU1YzRhYjJjMjFlMWFhMTBhYTlkYjhlM2M3N2RlZDAwZGQ4NWI1MzMwZjliYg==',
    'notice': 'RFJBRlQg4oCUIE5PVCBTRU5UOyBwcmVyZXF1aXNpdGVzIGFuZCB2ZXRvIG9ic2VydmF0aW9ucyBhcmUgbm90IHlldCByZWNvcmRlZC4KVG86IGNsYXVkZTIuZ2xhcmluZzYxMEBwYXNzbWFpbC5uZXQKU3ViamVjdDogTklHSFQgTk9USUNFIOKAlCBxcGUwMS1waWxvdC1uMS0yMDI2MDkyMy0yMjAwIChFVklERU5DRTsgRElBR05PU1RJQ19OT19QQUNLKSDigJQgYXR0ZW1wdCAxCgpFZCwKTGF1bmNoIG5lZWRzIG5vIGFjdGlvbiBmcm9tIHlvdSB1bmxlc3MgeW91IHJlcGx5IE5PLiBZb3VyIE5PIG92ZXJyaWRlcy4KQXJtIGF0dGVtcHQgMTsgcHJpb3IgY2FuZGlkYXRlcyBmb3IgdGhpcyBkYXRlOiBub25lLgpUaGlzIGlkbGUtdmFyaWFuY2UgZXZpZGVuY2UgbmlnaHQgc2l6ZXMgYSBsYXRlciBleHBlcmltZW50OyBpdCBhY3RpdmF0ZXMgbm8gbmV3IHF1aWV0bmVzcyBjdXRvZmYuCkFmdGVyIDYwMCBzZWNvbmRzIHNldHRsaW5nLCB0d2VsdmUgNjAwLXNlY29uZCBpZGxlIGVudmVsb3BlcyBzdGFydCA2MjAgc2Vjb25kcyBhcGFydCBhbmQgdXNlIDQ4MC1zZWNvbmQgaW50ZXJpb3JzIGFmdGVyIDYwLXNlY29uZCBvZmZzZXRzLgpQb3dlciBzYW1wbGluZyBpcyBldmVyeSAxMDAgbXMsIHdpdGggY2Vuc3VzLCBBQy1wb3dlciwgdGhlcm1hbCwgdGltaW5nIGFuZCBjbGVhbnVwIG9ic2VydmF0aW9ucyBhbmQgYSBqb3VybmFsIG9mIGJ1c3kgY29yZXMgKHRoZSBhdmVyYWdlIG51bWJlciBvZiBDUFUgY29yZXMgYSBwcm9jZXNzIGtlcHQgYnVzeSkuClRoZSA4LDAyMC1zZWNvbmQgcHJvZ3JhbSBmaXRzIGluc2lkZSB0aGUgOSwwMDAtc2Vjb25kIHdpbmRvdzsgbm8gdG9wLXVwIG9yIGF1dG9tYXRpYyByZXBlYXQuCkEgcHJvY2VzcyBvdXRzaWRlIHRoZSBtZWFzdXJlbWVudCBhcHBhcmF0dXMgKHRoZSBuaWdodCdzIG93biBtZWFzdXJlbWVudCBwcm9jZXNzZXMpIGF0IG9yIGFib3ZlIDAuNSBidXN5IGNvcmVzIHJlZnVzZXMgdGhlIG5pZ2h0IGF0IHRoZSBhcm0gY2hlY2sgKHRoZSBwcmUtYXJtIGNoZWNrcyBydW4gYmVmb3JlIHRoaXMgbm90aWNlIGlzIHNlbnQgYW5kIGJlZm9yZSB0aGUgbmlnaHQgaXMgaW5zdGFsbGVkKSBvciBhdCB0MCwgdGhlIHNjaGVkdWxlZCBzdGFydC4KQSBwcm9jZXNzIG91dHNpZGUgdGhlIG1lYXN1cmVtZW50IGFwcGFyYXR1cyB1c2luZyAzMCBvciBtb3JlIGNvcmUtc2Vjb25kcyAoYnVzeSBjb3JlcyBtdWx0aXBsaWVkIGJ5IHNlY29uZHMpIGluc2lkZSBhbiBlbnZlbG9wZSBleGNsdWRlcyB0aGF0IGVudmVsb3BlLiBUd28gc3VjaCBleGNsdXNpb25zIGluIGEgcm93IGVuZCB0aGUgbmlnaHQuCkF0IHQwIHRoZSBnYXRlIHJlYWRzIGxhdW5jaGQncyBsb2cgZm9yIHRoZSBwcmV2aW91cyB0ZW4gbWludXRlczsgd2hlbiB0aGF0IHJlYWQgc3VjY2VlZHMsIHRoZSBuaWdodCBpcyByZWZ1c2VkIGF0IGl0cyBzdGFydCBpZiBsYXVuY2hkIHNwYXduZWQgdGhlIFdpLUZpIGxvZy1jYXB0dXJlIGhlbHBlciBjb3JlY2FwdHVyZWQgbW9yZSB0aGFuIHR3aWNlIGluIHRoZSBwcmV2aW91cyB0ZW4gbWludXRlcy4gV2hlbiB0aGUgbG9nIGNhbm5vdCBiZSByZWFkLCB0aGUgY291bnQgaXMgcmVjb3JkZWQgYXMgbm90IG1lYXN1cmVkIGFuZCB0aGUgbmlnaHQgY29udGludWVzLgpEdXJpbmcgdGhlIG5pZ2h0LCByZWFkLW9ubHkgZ2l0IHNob3cgY2hlY2tzIHJ1biBpbiB0aGUgbWVhc3VyZW1lbnQgY2xvbmU7IHN1Y2Nlc3NmdWwgcmVzdWx0cyBwdWJsaWNhdGlvbiBjb21taXRzIGFuZCBwdXNoZXMgdGhlbSBmcm9tIGEgc2VwYXJhdGUgcmVzdWx0cyBjbG9uZS4KUGFydGlhbCBvYnNlcnZhdGlvbnMgYW5kIHJlZnVzYWxzIGFyZSBrZXB0LiBObyBtb2RlbCwgbG9hZCBnZW5lcmF0b3IsIGNhbGlicmF0aW9uLWxlZGdlciBzZXNzaW9uIG9yIG1lYXN1cmVtZW50IHBhY2sgcnVucy4KVGhlIHNjaGVkdWxlciBzdXBlcnZpc2VzIHRoZSBwcm9ncmFtIGFuZCB0aGUgY291cmllciBlbWFpbHMgdGhlIHJlc3VsdC4gRXZpZGVuY2UgcmVtYWlucyBQUk9WSVNJT05BTC4KQWZ0ZXIgZGVsaXZlcnkgdGhlIGxlYWQgc2l6ZXMgYmxvY2sgdHdvIG9yIHJlY29yZHMgJ25vIGN1dG9mZiBxdWFsaWZpZXMnLgpwbGFuX2lkOiBxcGUwMS1waWxvdC1uMS0yMDI2MDkyMy0yMjAwCnJlcG9faGVhZCA9IG1lYXN1cmVtZW50X2hlYWQgPSBIOiAwYWVkMGRhMzI1YmY2YjRiZWRmNDFlMmMwMmVmZTM0MTQzNzdhOTA2CmNsb25lOiAvdG1wL2p3a2luZGJhc2UKY3VzdG9keTogL3RtcC9qd2tpbmRmaXh0dXJlL2N1c3RvZHkKcnVuczogL3RtcC9qd2tpbmRmaXh0dXJlL2N1c3RvZHkvcnVucwpzdGFnZWQgcGxhbjogL3RtcC9qd2tpbmRmaXh0dXJlL2N1c3RvZHkvbmlnaHRfcGxhbi5qc29uCmF1dGhvcmVkX2Vwb2NoX3M6IDE3OTAxOTcyMDAKL3RtcC9qd2tpbmRiYXNlL2NvbmZpZ3MvY2FtcGFpZ25zL3F1aWV0X3ByZWRpY2F0ZV9ldmlkZW5jZV8wMS9waWxvdF9wcm90b2NvbF92My5qc29uIHNoYTI1NiA2OTMyMWM2OTNiMzM3MGI5NDliMGE0YTFiODU0OGUzNWRkMDgxYTM2MTY1YmE4ZjY3OTlhMzg3YzJkODEzNjE2Ci90bXAvandraW5kYmFzZS9zY3JpcHRzL25pZ2h0X2NoYWlucy9xdWlldF9wcmVkaWNhdGVfZXZpZGVuY2UuenNoIHNoYTI1NiA1NjhhMjc3MWIyOGRhOWQ4MDVjZDIzZmY0MDU5YmJiYzI3ZDZkZmFkMWY4ZDk2MDMzMzFhNDEyZTM3NTFiN2VhCk5vLW9iamVjdGlvbiBvcGVucyBvbmx5IG9uIG1haWwgc2VydmljZSBhY2NlcHRhbmNlIG9mIHRoZSBleGFjdCBub3RpY2UuIFB1YmxpY2F0aW9uIGZvbGxvd3MgYWNjZXB0YW5jZSB3aXRoIG5vIGFkZGl0aW9uYWwgbWluaW11bSB3YWl0aW5nIGludGVydmFsLgpFdmVyeSBvYnNlcnZlZCBOTyBzdG9wcyBwdWJsaWNhdGlvbiwgaW5jbHVkaW5nIG9sZGVyIHRocmVhZHMuIFJlcGx5IE5PIG9uIHRoZSB0aHJlYWQgb3IgdGhyb3VnaCBhbiBvd25lci1hdXRob3JlZCBkaXJlY3RpdmU7IG5vIHJlcGx5IGlzIHJlcXVpcmVkLgpUaGUgbWFnaXN0cmF0ZSBjaGVja3MgcmVhZGFibGUgTk8vZGlyZWN0aXZlL3N0b3AgY2hhbm5lbHMgYmVmb3JlIHB1YmxpY2F0aW9uIGFuZCBleGl0cyBiZWZvcmUgUkVRVUVTVC4KS2VlcCBhZ2VudCBhcHBsaWNhdGlvbnMgY2xvc2VkIGFuZCB0aGUgbWFjaGluZSB1bnRvdWNoZWQgZnJvbSBSRVFVRVNUIHRocm91Z2ggY29tcGxldGlvbiwgbG9uZ2VyIGlmIHRoZSBuaWdodCByZW1haW5zIGFjdGl2ZS4K',
    'notice_checked': 'UHJlcGFyZWQgY2FuZGlkYXRlIHFwZTAxLXBpbG90LW4xLTIwMjYwOTIzLTIyMDA7IHByZS1hcm0gY2hlY2sgY2NjY2NjY2NjY2NjIGF0IDIwMjYtMDktMjNUMjE6MDE6NDArMDA6MDAKCkVkLApMYXVuY2ggbmVlZHMgbm8gYWN0aW9uIGZyb20geW91IHVubGVzcyB5b3UgcmVwbHkgTk8uIFlvdXIgTk8gb3ZlcnJpZGVzLgpBcm0gYXR0ZW1wdCAxOyBwcmlvciBjYW5kaWRhdGVzIGZvciB0aGlzIGRhdGU6IG5vbmUuClRoaXMgaWRsZS12YXJpYW5jZSBldmlkZW5jZSBuaWdodCBzaXplcyBhIGxhdGVyIGV4cGVyaW1lbnQ7IGl0IGFjdGl2YXRlcyBubyBuZXcgcXVpZXRuZXNzIGN1dG9mZi4KQWZ0ZXIgNjAwIHNlY29uZHMgc2V0dGxpbmcsIHR3ZWx2ZSA2MDAtc2Vjb25kIGlkbGUgZW52ZWxvcGVzIHN0YXJ0IDYyMCBzZWNvbmRzIGFwYXJ0IGFuZCB1c2UgNDgwLXNlY29uZCBpbnRlcmlvcnMgYWZ0ZXIgNjAtc2Vjb25kIG9mZnNldHMuClBvd2VyIHNhbXBsaW5nIGlzIGV2ZXJ5IDEwMCBtcywgd2l0aCBjZW5zdXMsIEFDLXBvd2VyLCB0aGVybWFsLCB0aW1pbmcgYW5kIGNsZWFudXAgb2JzZXJ2YXRpb25zIGFuZCBhIGpvdXJuYWwgb2YgYnVzeSBjb3JlcyAodGhlIGF2ZXJhZ2UgbnVtYmVyIG9mIENQVSBjb3JlcyBhIHByb2Nlc3Mga2VwdCBidXN5KS4KVGhlIDgsMDIwLXNlY29uZCBwcm9ncmFtIGZpdHMgaW5zaWRlIHRoZSA5LDAwMC1zZWNvbmQgd2luZG93OyBubyB0b3AtdXAgb3IgYXV0b21hdGljIHJlcGVhdC4KQSBwcm9jZXNzIG91dHNpZGUgdGhlIG1lYXN1cmVtZW50IGFwcGFyYXR1cyAodGhlIG5pZ2h0J3Mgb3duIG1lYXN1cmVtZW50IHByb2Nlc3NlcykgYXQgb3IgYWJvdmUgMC41IGJ1c3kgY29yZXMgcmVmdXNlcyB0aGUgbmlnaHQgYXQgdGhlIGFybSBjaGVjayAodGhlIHByZS1hcm0gY2hlY2tzIHJ1biBiZWZvcmUgdGhpcyBub3RpY2UgaXMgc2VudCBhbmQgYmVmb3JlIHRoZSBuaWdodCBpcyBpbnN0YWxsZWQpIG9yIGF0IHQwLCB0aGUgc2NoZWR1bGVkIHN0YXJ0LgpBIHByb2Nlc3Mgb3V0c2lkZSB0aGUgbWVhc3VyZW1lbnQgYXBwYXJhdHVzIHVzaW5nIDMwIG9yIG1vcmUgY29yZS1zZWNvbmRzIChidXN5IGNvcmVzIG11bHRpcGxpZWQgYnkgc2Vjb25kcykgaW5zaWRlIGFuIGVudmVsb3BlIGV4Y2x1ZGVzIHRoYXQgZW52ZWxvcGUuIFR3byBzdWNoIGV4Y2x1c2lvbnMgaW4gYSByb3cgZW5kIHRoZSBuaWdodC4KQXQgdDAgdGhlIGdhdGUgcmVhZHMgbGF1bmNoZCdzIGxvZyBmb3IgdGhlIHByZXZpb3VzIHRlbiBtaW51dGVzOyB3aGVuIHRoYXQgcmVhZCBzdWNjZWVkcywgdGhlIG5pZ2h0IGlzIHJlZnVzZWQgYXQgaXRzIHN0YXJ0IGlmIGxhdW5jaGQgc3Bhd25lZCB0aGUgV2ktRmkgbG9nLWNhcHR1cmUgaGVscGVyIGNvcmVjYXB0dXJlZCBtb3JlIHRoYW4gdHdpY2UgaW4gdGhlIHByZXZpb3VzIHRlbiBtaW51dGVzLiBXaGVuIHRoZSBsb2cgY2Fubm90IGJlIHJlYWQsIHRoZSBjb3VudCBpcyByZWNvcmRlZCBhcyBub3QgbWVhc3VyZWQgYW5kIHRoZSBuaWdodCBjb250aW51ZXMuCkR1cmluZyB0aGUgbmlnaHQsIHJlYWQtb25seSBnaXQgc2hvdyBjaGVja3MgcnVuIGluIHRoZSBtZWFzdXJlbWVudCBjbG9uZTsgc3VjY2Vzc2Z1bCByZXN1bHRzIHB1YmxpY2F0aW9uIGNvbW1pdHMgYW5kIHB1c2hlcyB0aGVtIGZyb20gYSBzZXBhcmF0ZSByZXN1bHRzIGNsb25lLgpQYXJ0aWFsIG9ic2VydmF0aW9ucyBhbmQgcmVmdXNhbHMgYXJlIGtlcHQuIE5vIG1vZGVsLCBsb2FkIGdlbmVyYXRvciwgY2FsaWJyYXRpb24tbGVkZ2VyIHNlc3Npb24gb3IgbWVhc3VyZW1lbnQgcGFjayBydW5zLgpUaGUgc2NoZWR1bGVyIHN1cGVydmlzZXMgdGhlIHByb2dyYW0gYW5kIHRoZSBjb3VyaWVyIGVtYWlscyB0aGUgcmVzdWx0LiBFdmlkZW5jZSByZW1haW5zIFBST1ZJU0lPTkFMLgpBZnRlciBkZWxpdmVyeSB0aGUgbGVhZCBzaXplcyBibG9jayB0d28gb3IgcmVjb3JkcyAnbm8gY3V0b2ZmIHF1YWxpZmllcycuCnBsYW5faWQ6IHFwZTAxLXBpbG90LW4xLTIwMjYwOTIzLTIyMDAKcmVwb19oZWFkID0gbWVhc3VyZW1lbnRfaGVhZCA9IEg6IDBhZWQwZGEzMjViZjZiNGJlZGY0MWUyYzAyZWZlMzQxNDM3N2E5MDYKY2xvbmU6IC90bXAvandraW5kYmFzZQpjdXN0b2R5OiAvdG1wL2p3a2luZGZpeHR1cmUvY3VzdG9keQpydW5zOiAvdG1wL2p3a2luZGZpeHR1cmUvY3VzdG9keS9ydW5zCnN0YWdlZCBwbGFuOiAvdG1wL2p3a2luZGZpeHR1cmUvY3VzdG9keS9uaWdodF9wbGFuLmpzb24KYXV0aG9yZWRfZXBvY2hfczogMTc5MDE5NzIwMAovdG1wL2p3a2luZGJhc2UvY29uZmlncy9jYW1wYWlnbnMvcXVpZXRfcHJlZGljYXRlX2V2aWRlbmNlXzAxL3BpbG90X3Byb3RvY29sX3YzLmpzb24gc2hhMjU2IDY5MzIxYzY5M2IzMzcwYjk0OWIwYTRhMWI4NTQ4ZTM1ZGQwODFhMzYxNjViYThmNjc5OWEzODdjMmQ4MTM2MTYKL3RtcC9qd2tpbmRiYXNlL3NjcmlwdHMvbmlnaHRfY2hhaW5zL3F1aWV0X3ByZWRpY2F0ZV9ldmlkZW5jZS56c2ggc2hhMjU2IDU2OGEyNzcxYjI4ZGE5ZDgwNWNkMjNmZjQwNTliYmJjMjdkNmRmYWQxZjhkOTYwMzMzMWE0MTJlMzc1MWI3ZWEKTm8tb2JqZWN0aW9uIG9wZW5zIG9ubHkgb24gbWFpbCBzZXJ2aWNlIGFjY2VwdGFuY2Ugb2YgdGhlIGV4YWN0IG5vdGljZS4gUHVibGljYXRpb24gZm9sbG93cyBhY2NlcHRhbmNlIHdpdGggbm8gYWRkaXRpb25hbCBtaW5pbXVtIHdhaXRpbmcgaW50ZXJ2YWwuCkV2ZXJ5IG9ic2VydmVkIE5PIHN0b3BzIHB1YmxpY2F0aW9uLCBpbmNsdWRpbmcgb2xkZXIgdGhyZWFkcy4gUmVwbHkgTk8gb24gdGhlIHRocmVhZCBvciB0aHJvdWdoIGFuIG93bmVyLWF1dGhvcmVkIGRpcmVjdGl2ZTsgbm8gcmVwbHkgaXMgcmVxdWlyZWQuClRoZSBtYWdpc3RyYXRlIGNoZWNrcyByZWFkYWJsZSBOTy9kaXJlY3RpdmUvc3RvcCBjaGFubmVscyBiZWZvcmUgcHVibGljYXRpb24gYW5kIGV4aXRzIGJlZm9yZSBSRVFVRVNULgpLZWVwIGFnZW50IGFwcGxpY2F0aW9ucyBjbG9zZWQgYW5kIHRoZSBtYWNoaW5lIHVudG91Y2hlZCBmcm9tIFJFUVVFU1QgdGhyb3VnaCBjb21wbGV0aW9uLCBsb25nZXIgaWYgdGhlIG5pZ2h0IHJlbWFpbnMgYWN0aXZlLgo=',
    'plan': 'ewogICJhdXRob3JlZF9lcG9jaF9zIjogMTc5MDE5NzIwMCwKICAiY2hhaW5fcGF0aCI6ICIvdG1wL2p3a2luZGZpeHR1cmUvY3VzdG9keS9jaGFpbi56c2giLAogICJjaGFpbl9zaGEyNTZfcGF0aCI6ICIvdG1wL2p3a2luZGZpeHR1cmUvY3VzdG9keS9jaGFpbi56c2guc2hhMjU2IiwKICAiY3VzdG9keV9yb290IjogIi90bXAvandraW5kZml4dHVyZS9jdXN0b2R5IiwKICAibWVhc3VyZW1lbnRfaGVhZCI6ICIwYWVkMGRhMzI1YmY2YjRiZWRmNDFlMmMwMmVmZTM0MTQzNzdhOTA2IiwKICAibWVhc3VyZW1lbnRfcm9vdCI6ICIvdG1wL2p3a2luZGJhc2UiLAogICJwbGFuX2lkIjogInFwZTAxLXBpbG90LW4xLTIwMjYwOTIzLTIyMDAiLAogICJyZWNlaXB0X2NsYXNzIjogIkRJQUdOT1NUSUNfTk9fUEFDSyIsCiAgInJlZ2lzdHJhdGlvbl9wYXRoIjogImNvbmZpZ3MvY2FtcGFpZ25zL3F1aWV0X3ByZWRpY2F0ZV9ldmlkZW5jZV8wMS9waWxvdF9wcm90b2NvbF92My5qc29uIiwKICAicmVwb19oZWFkIjogIjBhZWQwZGEzMjViZjZiNGJlZGY0MWUyYzAyZWZlMzQxNDM3N2E5MDYiLAogICJzY2hlbWEiOiAiam91bGV3aXNlLm5pZ2h0X3BsYW4udjIiLAogICJzY2hlbWFfdmVyc2lvbiI6IDIsCiAgInQwX2Vwb2NoX3MiOiAxNzkwMjAwODAwLAogICJ3aW5kb3dfbWF4X3MiOiA5MDAwCn0K',
}


def ensure_base_source():
    if (BASE_SOURCE / ".git").is_dir():
        return
    BASE_SOURCE.mkdir(parents=True, exist_ok=True)
    archive = subprocess.check_output(["git", "-C", str(ROOT), "archive", "cdc05e9b"])
    with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
        if sys.version_info >= (3, 12):
            stream.extractall(BASE_SOURCE, filter="data")
        else:
            stream.extractall(BASE_SOURCE)
    subprocess.run(["git", "-C", str(BASE_SOURCE), "init", "-q"], check=True)
    subprocess.run(["git", "-C", str(BASE_SOURCE), "-c", "core.autocrlf=false",
                    "add", "-A"], check=True)
    env = dict(os.environ, GIT_AUTHOR_NAME="Fixture", GIT_AUTHOR_EMAIL="fixture@example.invalid",
               GIT_COMMITTER_NAME="Fixture", GIT_COMMITTER_EMAIL="fixture@example.invalid",
               GIT_AUTHOR_DATE="2026-09-23T00:00:00+00:00",
               GIT_COMMITTER_DATE="2026-09-23T00:00:00+00:00")
    subprocess.run(["git", "-C", str(BASE_SOURCE), "-c", "commit.gpgsign=false",
                    "-c", "core.hooksPath=/dev/null",
                    "commit", "-qm", "fixture"], check=True, env=env)


def render_fixture():
    ensure_base_source()
    os.environ["TZ"] = "UTC"
    if hasattr(time, "tzset"):
        time.tzset()
    if FIXTURE.exists():
        shutil.rmtree(FIXTURE)
    FIXTURE.mkdir()
    measurement = BASE_SOURCE
    custody = FIXTURE / "custody"
    custody.mkdir()
    head = subprocess.check_output(
        ["git", "-C", str(measurement), "rev-parse", "HEAD"], text=True).strip()
    plan = night_gate.NightPlan(
        plan_id="qpe01-pilot-n1-20260923-2200", receipt_class="DIAGNOSTIC_NO_PACK",
        t0_epoch_s=1790200800, window_max_s=9000, authored_epoch_s=1790197200,
        repo_head=head, measurement_root=str(measurement), measurement_head=head,
        chain_path=str(custody / "chain.zsh"),
        chain_sha256_path=str(custody / "chain.zsh.sha256"), custody_root=str(custody),
        registration_path=night_gate.QPE01_PILOT_REGISTRATION_PATH,
    )
    plan_path = custody / "night_plan.json"
    write_night_plan(plan_path, plan)
    plan_bytes = plan_path.read_bytes()
    manifest = quiet_predicate_campaign.manifest_for(plan)
    gen_evidence_night.generate(plan_path)
    python = measurement / ".venv/bin/python"
    python.parent.mkdir(parents=True, exist_ok=True)
    if not python.exists():
        python.symlink_to(sys.executable)
    sealed = evidence_night.sealed_candidate(measurement, plan_path)
    assert sealed["chain_source_sha256"] == manifest["files"][night_gate.EVIDENCE_CHAIN_PATH]
    registration = measurement / night_gate.QPE01_PILOT_REGISTRATION_PATH
    source = measurement / night_gate.EVIDENCE_CHAIN_PATH
    state = {
        "kind": "quiet_predicate_evidence", "plan_id": plan.plan_id,
        "attempt": 1, "prior_candidates": [], "head": head,
        "measurement_root": str(measurement), "custody_root": str(custody),
        "plan_path": str(plan_path), "digests": {},
        "schedule": {"boundaries": {}, "install_spans_today": []},
        "bindings": {
            "registration_path": str(registration),
            "registration_sha256": hashlib.sha256(registration.read_bytes()).hexdigest(),
            "chain_source_path": str(source),
            "chain_source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        },
    }
    artifacts = {
        "plan": plan_bytes,
        "chain": (custody / "chain.zsh").read_bytes(),
        "chain_sha256": (custody / "chain.zsh.sha256").read_bytes(),
        "chain_source_sha256": (custody / "chain.zsh.chain-source.sha256").read_bytes(),
        "manifest": (custody / "evidence_manifest.json").read_bytes(),
        "manifest_digest": hashlib.sha256((custody / "evidence_manifest.json").read_bytes()).hexdigest().encode(),
        "notice": evidence_night.render_notice(state).encode(),
        "notice_checked": evidence_night.render_notice(
            state, checked={"finished_epoch_s": 1790197300}, check_sha256="c" * 64).encode(),
    }
    assert manifest == json.loads(artifacts["manifest"])
    return artifacts


def refusal_fixture():
    results = {}
    for kind in ("unknown_kind", "calibration"):
        try:
            evidence_night.prepare(kind=kind, t0="next")
        except Exception as exc:
            results[kind] = (type(exc).__name__, str(exc))
    roots = FIXTURE.resolve() / "roots"
    stages = FIXTURE.resolve() / "stages"
    epoch = 1790200800
    head = "a" * 40
    fields = evidence_night.locations(roots, stages, epoch, head)
    stage = Path(fields["staging"])
    stage.mkdir(parents=True)
    state = dict(fields, schema=evidence_night.SCHEMA, kind="quiet_predicate_evidence",
                 roots_under=str(roots), t0=epoch, head=head,
                 plan_path=str(stage / "night_plan.json"),
                 steps=[{"step": step} for step in evidence_night.STEPS])
    state["plan_id"] = "wrong-prefix-20260923-2200"
    (stage / "prepare.json").write_text(json.dumps(state))
    try:
        evidence_night.candidate_state(stage)
    except Exception as exc:
        results["wrong_prefix"] = (type(exc).__name__, str(exc))
    return results


class NightKindTests(unittest.TestCase):
    def test_rows_and_unknown_kind(self):
        self.assertEqual(set(NIGHT_KINDS), {"quiet_predicate_evidence", "calibration"})
        self.assertIs(night_gate.NIGHT_KINDS, NIGHT_KINDS)
        idle = kind_row("quiet_predicate_evidence")
        calibration = kind_row("calibration")
        self.assertIs(idle, NIGHT_KINDS["quiet_predicate_evidence"])
        self.assertEqual(idle.plan_id_prefix, "qpe01-pilot-n1-")
        self.assertEqual(idle.measurement_root_suffix, "qpe01-pilot-n1")
        self.assertEqual(idle.window_max_s, 9000)
        self.assertEqual(idle.generator_script, "scripts/gen_evidence_night.py")
        self.assertTrue(idle.authenticate_chain_source)
        self.assertTrue(idle.requires_chain_bound_registration)
        self.assertTrue(idle.corecaptured_at_arm_and_t0)
        self.assertTrue(idle.non_observer_at_arm_and_t0)
        self.assertEqual(calibration.chain_source_path,
                         "scripts/night_chains/calibration_derivation_only.zsh")
        self.assertIsNone(calibration.manifest_for)
        self.assertIsNone(calibration.generator_script)
        self.assertFalse(calibration.authenticate_chain_source)
        self.assertFalse(calibration.requires_chain_bound_registration)
        self.assertFalse(calibration.corecaptured_at_arm_and_t0)
        self.assertFalse(calibration.non_observer_at_arm_and_t0)
        with self.assertRaises(UnknownNightKind):
            kind_row("unknown_kind")
        with self.assertRaises(TypeError):
            NIGHT_KINDS["other"] = None
        with self.assertRaises(FrozenInstanceError):
            idle.kind = "other"

    def test_base_archive_byte_goldens(self):
        actual = render_fixture()
        self.assertEqual(set(actual), set(GOLDENS))
        for name, raw in actual.items():
            with self.subTest(name=name):
                self.assertEqual(raw, base64.b64decode(GOLDENS[name]))

    def test_refusal_parity(self):
        render_fixture()
        self.assertEqual(refusal_fixture(), {
            "unknown_kind": ("Refused", "invalid or unresolved kind"),
            "calibration": ("Refused", "invalid or unresolved kind"),
            "wrong_prefix": ("Refused", "candidate is not a completed, owned preparation"),
        })


if __name__ == "__main__" and "--dump-goldens" in sys.argv:
    payload = {name: base64.b64encode(raw).decode() for name, raw in render_fixture().items()}
    print(json.dumps(payload, sort_keys=True))
