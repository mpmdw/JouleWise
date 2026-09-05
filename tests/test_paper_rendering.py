"""Synthetic runtime controls for F1; F6's carrier and CLI remain deferred."""
from __future__ import annotations

import unittest
from unittest import mock

from joulewise import paper_custody as custody
from joulewise import paper_rendering as rendering
from tests.test_paper_custody import _FamilyFixture, _issued_control


class PaperRenderingTests(unittest.TestCase):
    def setUp(self):
        self.fixture = _FamilyFixture("d165_closeout")
        self.addCleanup(self.fixture.close)

    def test_d165_issued_control_and_subject_grants(self):
        value = _issued_control(self.fixture, payload={"d165_closeout": {"branch": "B"}})
        self.assertEqual(rendering.render_d165(value), "B")
        for kind in ("dominance_sentence", "subtitle"):
            body = mock.Mock(return_value="must not render")
            guarded = rendering._issued_renderer(custody.VerifiedD165Closeout, kind)(body)
            with self.assertRaises(custody.PaperCustodyRefusal) as raised:
                guarded(value)
            self.assertEqual(raised.exception.rendered_output, ())
            body.assert_not_called()
        grants = tuple(custody._RenderGrant(kind, self.fixture.role) for kind in ("outcome", "dominance_sentence", "subtitle"))
        positive = _issued_control(self.fixture, grants=grants, payload={"d165_closeout": {"branch": "A"}})
        self.assertEqual(rendering.render_d165(positive), "A")

    def test_tokenless_wrong_family_and_mixed_subjects_cannot_render(self):
        for value in ({}, object.__new__(custody.VerifiedD165Closeout),
                      object.__new__(custody.VerifiedClaimEvidence)):
            with self.assertRaises(custody.PaperCustodyRefusal) as raised:
                rendering.render_d165(value)
            self.assertEqual(raised.exception.rendered_output, ())
        grants = (custody._RenderGrant("outcome", "one"), custody._RenderGrant("outcome", "two"),
                  custody._RenderGrant("subtitle", "one"))
        value = _issued_control(self.fixture, grants=grants, subjects=("one", "two"))
        body = mock.Mock()
        guarded = rendering._issued_renderer(custody.VerifiedD165Closeout, "subtitle")(body)
        with self.assertRaises(custody.PaperCustodyRefusal):
            guarded(value)
        body.assert_not_called()

    def test_non_admission_carrier_is_deferred(self):
        self.assertFalse(hasattr(rendering, "render_non_admission"))
        self.assertNotIn(("whole_window_verdict", "whole-window.v1"), custody._ISSUANCE_GATES)
        self.assertNotIn("non_admission", custody._GRANT_KINDS["whole_window_verdict"])


if __name__ == "__main__":
    unittest.main()
