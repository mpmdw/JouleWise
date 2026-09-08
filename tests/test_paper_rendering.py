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

    def test_reported_energy_fixture_projection_renders_through_typed_field(self):
        from joulewise.paper_reported_energy import _synthetic_projection
        from tests.test_paper_reported_energy import synthetic_input
        fixture = _FamilyFixture("reported_energy_parents")
        self.addCleanup(fixture.close)
        projection = _synthetic_projection(synthetic_input())
        subject = projection["cells"][0]["cell_id"]
        value = _issued_control(fixture, subjects=(subject,), projection=projection,
                                payload={"extraction_report": "deliberately unusable"})
        self.assertEqual(rendering.render_reported_energy(value), f"{subject}: 42.5")
        self.assertIsInstance(value.reported_energy_projection, custody._FrozenObject)
        # This is a private synthetic issuing control, never production admission.
        with self.assertRaises(custody.PaperCustodyRefusal):
            rendering.render_reported_energy(custody.open_paper_input(fixture.ref))

    def test_reported_energy_absent_projection_refuses_with_closed_code(self):
        from joulewise.paper_reported_energy import PaperReportedEnergyRefusal
        fixture = _FamilyFixture("reported_energy_parents")
        self.addCleanup(fixture.close)
        value = _issued_control(fixture)
        self.assertIsNone(value.reported_energy_projection)
        fixture_value = custody.open_paper_input(fixture.ref)
        self.assertIsNone(fixture_value.reported_energy_projection)
        tokenless = object.__new__(custody.VerifiedReportedEnergyParents)
        with self.assertRaises(custody.PaperCustodyRefusal):
            _ = tokenless.reported_energy_projection
        with self.assertRaises(PaperReportedEnergyRefusal) as raised:
            rendering.render_reported_energy(value)
        self.assertEqual(raised.exception.code, "paper_reported_energy_projection_absent")
        self.assertEqual(raised.exception.rendered_output, ())

    def test_reported_energy_missing_or_malformed_cells_refuses_with_closed_code(self):
        from joulewise.paper_reported_energy import PaperReportedEnergyRefusal
        fixture = _FamilyFixture("reported_energy_parents")
        self.addCleanup(fixture.close)
        for projection in ({}, {"cells": None}, {"cells": {}}):
            with self.subTest(projection=projection):
                value = _issued_control(fixture, projection=projection)
                self.assertIsNotNone(value.reported_energy_projection)
                with self.assertRaises(PaperReportedEnergyRefusal) as raised:
                    rendering.render_reported_energy(value)
                self.assertEqual(raised.exception.code, "paper_reported_energy_projection_mismatch")
                self.assertEqual(raised.exception.rendered_output, ())

    def test_non_admission_carrier_is_deferred(self):
        self.assertFalse(hasattr(rendering, "render_non_admission"))
        self.assertNotIn(("whole_window_verdict", "whole-window.v1"), custody._ISSUANCE_GATES)
        self.assertNotIn("non_admission", custody._GRANT_KINDS["whole_window_verdict"])


if __name__ == "__main__":
    unittest.main()
