# Bench cures after the round-4 delta (SF3, SF4), 2026-09-03 22:20 PDT — file 14

SF3: the four residual \rm macros (lines 285, 295, 302, 329) replaced by \mathrm; the document now has one spelling (`grep -c '\\rm\b'` → 0). SF4: Figure 3's SVG (desc, Gate 1 box text, legend note) and the caption's two sentences now name the final Gate 1 threshold the cell floor, with the legend stating 'after the safeguards of Section 4'; 'detection floor' remains only for the pre-safeguard bound in §1. Tests: ledger + terms-lint OK.

```
diff --git a/docs/paper/draft-v2-skeleton.md b/docs/paper/draft-v2-skeleton.md
index 32daf144..5e1c5264 100644
--- a/docs/paper/draft-v2-skeleton.md
+++ b/docs/paper/draft-v2-skeleton.md
@@ -282,7 +282,7 @@ I_i=[\delta_i^-,\delta_i^+]
 \]
 The mean interval over the five identical-condition null-test blocks—blocks in
 which both conditions are the same—is
-\(I_{\rm mean}=[\sum_i\delta_i^-/5,\sum_i\delta_i^+/5]\). Let
+\(I_{\mathrm mean}=[\sum_i\delta_i^-/5,\sum_i\delta_i^+/5]\). Let
 \(C=[-m,+m]\) be the earlier comparator, where \(m\) is its positive joule
 endpoint, and define the largest absolute allowed block difference as
 \[
@@ -292,14 +292,14 @@ No issued null-ladder member endpoints are available, so this construction is
 symbolic rather than measured. The forcing problem is that a point value can
 hide an allowed nonzero difference, while a mean can hide blocks moving in
 opposite directions. The containment test therefore requires every \(I_i\) to
-contain zero, then requires \(I_{\rm mean}\subseteq C\) and \(M\le m\).
+contain zero, then requires \(I_{\mathrm mean}\subseteq C\) and \(M\le m\).
 
 Here is a numeric illustration, not measured evidence: its comparator is
 \([-3\ \mathrm{J},+3\ \mathrm{J}]\), and its five block intervals, all in
 joules, are \([-2,+2]\), \([-1,+1]\), \([-0.5,+0.5]\),
 \([-1.5,+1.5]\), and \([-1,+1]\). For this numeric illustration, the
 lower endpoints sum to \(-6\) J and the upper endpoints to \(+6\) J, so
-\(I_{\rm mean}=[-1.2\ \mathrm{J},+1.2\ \mathrm{J}]\) and \(M=2\) J.
+\(I_{\mathrm mean}=[-1.2\ \mathrm{J},+1.2\ \mathrm{J}]\) and \(M=2\) J.
 Every displayed check passes. If, still only as an illustration, the fifth
 interval were \([+0.5\ \mathrm{J},+2.5\ \mathrm{J}]\), it would remain
 inside the comparator but exclude zero, so that block would fail the first
@@ -326,7 +326,7 @@ unknown, so a pass establishes only
 measured-block containment, never population coverage.
 
 For phase accounting, the residual
-\(D=E_{\rm prefill}+E_{\rm decode}-E_{\rm request}\) is the signed energy left
+\(D=E_{\mathrm prefill}+E_{\mathrm decode}-E_{\mathrm request}\) is the signed energy left
 after subtracting the enclosing request from the two phase energies. A positive
 value is double-counted energy. A negative value may be energy in the unphased gap,
 the recorded interval between the end of prefill and the start of decode;
@@ -884,7 +884,7 @@ directional claim.
 
 ![Figure 3. Evidence refusal and two sequential claim gates.](figures/fig3_decision_gates.svg)
 
-*Figure 3. Decision-gate schematic; no measured data or numeric threshold is encoded by its layout. On the white background, the title and subtitle identify two gates and four outcomes. In the upper lane, a dashed box lists an admission or custody failure and the six evidence defects that can cause it; a right-pointing arrow labelled as a side entry that reaches no gate leads to the bordered “refused” box, which says that the evidence produces no result. A pale horizontal rule separates that refusal lane from the lower decision lane. The lower lane starts with a gray measured-contrast box containing the point estimate and composed uncertainty interval. A right-pointing arrow leads to the first white rounded box, Gate 1, which asks whether the estimate's magnitude exceeds the cell's detection floor. Its “yes” arrow leads to the second white rounded box, Gate 2, which asks whether the whole uncertainty interval points one way; the next “yes” arrow leads to the blue directional-claim box, which states that both gates passed in the direction registered before collection. Gate 1's downward “no” arrow leads to the “not resolvable” box, which says the effect is smaller than this instrument can resolve and does not mean zero, equality, or no difference. Gate 2's downward “no” arrow leads to the “direction unresolved” box, which says the floor cleared but the interval did not settle direction, so no claim is made. The three bottom notes define the detection floor as the largest apparent effect produced when nothing changed, state that the floor and interval are separate gates, and state that their sum is a planning disclosure rather than an acceptance threshold.*
+*Figure 3. Decision-gate schematic; no measured data or numeric threshold is encoded by its layout. On the white background, the title and subtitle identify two gates and four outcomes. In the upper lane, a dashed box lists an admission or custody failure and the six evidence defects that can cause it; a right-pointing arrow labelled as a side entry that reaches no gate leads to the bordered “refused” box, which says that the evidence produces no result. A pale horizontal rule separates that refusal lane from the lower decision lane. The lower lane starts with a gray measured-contrast box containing the point estimate and composed uncertainty interval. A right-pointing arrow leads to the first white rounded box, Gate 1, which asks whether the estimate's magnitude exceeds the cell floor. Its “yes” arrow leads to the second white rounded box, Gate 2, which asks whether the whole uncertainty interval points one way; the next “yes” arrow leads to the blue directional-claim box, which states that both gates passed in the direction registered before collection. Gate 1's downward “no” arrow leads to the “not resolvable” box, which says the effect is smaller than this instrument can resolve and does not mean zero, equality, or no difference. Gate 2's downward “no” arrow leads to the “direction unresolved” box, which says the floor cleared but the interval did not settle direction, so no claim is made. The three bottom notes define the cell floor as the largest apparent effect produced when nothing changed, after the safeguards of Section 4, state that the floor and interval are separate gates, and state that their sum is a planning disclosure rather than an acceptance threshold.*
 
 <!-- CAMPAIGN FILL LEDGER:
 1. Report all eight independent-edge ratios:
diff --git a/docs/paper/figures/fig3_decision_gates.svg b/docs/paper/figures/fig3_decision_gates.svg
index eecfac4f..81b37605 100644
--- a/docs/paper/figures/fig3_decision_gates.svg
+++ b/docs/paper/figures/fig3_decision_gates.svg
@@ -1,6 +1,6 @@
 <svg xmlns="http://www.w3.org/2000/svg" width="1000" height="640" viewBox="0 0 1000 640" role="img" aria-labelledby="fig3title fig3desc">
   <title id="fig3title">The two separate claim gates and the four possible outcomes</title>
-  <desc id="fig3desc">Schematic decision flow. A measured contrast, carrying a point estimate and a composed uncertainty interval, meets two gates in turn. Gate one asks whether the magnitude exceeds the cell's detection floor; failing it gives the outcome not resolvable. Gate two asks whether the whole uncertainty interval points one way; failing it gives the outcome direction unresolved. Passing both gives a directional claim. A separate side inlet, taken when any admission or custody check fails, gives the outcome refused without reaching either gate. No measured data is shown.</desc>
+  <desc id="fig3desc">Schematic decision flow. A measured contrast, carrying a point estimate and a composed uncertainty interval, meets two gates in turn. Gate one asks whether the magnitude exceeds the cell floor; failing it gives the outcome not resolvable. Gate two asks whether the whole uncertainty interval points one way; failing it gives the outcome direction unresolved. Passing both gives a directional claim. A separate side inlet, taken when any admission or custody check fails, gives the outcome refused without reaching either gate. No measured data is shown.</desc>
 
   <defs>
     <marker id="f3aEnd" markerWidth="10" markerHeight="10" refX="9" refY="4.5" orient="auto" markerUnits="userSpaceOnUse">
@@ -44,7 +44,7 @@
   <text x="350" y="262" font-family="sans-serif" font-size="12" font-weight="bold" fill="#777777" text-anchor="middle" letter-spacing="1.2">Gate 1</text>
   <text x="350" y="284" font-family="sans-serif" font-size="13" fill="#1b1b1b" text-anchor="middle">does the estimate</text>
   <text x="350" y="302" font-family="sans-serif" font-size="13" fill="#1b1b1b" text-anchor="middle">magnitude exceed the cell&#8217;s</text>
-  <text x="350" y="320" font-family="sans-serif" font-size="13" fill="#1b1b1b" text-anchor="middle">detection floor?</text>
+  <text x="350" y="320" font-family="sans-serif" font-size="13" fill="#1b1b1b" text-anchor="middle">cell floor?</text>
 
   <line x1="450" y1="290" x2="488" y2="290" stroke="#333333" stroke-width="2" marker-end="url(#f3aEnd)"/>
   <text x="469" y="280" font-family="sans-serif" font-size="12" fill="#333333" text-anchor="middle">yes</text>
@@ -86,7 +86,7 @@
 
   <!-- side annotation -->
   <g font-family="sans-serif" font-size="12.5" fill="#333333">
-    <text x="40" y="572">The detection floor is the largest apparent effect this instrument produces on this kind of measurement when nothing has actually changed.</text>
+    <text x="40" y="572">The cell floor is the largest apparent effect this instrument produces on this kind of measurement when nothing has actually changed, after the safeguards of Section 4.</text>
     <text x="40" y="592">The floor and the interval are checked as separate gates. Their sum is only a sizing disclosure — a planning disclosure — and is never</text>
     <text x="40" y="612">used as a single acceptance threshold; the uncertainty interval is never compared with that sum.</text>
   </g>
```
