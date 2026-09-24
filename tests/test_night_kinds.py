"""Byte and refusal parity for the two-kind table.

The goldens are retained cdc05e9b archive outputs. Their fixed /tmp paths
are relocated to each unique fixture before comparing bytes and digests.
The archived measurement source stays fixed; candidate-head preparation is
proved separately through the real prepare path.
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
import tempfile
import time
import unittest
from unittest import mock
from dataclasses import replace
from types import MappingProxyType
from types import SimpleNamespace

from joulewise import evidence_night, night_gate, quiet_predicate_campaign
from joulewise import night_kinds
try:
    from joulewise.night_kinds import NIGHT_KINDS, UnknownNightKind, kind_row
except ModuleNotFoundError:  # The base archive intentionally predates the table.
    NIGHT_KINDS, UnknownNightKind, kind_row = {}, ValueError, None
from joulewise.night_plan_writer import write_night_plan
from scripts import gen_evidence_night

from tests.git_fixture import init_git_fixture
from tests.test_evidence_night import _census_clean_tempdir


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = None
BASE_SOURCE = None
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
    init_git_fixture(BASE_SOURCE, "-q")
    subprocess.run(["git", "-C", str(BASE_SOURCE), "-c", "core.autocrlf=false",
                    "add", "-A"], check=True)
    commit_fixture(BASE_SOURCE, "fixture")


def commit_fixture(source, message):
    env = dict(os.environ, GIT_AUTHOR_NAME="Fixture", GIT_AUTHOR_EMAIL="fixture@example.invalid",
               GIT_COMMITTER_NAME="Fixture", GIT_COMMITTER_EMAIL="fixture@example.invalid",
               GIT_AUTHOR_DATE="2026-09-23T00:00:00+00:00",
               GIT_COMMITTER_DATE="2026-09-23T00:00:00+00:00")
    subprocess.run(["git", "-C", str(source), "-c", "commit.gpgsign=false",
                    "-c", "core.hooksPath=/dev/null",
                    "commit", "-qm", message], check=True, env=env)


def render_fixture():
    ensure_base_source()
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
    # The fixed measurement H is the archived base commit. It predates the
    # table, so supply only that new tracked file to the current authoring
    # code. All pre-existing paths still come from H through tracked_bytes.
    original_tracked_bytes = quiet_predicate_campaign.tracked_bytes
    def tracked_bytes(root, head, name):
        if name == "joulewise/night_kinds.py":
            return (ROOT / name).read_bytes()
        return original_tracked_bytes(root, head, name)
    with mock.patch.object(quiet_predicate_campaign, "tracked_bytes", side_effect=tracked_bytes):
        manifest = quiet_predicate_campaign.manifest_for(plan)
        gen_evidence_night.generate(plan_path)
    python = measurement / ".venv/bin/python"
    python.parent.mkdir(parents=True, exist_ok=True)
    if not python.exists():
        python.symlink_to(sys.executable)
    # The base archive's sealed_candidate can verify its own base manifest.
    # Current-code sealing against a current H is covered by the integration
    # tests; the fixed-H authoring comparison here isolates the manifest delta.
    if kind_row is None:
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
    def setUp(self):
        global FIXTURE, BASE_SOURCE
        # Same hermetic pattern as tests.test_evidence_night.PrepareTests: a
        # census-clean, symlink-free fixture root, and a courier stub on PATH
        # (the real prepare path checks `command -v claude`; the stub must never run).
        self._fixture_dir = _census_clean_tempdir(
            prefix="jwkind-", dir="/private/tmp" if Path("/private/tmp").is_dir() else "/tmp")
        FIXTURE = Path(self._fixture_dir.name).resolve()
        BASE_SOURCE = FIXTURE / "base"
        stub_bin = FIXTURE / "bin"
        stub_bin.mkdir()
        courier = stub_bin / "claude"
        courier.write_text("#!/bin/sh\necho 'courier must not run' >&2\nexit 99\n")
        courier.chmod(0o755)
        self._path_patch = mock.patch.dict(
            os.environ, {"PATH": str(stub_bin) + os.pathsep + os.environ.get("PATH", "")})
        self._path_patch.start()
        self.old_tz = os.environ.get("TZ")
        os.environ["TZ"] = "UTC"
        if hasattr(time, "tzset"):
            time.tzset()

    def tearDown(self):
        if self.old_tz is None:
            os.environ.pop("TZ", None)
        else:
            os.environ["TZ"] = self.old_tz
        if hasattr(time, "tzset"):
            time.tzset()
        self._path_patch.stop()
        self._fixture_dir.cleanup()

    def test_fixture_is_unique_and_local_to_one_run(self):
        self.assertTrue(FIXTURE.name.startswith("jwkind-"))
        self.assertEqual(BASE_SOURCE.parent, FIXTURE)
        self.assertTrue(FIXTURE.is_dir())

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
        self.assertTrue(idle.payload_kind)
        self.assertFalse(calibration.payload_kind)
        self.assertEqual(idle.handler, "evidence")
        self.assertEqual(idle.manifest_name, "evidence_manifest.json")
        self.assertEqual(idle.wrapper_prefix, "EVIDENCE")
        self.assertTrue(idle.successor_release)
        self.assertEqual(calibration.handler, "calibration")
        self.assertIsNone(calibration.plan_id_prefix)
        self.assertIsNone(calibration.measurement_root_suffix)
        with self.assertRaises(UnknownNightKind):
            kind_row("unknown_kind")
        with self.assertRaises(TypeError):
            NIGHT_KINDS["other"] = None
        with self.assertRaises(FrozenInstanceError):
            idle.kind = "other"

    def test_base_archive_byte_goldens(self):
        self.assert_prepared_candidate_head()
        actual = render_fixture()
        self.assertEqual(set(actual), set(GOLDENS))
        base = {name: base64.b64decode(raw) for name, raw in GOLDENS.items()}
        old_chain = base["chain"]
        old_wrapper_digest = hashlib.sha256(old_chain).hexdigest().encode()
        for name, raw in base.items():
            base[name] = (raw.replace(b"/tmp/jwkindbase", str(BASE_SOURCE).encode())
                          .replace(b"/tmp/jwkindfixture", str(FIXTURE).encode()))
        relocated_wrapper_digest = hashlib.sha256(base["chain"]).hexdigest().encode()
        base["chain_sha256"] = base["chain_sha256"].replace(old_wrapper_digest, relocated_wrapper_digest)
        old_manifest = json.loads(base["manifest"])
        new_manifest = json.loads(actual["manifest"])
        added = "joulewise/night_kinds.py"
        self.assertEqual(set(new_manifest), set(old_manifest))
        self.assertEqual({k: v for k, v in new_manifest.items() if k != "files"},
                         {k: v for k, v in old_manifest.items() if k != "files"})
        self.assertEqual(new_manifest["files"], old_manifest["files"] | {
            added: hashlib.sha256((ROOT / added).read_bytes()).hexdigest()})
        self.assertEqual(actual["manifest"],
                         (json.dumps(new_manifest, sort_keys=True, indent=2) + "\n").encode())
        old_digest = hashlib.sha256(base["manifest"]).hexdigest().encode()
        new_digest = hashlib.sha256(actual["manifest"]).hexdigest().encode()
        self.assertEqual(base["manifest_digest"], old_digest)
        self.assertEqual(actual["manifest_digest"], new_digest)
        expected_chain = base["chain"].replace(old_digest, new_digest)
        self.assertIn(old_digest, base["chain"])
        self.assertEqual(actual["chain"], expected_chain)
        old_wrapper_digest = hashlib.sha256(base["chain"]).hexdigest().encode()
        new_wrapper_digest = hashlib.sha256(expected_chain).hexdigest().encode()
        self.assertIn(old_wrapper_digest, base["chain_sha256"])
        for name in set(actual) - {"manifest", "manifest_digest"}:
            with self.subTest(name=name):
                expected = base[name].replace(old_digest, new_digest)
                expected = expected.replace(old_wrapper_digest, new_wrapper_digest)
                self.assertEqual(actual[name], expected)

    def test_refusal_parity(self):
        render_fixture()
        self.assertEqual(refusal_fixture(), {
            "unknown_kind": ("Refused", "invalid or unresolved kind"),
            "calibration": ("Refused", "invalid or unresolved kind"),
            "wrong_prefix": ("Refused", "candidate is not a completed, owned preparation"),
        })

    def test_probe_accepts_a_registered_third_payload_kind(self):
        third = replace(kind_row("quiet_predicate_evidence"), kind="scored_campaign")
        table = MappingProxyType(dict(NIGHT_KINDS, scored_campaign=third))
        with mock.patch.object(night_gate, "NIGHT_KINDS", table):
            self.assertEqual(night_gate.probe_payload_kind(
                "export NIGHT_PAYLOAD_KIND=scored_campaign\n"), "scored_campaign")
            for text in ("export NIGHT_PAYLOAD_KIND=unknown\n",
                         "export NIGHT_PAYLOAD_KIND=scored_campaign\nexport NIGHT_PAYLOAD_KIND=scored_campaign\n",
                         "export NIGHT_PAYLOAD_KIND=scored_campaign\nexport CALIBRATION_LEDGER=x\n"):
                with self.subTest(text=text), self.assertRaisesRegex(ValueError, "probe payload kind ambiguous"):
                    night_gate.probe_payload_kind(text)

    def test_unhandled_third_row_routes_or_refuses_across_shared_entries(self):
        from joulewise import night_agent_install, zero_capture_facts
        from scripts import run_night
        from tests.test_night_gate import FakeProbeSource, make_plan

        render_fixture()
        third = replace(kind_row("quiet_predicate_evidence"),
                        kind="test_night", plan_id_prefix="test-night-",
                        measurement_root_suffix="test-night",
                        chain_source_path="scripts/night_chains/test_night.zsh",
                        receipt_class="TEST_CLASS", manifest_name="test_manifest.json",
                        handler=None, successor_release=False,
                        notice_subject_label="TEST")
        table = MappingProxyType(dict(NIGHT_KINDS, test_night=third))
        custody = FIXTURE / "custody"
        plan_path = custody / "night_plan.json"
        plan = night_gate.NightPlan.from_mapping(json.loads(plan_path.read_text()))
        source = BASE_SOURCE / third.chain_source_path
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("test chain source\n")
        sha = hashlib.sha256(source.read_bytes()).hexdigest()
        chain = custody / "chain.zsh"
        chain.write_text(f"export NIGHT_PAYLOAD_KIND={third.kind}\n"
                         f"export EVIDENCE_CHAIN_SOURCE_SHA256={sha}\n")
        (custody / "chain.zsh.sha256").write_text(
            f"{hashlib.sha256(chain.read_bytes()).hexdigest()}  chain.zsh\n")
        state = {"custody_root": str(custody), "measurement_root": str(BASE_SOURCE),
                 "plan_id": "test-night-1", "attempt": 1,
                 "bindings": {"chain_source_path": str(source), "chain_source_sha256": sha}}
        with mock.patch.object(night_kinds, "NIGHT_KINDS", table), \
                mock.patch.object(evidence_night, "NIGHT_KINDS", table), \
                mock.patch.object(night_gate, "NIGHT_KINDS", table), \
                mock.patch.object(gen_evidence_night, "NIGHT_KINDS", table):
            self.assertEqual(night_gate.probe_payload_kind(chain.read_text()), third.kind)
            with self.assertRaisesRegex(ValueError, "probe payload kind ambiguous"):
                night_gate.probe_payload_kind("export NIGHT_PAYLOAD_KIND=unknown_test\n")
            paths = evidence_night.locations(FIXTURE, FIXTURE / "stages", 1790200800,
                                             "a" * 40, third.kind)
            self.assertTrue(paths["plan_id"].startswith(third.plan_id_prefix))
            stage = Path(paths["staging"])
            stage.mkdir(parents=True)
            (stage / "prepare.json").write_text(json.dumps({"schema": evidence_night.SCHEMA,
                                                               "kind": third.kind}))
            state.update(staging=str(stage), t0=1790200800, head="a" * 40)
            self.assertEqual(len(evidence_night.prior_records(stage.parent, FIXTURE, third.kind)), 1)
            with self.assertRaisesRegex(evidence_night.Refused, "invalid or unresolved kind"):
                evidence_night.prepare(kind=third.kind, t0="next")
            with self.assertRaisesRegex(evidence_night.Refused, "completed, owned preparation"):
                evidence_night.candidate_state(stage)
            self.assertIn("(TEST; TEST_CLASS)", evidence_night.notice_subject(state))
            with self.assertRaisesRegex(evidence_night.Refused, "no approved evidence handler"):
                evidence_night.render_notice(state)
            sibling = stage.with_name(stage.name + "-other")
            journal = sibling / "lifecycle/attempts.json"
            journal.parent.mkdir(parents=True)
            journal.write_text(json.dumps({"notice_accepted": "used-test-notice"}))
            with self.assertRaisesRegex(evidence_night.Refused, "notice id already used"):
                evidence_night.notice_unused(state, "used-test-notice")
            state["digests"] = {str(stage / "night_plan.json"): "0" * 64,
                                str(BASE_SOURCE / "env/mac-measurement-lock.txt"): "0" * 64,
                                str(custody / "chain.zsh"): "0" * 64,
                                str(custody / "chain.zsh.sha256"): "0" * 64,
                                str(custody / "chain.zsh.chain-source.sha256"): "0" * 64,
                                str(custody / third.manifest_name): "0" * 64}
            with self.assertRaisesRegex(evidence_night.Refused, "unknown or missing render output"):
                evidence_night.sealed_state(state)
            from tests.test_arm_census import observation, row as census_row
            observed = observation(census_row(20, 1, "/bin/claude"),
                                   census_row(90, 20, "/bin/python3"), hits=(20,))
            census = evidence_night.clone_census(state, 90, observed)
            self.assertEqual(census["classification"]["receipt_class"], third.receipt_class)
            with self.assertRaisesRegex(gen_evidence_night.GenerationRefusal, "alternate chain refused"):
                gen_evidence_night.generate(plan_path, chain_template=third.chain_source_path)

            wrapper = "export NIGHT_PAYLOAD_KIND=test_night\n"
            probe = FakeProbeSource(chain_text=wrapper)
            receipt = night_gate.evaluate_night(make_plan(), probe.probes())
            c5 = next(item for item in receipt.conditions if item.condition_id == "C5")
            c3 = next(item for item in receipt.conditions if item.condition_id == "C3")
            self.assertNotEqual(c5.status, "PASS")
            self.assertNotIn("payload_kind", c5.measured)
            self.assertNotIn("corecaptured", c3.measured)
            self.assertEqual(probe.observation_calls, 0)
            self.assertEqual(receipt.refusal.reason, "night_chain_digest_mismatch")
            self.assertEqual(night_gate.RULED_REGISTRATIONS.get("test_night"), None)

            prepared = SimpleNamespace(plan=plan, plan_path=plan_path)
            with self.assertRaisesRegex(night_agent_install.Refused, "no approved probe handler"):
                night_agent_install.validate_probe_receipt(prepared)
            render_args = SimpleNamespace(plan=plan_path, python=sys.executable,
                                          render_only=FIXTURE / "rendered", hour=None, minute=None)
            fake_prepared = SimpleNamespace(custody_night=FIXTURE / "empty-night",
                                            admit=lambda *args, **kwargs: None)
            completed = subprocess.CompletedProcess([], 0, stdout=plan.repo_head + "\n")
            with mock.patch.object(night_agent_install.subprocess, "run", return_value=completed), \
                    mock.patch.object(night_agent_install.shutil, "which", return_value="/bin/true"), \
                    mock.patch.object(run_night, "schedule", return_value={"night_calendar": {}}), \
                    mock.patch.object(night_agent_install, "Prepared", return_value=fake_prepared), \
                    mock.patch.object(night_agent_install.time, "time", return_value=plan.authored_epoch_s + 60):
                with self.assertRaisesRegex(night_agent_install.Refused, "no approved render handler"):
                    night_agent_install.validate_install(render_args, BASE_SOURCE)
            receipt_path = FIXTURE / "third-probe.json"
            progress_path = FIXTURE / "third-progress.json"
            self.assertEqual(run_night._probe_worker(plan_path, receipt_path, progress_path,
                                                      time.time() + 60), 2)
            self.assertIn("no approved probe handler", receipt_path.read_text())
            with self.assertRaisesRegex(ValueError, "no approved artifact handler"):
                run_night._artifact_list(custody, custody / "night", plan)
            with self.assertRaisesRegex(ValueError, "no approved courier handler"):
                run_night._courier_argv(custody, plan, FIXTURE / "courier")
            night = custody / "night"
            night.mkdir(exist_ok=True)
            (night / "chain.started").write_text("{}")
            (night / "receipt.json").write_text(json.dumps({"plan_id": plan.plan_id,
                "conditions": [{"condition_id": "C5", "status": "PASS",
                                "measured": {"payload_kind": third.kind}}]}))
            with mock.patch.object(night_gate, "validate_receipt", return_value=[]):
                self.assertEqual(run_night._evidence_cleanup_error(plan, night),
                                 "night payload kind has no approved cleanup handler")
            (night / "courier.sent").write_text("delivered")
            (night / "result.json").write_text("{}")
            self.assertFalse(zero_capture_facts.zero_capture_facts(plan).clean)

    def test_third_row_notice_text_and_corecaptured_flag(self):
        render_fixture()
        third = replace(kind_row("quiet_predicate_evidence"), kind="test_night",
                        notice_subject_label="TEST", notice_intro="Test-only notice intro.",
                        corecaptured_at_arm_and_t0=False)
        table = MappingProxyType(dict(NIGHT_KINDS, test_night=third))
        custody = FIXTURE / "custody"
        chain = custody / "chain.zsh"
        chain.write_text(chain.read_text().replace(
            "NIGHT_PAYLOAD_KIND=quiet_predicate_evidence", "NIGHT_PAYLOAD_KIND=test_night"))
        (custody / "chain.zsh.sha256").write_text(
            f"{hashlib.sha256(chain.read_bytes()).hexdigest()}  chain.zsh\n")
        plan_path = custody / "night_plan.json"
        plan = json.loads(plan_path.read_text())
        source = BASE_SOURCE / third.chain_source_path
        registration = BASE_SOURCE / third.protocol_path
        state = dict(plan_id=plan["plan_id"], attempt=1, prior_candidates=[],
                     head=plan["measurement_head"], measurement_root=str(BASE_SOURCE),
                     custody_root=str(custody), plan_path=str(plan_path), digests={},
                     schedule={"boundaries": {}, "install_spans_today": []},
                     bindings={"chain_source_path": str(source),
                               "chain_source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                               "registration_path": str(registration),
                               "registration_sha256": hashlib.sha256(registration.read_bytes()).hexdigest()})
        with mock.patch.object(night_kinds, "NIGHT_KINDS", table), \
                mock.patch.object(night_gate, "NIGHT_KINDS", table):
            notice = evidence_night.render_notice(state)
        self.assertIn("(TEST; DIAGNOSTIC_NO_PACK)", notice)
        self.assertIn("Test-only notice intro.", notice)
        self.assertNotIn("At t0 the gate reads launchd's log", notice)

    def test_third_row_generator_selects_manifest_executor_and_literals(self):
        render_fixture()
        source_name = "scripts/night_chains/test_night.zsh"
        source = BASE_SOURCE / source_name
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("export NIGHT_PAYLOAD_KIND=test_night\n")
        source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
        third = replace(kind_row("quiet_predicate_evidence"), kind="test_night",
                        chain_source_path=source_name, manifest_name="test_manifest.json",
                        wrapper_prefix="TEST", executor_module="joulewise.test_executor",
                        manifest_for=lambda plan: {"files": {source_name: source_sha}},
                        successor_release=False)
        table = MappingProxyType(dict(NIGHT_KINDS, test_night=third))
        old_plan = night_gate.NightPlan.from_mapping(json.loads(
            (FIXTURE / "custody/night_plan.json").read_text()))
        custody = FIXTURE / "test-custody"
        custody.mkdir()
        target = custody / "chain.zsh"
        plan = replace(old_plan, custody_root=str(custody), chain_path=str(target),
                       chain_sha256_path=str(target) + ".sha256")
        plan_path = custody / "night_plan.json"
        write_night_plan(plan_path, plan)
        with mock.patch.object(night_kinds, "NIGHT_KINDS", table), \
                mock.patch.object(night_gate, "NIGHT_KINDS", table), \
                mock.patch.object(gen_evidence_night, "NIGHT_KINDS", table):
            self.assertEqual(gen_evidence_night.generate(
                plan_path, chain_template=source_name), target)
        wrapper = target.read_text()
        self.assertIn("export NIGHT_PAYLOAD_KIND=test_night\n", wrapper)
        self.assertIn("export TEST_MANIFEST_PATH=", wrapper)
        self.assertIn("$TEST_CHAIN_SOURCE_SHA256", wrapper)
        self.assertIn("-m joulewise.test_executor refuse", wrapper)
        self.assertTrue((custody / third.manifest_name).is_file())

    def test_calibration_cannot_supply_preparation_paths(self):
        with self.assertRaisesRegex(evidence_night.Refused, "no preparation path identity"):
            evidence_night.locations(FIXTURE, FIXTURE / "stages", 1790200800,
                                     "a" * 40, kind="calibration")

    def test_generator_exports_manifest_for(self):
        self.assertIs(gen_evidence_night.manifest_for, quiet_predicate_campaign.manifest_for)

    def test_manifest_verifier_uses_row_kind(self):
        row = replace(kind_row("quiet_predicate_evidence"), kind="scored_campaign")
        manifest = {"files": {quiet_predicate_campaign.CHAIN_PATH: "a" * 64}}
        path = FIXTURE / "manifest.json"
        raw = json.dumps(manifest).encode()
        path.write_bytes(raw)
        chain = (f"export EVIDENCE_MANIFEST_PATH={path}\n"
                 f"export EVIDENCE_MANIFEST_SHA256={hashlib.sha256(raw).hexdigest()}\n"
                 f"export EVIDENCE_CHAIN_SOURCE_SHA256={'a' * 64}\n")
        with mock.patch.object(quiet_predicate_campaign, "kind_row", return_value=row), \
                mock.patch.object(night_gate, "probe_payload_kind", return_value=row.kind), \
                mock.patch.object(quiet_predicate_campaign, "manifest_for", return_value=manifest):
            self.assertEqual(quiet_predicate_campaign.verify_manifest(None, chain)[1], manifest)

    def test_generator_uses_calibration_basename_from_row(self):
        render_fixture()
        plan_path = FIXTURE / "custody/night_plan.json"
        chain = FIXTURE / "custody/chain.zsh"
        chain.write_text("alternate_calibration.zsh\n")
        calibration = replace(kind_row("calibration"),
                              chain_source_path="scripts/night_chains/alternate_calibration.zsh")
        original = gen_evidence_night.kind_row
        with mock.patch.object(gen_evidence_night, "kind_row",
                               side_effect=lambda kind: calibration if kind == "calibration" else original(kind)):
            with self.assertRaisesRegex(gen_evidence_night.GenerationRefusal,
                                        "calibration/derivation chain refused"):
                gen_evidence_night.generate(plan_path)

    def test_manifest_window_follows_protocol_not_row_default(self):
        render_fixture()
        plan = night_gate.NightPlan.from_mapping(json.loads(
            (FIXTURE / "custody/night_plan.json").read_text()))
        row = replace(kind_row("quiet_predicate_evidence"), window_max_s=8999)
        original = quiet_predicate_campaign.tracked_bytes
        def tracked(root, head, name):
            if name == "joulewise/night_kinds.py":
                return (ROOT / name).read_bytes()
            return original(root, head, name)
        with mock.patch.object(quiet_predicate_campaign, "kind_row", return_value=row), \
                mock.patch.object(quiet_predicate_campaign, "tracked_bytes", side_effect=tracked):
            self.assertEqual(quiet_predicate_campaign.manifest_for(plan)["plan_id"], plan.plan_id)

    def test_arm_flags_match_t0_scoping_when_flags_differ(self):
        from tests.test_evidence_night import LifecycleTests
        case = LifecycleTests("test_the_arm_check_spends_the_predicate_only_on_an_evidence_chain")
        case.setUp()
        try:
            third = replace(kind_row("quiet_predicate_evidence"), kind="scored_campaign",
                            corecaptured_at_arm_and_t0=False,
                            non_observer_at_arm_and_t0=True)
            table = MappingProxyType(dict(NIGHT_KINDS, scored_campaign=third))
            seen = []
            def observe():
                seen.append("quiet")
                return case.kw["quiet_observer"]()
            with mock.patch.object(night_gate, "NIGHT_KINDS", table), \
                    mock.patch.object(evidence_night, "NIGHT_KINDS", table), \
                    mock.patch.object(evidence_night, "candidate_payload_kind", return_value=third.kind):
                record = evidence_night.check(**dict(case.kw, quiet_observer=observe))
            self.assertEqual(record["checks"]["corecaptured"]["verdict"], "skipped")
            self.assertEqual(record["checks"]["machine_quiet"]["verdict"], "pass")
            self.assertEqual(seen, ["quiet"])
            self.assertFalse(third.corecaptured_at_arm_and_t0)
            self.assertTrue(third.non_observer_at_arm_and_t0)
        finally:
            case.doCleanups()

    @unittest.skipUnless(Path("/bin/zsh").is_file(), "candidate sealing requires zsh")
    def test_prepare_authors_row_paths_and_seals_candidate_at_head(self):
        self.assert_prepared_candidate_head()

    @unittest.skipUnless(Path("/bin/zsh").is_file(), "candidate sealing requires zsh")
    def test_prepare_consumes_row_prefix_and_suffix(self):
        row = replace(kind_row("quiet_predicate_evidence"),
                      plan_id_prefix="mutant-", measurement_root_suffix="mutantroot")
        table = MappingProxyType(dict(NIGHT_KINDS, quiet_predicate_evidence=row))
        with mock.patch.object(night_kinds, "NIGHT_KINDS", table):
            plan = self.assert_prepared_candidate_head()
        self.assertTrue(plan["plan_id"].startswith("mutant-"))
        self.assertTrue(Path(plan["measurement_root"]).name.endswith("-mutantroot"))

    @unittest.skipUnless(Path("/bin/zsh").is_file(), "candidate sealing requires zsh")
    def test_committed_window_mutant_refused_by_real_prepare(self):
        with self.assertRaises(evidence_night.Refused) as refusal:
            self.prepare_candidate_head(window_max_s=8999)
        self.assertEqual(str(refusal.exception),
                         "python failed (2): REFUSED: window_max_s must equal the frozen protocol's 9000 s")
        plan, _ = self.prepare_candidate_head()
        self.assertEqual(plan["window_max_s"], 9000)

    def prepare_candidate_head(self, *, window_max_s=None):
        # Clone the committed candidate H locally; no network or machine action.
        # Census-clean like the fixture root: a random suffix containing "t3"
        # would make the generator refuse the plan path.
        head_dir = _census_clean_tempdir(prefix="head-", dir=FIXTURE, ignore_cleanup_errors=True)
        self.addCleanup(head_dir.cleanup)
        work = Path(head_dir.name)
        source = ROOT
        if window_max_s is not None:
            source = work / "source"
            subprocess.run(["git", "-c", "commit.gpgsign=false", "-c",
                            "core.hooksPath=/dev/null", "clone", "-q", "--no-hardlinks",
                            str(ROOT), str(source)], check=True)
            kind_path = source / "joulewise/night_kinds.py"
            original = kind_path.read_text()
            old = "window_max_s=9000,"
            self.assertEqual(original.count(old), 1)
            kind_path.write_text(original.replace(old, f"window_max_s={window_max_s},", 1))
            subprocess.run(["git", "-C", str(source), "-c", "core.hooksPath=/dev/null",
                            "add", "joulewise/night_kinds.py"], check=True)
            commit_fixture(source, "fixture window mutant")
        remote = work / "remote.git"
        subprocess.run(["git", "clone", "--bare", "-q", "--no-hardlinks", str(source), str(remote)], check=True)
        head = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
        subprocess.run(["git", "--git-dir", str(remote), "update-ref", "refs/heads/main", head], check=True)
        t0 = (int(time.time()) // 60 + 90) * 60
        def builder(root):
            (root / ".venv/bin").mkdir(parents=True)
            (root / ".venv/bin/python").symlink_to(sys.executable)
        state = evidence_night.prepare(
            kind=kind_row("quiet_predicate_evidence").kind, t0=str(t0), head=head,
            remote=str(remote), roots_under=work / "roots", staging_under=work / "stages",
            builder=builder, lock_verifier=lambda root: None)
        return json.loads(Path(state["plan_path"]).read_text()), state

    def assert_prepared_candidate_head(self):
        plan, state = self.prepare_candidate_head()
        head = state["head"]
        row = kind_row("quiet_predicate_evidence")
        self.assertTrue(plan["plan_id"].startswith(row.plan_id_prefix))
        self.assertTrue(Path(plan["measurement_root"]).name.endswith("-" + row.measurement_root_suffix))
        self.assertEqual(plan["window_max_s"], row.window_max_s)
        self.assertEqual(plan["receipt_class"], row.receipt_class)
        self.assertEqual(plan["registration_path"], row.protocol_path)
        self.assertEqual(plan["measurement_head"], head)
        self.assertEqual(state["bindings"], evidence_night.sealed_candidate(
            Path(state["measurement_root"]), Path(state["plan_path"])))
        return plan


if __name__ == "__main__" and "--dump-goldens" in sys.argv:
    payload = {name: base64.b64encode(raw).decode() for name, raw in render_fixture().items()}
    print(json.dumps(payload, sort_keys=True))
