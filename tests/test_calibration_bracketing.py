"""Defect-shaped regressions for claim-bearing calibration bracketing."""

from __future__ import annotations

import base64
import hashlib
import json
import math
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
import subprocess
import tempfile
from types import MappingProxyType, SimpleNamespace
import unittest
from unittest.mock import patch
import zlib

from joulewise.calibration_bracketing import (
    ACCEPTANCE_BOUND_SCHEMA,
    DEFAULT_ACCEPTANCE_BOUND_PATH,
    ISSUED_ACCEPTANCE_BOUND_SHA256,
    CalibrationCandidate,
    _canonical_sha256,
    _valid_acceptance_bound,
    build_calibration_bracket_binding,
    calibration_bracket_for_bundles,
    discover_calibration_candidates,
    evaluate_calibration_bracket as _evaluate_calibration_bracket,
    load_calibration_acceptance_bound,
    load_calibration_candidate,
    validate_calibration_bracket_binding,
)
from joulewise.calibration_ledger import (
    DEFAULT_HEAD_PIN_PATH,
    GENESIS_DIGEST,
    LEDGER_SCHEMA,
    CalibrationLedgerSnapshot,
    CalibrationBracketSession,
    LedgerObservation,
    bootstrap_historical_import,
    content_id_from_artifact_hashes,
    load_calibration_ledger_snapshot,
)
from joulewise.powermetrics_fiducial import (
    MAX_AGE_S,
    PROTOCOL_ID,
    PROTOCOL_V2_ID,
    PROTOCOL_V3_SHA256,
    PULSE_COUNT,
    REGION_COVERAGE_RESOLUTION_S,
    RESIDUAL_REGION_METHOD,
    V2_BINDING_FIELDS,
)
from joulewise.schemas import CalibrationBracketingPolicy
from scripts.calibration_ledger_bootstrap import (
    _issued_acceptance_artifact,
    _issued_artifact_bytes,
)


_REAL_D079_TABLE = Path("/private/tmp/d079-ledger-dispositions.json")
_REAL_D079_CUSTODY_MANIFEST = Path(
    "/private/tmp/d079-custody-manifest.lead.json"
)
_REAL_D079_TABLE_SHA256 = (
    "5da820aa5c649e5991b934230cd75e8c99daa8dcea22f3f1b3e3db89c80f2a6a"
)
_REAL_D079_CUSTODY_MANIFEST_SHA256 = (
    "99cbf3df7aef3b81839f40272a529eb137bf2f21276e2a1d07788c764035f078"
)
_UNISSUED_ACCEPTANCE_FIXTURE_SHA256 = (
    "9a264c57fdc007de473872870f19a5e1c9bd9b11256c25266b0e3e50ebba0ceb"
)
_UNISSUED_ACCEPTANCE_FIXTURE_B85 = b"""
c-qZd*={3Ac75-!AoSD?7pr4m#!oh827a(-fI-_YMk8?};zlXExoDWAstb+!cc0)+i4;Y(3UC2cDv_BPH}1L1Igt^+e>WQ44f&p@
)IIWI=;yP$KaK8wnXe}NxgYprrb(X`w8R%3<;)LDnq}_Nd^IZ{AJxa&|F&E$_~WCz`_P_sbWLB{ql)mcyYQ4p)y-tw+*mmGZFt-
^;J*LGXZZBbV=2`7g6%Ky4*&moGt^?)SIWz7F`sZ7YCDguN!@DJ55tPf=K1aaZBShJ`{r@Ol9sDB*4=8>Y^yz&-
Oalp^Mv|o$CLh3pVos^nhd=Ca=|og{I#}h^ba+{^{atLezf3!uKEQJqX|<P!L@jNUOQkkucHNh9zEQD8TveoXjVq|G~DCb#C5*l(
Zgb1R(XBx-
fE2abv=&>mruOt@@hG+^=L8}k2lj3Tl4NQa##9KJS>}y;t&4Wxnyg=#@UyHWu69JJZ}EKxn&n4&2wACc2Ird84vx?&F0IFy2Jdt-
TZg+-
MgVLJX`k5FC9P3^ZmgO^Px+tezFcdW&aw?ZpeFDl+T2*rt`v+_Vs^Jmi9y3UGOmfjA=d0Cw>0XzNXyW_n+>&_2;{b2AV!h`q`(hp
Do+;Cf&3}kQ6(o!`c0mmh(lo;K%-
uPq@CD%!i>HRtTg=o*bS4kInKul3{Pj3NhBau$<@lWSd88Gp4*;AZEJF6}5+(dOYD#9~^_*h6jfC9vLPS1l|UOgNuL?&k8L%{_UY
(w7Je!lgV~$JpWUJ_ZYs#YJ=7<E5L}fD$P%e9&_BM;0#kjOz@<_s^#73!w&g;3>?yJQo4LkvroHp+nB$ZHJ*O(W%{z@XP3_Sa|i$
Rr2{Ih+-x75>0upIm>zO#*iHqxy*Rx;&leA?p)2!-$k5freA>y_E$5vMr=tvCh9!c1+2^iOKWPt#F%!5E$pu$%MS-
|qA}1Eiv%B@JKkvZYO=!3$WnJ@QWU5isV5N4fw8_>n=~|06Ix6xyYpIJN5mlyCwFuQ#OH^wlEz>@W4*toA>B9iO?`+>^=8q@Qvx}
RL59>fzlC$*LCnaTM8@*(ga@Da!6=jLSm!yrS<cOS((Iu%VXr~1m?MWYebr^4joLwvlF^&v<Y|v!h4(Gj*s>o<kGCKQOv-
Vm?silpQrIKD~FH6wH31cGXR3vE*KIRxg_UDG90?ZL;C-dBmr-
NXoU@I4utrXf&E~$E%3X$<9hmwu3x@JW(1xLYTVUrfH(Puh09ujM{pOBR@1QSc4SaQ-XnX0p`<XjcfJMXf~M#7~=IHgF{0@qnpwU
p90X*comb)Uh9ob5ItdR*lvoVVG0w~qbMF22T(dbExFeIr@k^N4@TlU3m|`rOaT{PXzVN9#1kjnpqb;A^DsXqP*qO*P%dR~tpf?J
rZFrqfj3h1vegZKYB|IpLN1Ng8Xl9dk4?2POB8Y!jKU7O3h4Eixm3*M3~AW<$5J5=~(Dlpp)quw1OBFmRLYYtQ`nnnBW`Lay7q_$
UBshyih>oYhL1<IATs>nn2VC{r29S+a}~aT2vNrIu`UOd9!Xh-
;3~S6?|7CbC5rFPu;T!4()u;*TGHG>=_I9E~JRAfF7v#&TuExkL8Zj5NzBW{KQz$P|gxiB43fOhA&BfCx&Olc&4wKwm$+8Xb5{hB
0DRctr0_=&0Ajb9t0A@F--4aB#IU0<Mkj3O*uORY+1vqKHzI(I{d@rQ&=+t#Va4jLXa@HZ`%VJ_4HTz4S&2BVUhC@=mkGbA?vc7S
Ab3cpr)Ga?XW96d|Qp5L=OwQQ(8xYGJAsl~CMo$EQt1iLq?ODrIpKKKj-
8yfDhS^wClY6fGT$cHXON>BDfgq~O^SfT=bMqu2l_bd-
={LN8E&g)<R(6lmm*sAxqNRnn##;L#}XH5ym6RjROYNl1#KsF;Lts!EOY638)%u2iiPWgo4G1#>}<p|`+erSfCMR&`F&P4Ji-
;JG-;x%5%!twMP1g*6WIzJgB#x$vPT6tfgvt|16%6MR?$S~97|HWWN&g9k0~0r>-
J;ziBYvLO3<e1x;eyr|l}<SL<R$1G&7K2eZPYYqAlax2LRq`*qlQ~Y0M@(2mk>D%#9N^3Qa7{q3&zZE{0M>(557Ou1o6)r^lxt2c
F8&1VmL10THtPc*&2x;O%VqJ@m-WpX(EIu>HQ7JxITV-+_vNf-Vhmkls6f2ypqDo~$F+SCdZYFAy)!0DJgGWVcfQC>49MF-
bY*P)D-vAHFsEFgBoKaT#o8YlKc=T0xE{}39eZ0f;&{85Ox6#2~!N-E`kut2k7pN@)q!s<EWc-HWg655W!J<?^q_lSqT$5{H4>zW
YA2;CB61zexlw5Id^s0g+qZ>g$WFJan(5T;jTmOU(G9(lM3S^8a{#JbSPeOsChB4{@xO$G?1fLg2Ifsw&R%?Sa5)xHW`78Kjw0#|
%BT%VIBC#X3S(N~`R#0UOG!@%gtXD}Tsj5<$UDF}nqs*1p<Ku!ua#-jV78!!rK)|s9{f~iFq!MB>-
d6|CX1pjaK;J1So*EjHl=%(#SS73+7qE<w1AQxeE{}2!ACT0>4O~R4z~8Ivtu{B*fcB$^grf{!v<wL%M||1RsB$Hc>D(l-
jJAT~Q}Jl)EYuD7fD#6d4mGW~3PC10;Ag1WC=YQIBjO<=tia@Ta-gBsOCd!Ho(#VQ9~ls(Zfp=xQ6+N|KJL}{yfDhy`lg(cPJ|Gw
u}WUcpF~wwR2rnF^2D*CvXM42X#i~rZ34_GS_%H^!Pbj&s+eG0ChG#ld`tdBV_l(S8OewYw52B0OrwFBG>s3U<$&R#>?znG)tcc$
jyWJ#${X+jSw!P5!Z4~Oe=B@0k8-xYStuW;W0Oi2C|$z`@Y@XXB%M@HI_zb#35-
g5lssEdBV}X|2lQ)*l~}=w!KYC5(5evXug9lqBqk<MMJQ;E)~@vqCWYj2HZhY)Y;-
ooO6%Detw8lt(?n53a&N)MdM(B&gZM~uTYd94;B#@5v-
Pd5+u&9OGGUFmh7S}7qm?)S5gd3@($!bZLZ%3zN{o`Eye+1*UM5*tj*_5>G;>ly+(56r%&5FoXDBP3qZ1_taJhsb@o>;hVnRvN(L
<xceu7p-gR+j3Y0C$<<D(!PO&l|x>>&oe5k4=Ba<;yCU=)H15`;q7Yy1re7A;WB5Cs`R$Q1<^=SrwLlCd6-
gO)GJzzB41TU7*G0o}%ptYy4Gp5mDSxtFpIkU-jiz>z5#WFaU{&Vm#A&?+88a<Zy1hc!>srsk^XE%<;axv`d}x)N{0C)|L~#Zk_#
?f@5OCDc+|Jh1u-
KBei=9I{9`%Vbo{ma`Jj!qnOj3+NRnNE4xZBjkt?kyUm%8Bj1^`38QiV~v`?)RbZ&gl_A7##f;rZoo)@kBU)>j8+IDE~G}KgDyp$
niPb-6(94HkWlJz3`vJ#Y1KEu=fzRZ);Dxo2d&o@;iS4IPfacYj&?#biAE1m&8mT-
N4jcCRRADDLN!HI(FW0y+WI$(CThvu0uO^Rm*~Mq94IsDXF)JjYpT)CMeq&C(U2OavCv}~V4)f!RRudn$lVH${R!1qqHz;6o0RD`
c^Y@{n3v&sag=lLXl0}g63SGy8?MpotWfX0Z9Li{Uz~)*uNjiG_=KtlMXYOyNk&K>@L-
DwY44mYR0%pszM;I~K2%+*$;;wEn}ZV;dNeo%Di9JHkw!U1rs!5nvjjL1It-
dvmMRm!0Us$L1;+w}F?*lC6+V|oIfqXO5ljq)Lj<UOeXae-Bv5zOpvd-iPg@<qs>y<CgV~u>3{_~6nuP}wW=P8H6=EH7B|y*KK(7
I`PG~zIXRR*=bTVbZouh}*Nm-E%R|E21BifJmV5|5SstElG+4Tl|P?Dt@3&;bsF#E0Wxjf1_d?G}tLasqm;D@+I-
?Gku+Y$jpddi>&wggBNG8&i}i@!qU_AWCS!JvguA~84zX%z|pyn()fQ(KT{(2<f2>Zg<$%vk^x*_Pj2B+Rd9DxmS0td}ksNT#Y#)
3q)127JI|5!ppo;T_+Gj}$wA>{Wm+4|7)k1P_c*!y#u-
wy!N;SFm0P4+X*t85Gc<+pi3_L6?GO*!IE);T@Vh@#G828iaqVxvb6Ua>ljwH?$qD2@0qtN0?PEwup$j1|h6;a)CvAu@RwxjTN4w
%d)J4q|t;o0OZhu{W$t;b0YW60J=QPS%M%SQ6bee*f=8a8i9+!qy&e9JS$3u92IVBI2MWoDX3j>s%<S`>w-
gX4<3cHX?}7pd2z!6HmI4FfTfD2qBF*+x<C#?UX@fE88A=<QhHw~6jV};E1VXAL9{EWJwThi8%Mio+BTQt%`gKmkG9gB?!r2|59^
!l#QLLqvA#Qs$h$nBEt_xmyJ)7oyq~XQa^vOiGtK6+9*^yQ8RoO^e?J4r$M(&KT_CJ~`#NfScSf6M3_tv^-@DQ_8g!YKG?{-
ocHnxy;OVBW7dLjjYIE1CH+a2jlh=D~^!g*4y$-
>;L+}XXlU*7|&~8{E88j_s?`u(63Ia=n$TFx01$qkXx+;hIi8>caQISZ=l0h0}Va4$14!ooNo!f0A_^lrv=0kt7MWuaC%Oy`Ame+
QO9O~l}tI@m(R;RX%mN^7ubFHZ5(C^R{qT-
2yQNjf17nltB_9{!)idq9Y%ly7pKiSi8(P}6(l`Fw<5kf>pQ0#)P9?=VBFw9EBHbc@El~B8ydIC7Lt>rY4S>M&_r*HZ%TU|Vd7^D
yEn~*k8URqPz`k*C94)~1^mQr$Fk}9UHSEA>D@t9a`d+qqHR-
e8Azi2fG14CrG6sRpkrU<8&XtdAF!DuB+2qjxc`CN4>;OAi3E?W)30-
gWPzJBsr_@dQTM1?E_qnE0pS3ywwCL%aMxN;Ic3+S`zp!+OA1_&zzDNsb?3Vfa4*Xk#4OD|_*V^jj!=CV^!fR|dd>=;M{p+SRE&E
N@A2`yE7c?{j^BI_Uuv<_nG9j$);4)LPZOt7|EMv{34H&#S&2}&W3JqWx7FC<3!z*m-
A;Zs>45pqq?Owg(CYxR>iYZt9<n_)uns=YtXt?FrHFDf8Ya%_aNus1aZTvav3!&nr`QW5QyDAw|>RzH2;bU8v=rpc&dB8Vvb^cqn
Sj5CaohS*_~WFbKwu>>va6d^hgB|;c>CBCoKPu{{@t|5dl@S55Sc8<C2^Fzmh8$+=uC(a_ylMPXTwOUSX;TSp^1zu!{E5kcmefn<
VqSZ!*(zbn&)1{zFBx1=askV7H;8~EBRa<yBMFTYp3?O6?bqK+>7dOAF)lXOKFIo+Lo=nQxXfVUv+-
?Zno6yKZgbtP#lR`ig=Tj@E)?sdKEhMruC^GMC_31kHMXR+XMt6ov_mC~YIvImvB(Rr|nTjQ$uiL!dBgoD%`g|fQjkK6s$@(3we!
jYU(dtxvR?@e%^I8dV2LYR`Mw2N?u=AiL6=pNlOy0-R-
WQ?t39oagKE0>a&lf!}S}jFok!nSWMvGJsoK<C{LyKOHH35cHyao+3goJIay}c-gRtH%WoZr{#Crg2s;~Ejf2xAl5Qnf+h6T(-
WwY5oSRSL+5_8h&C2~{cK!YE9YZ2_yjdw5@~pDd7F<{`2wQ_;_}1s5TUKCP`WAgCs_r6>eQ+d9L6QMnoQC`9M+HwZuygLz-
8pR5{Pv>Lr7W)wEzDgv0G2oNJuRsa-
{e`H)xMcdL&G+;hKWpJzLJ!({>^$PcUTK!}x<)ye@@1=~WkisCqAtJo<nGAST+hd7zR4F5hQCdn{qBqJ|L&kyvpbFk(b%KyB<NNu
f%va0j)^87BjeniZKhO4;JzWJs6aTgLlL_?tth6<xYp3Y;*LCyR<jejr-Tu>l_6UD$)~<fvdiGBvtv<AMp53qR>){B^v-
4nSGS9zqyKK2w9S-EJ58ajS_`F>+tsTM}V}@MX(Yx{S(YxIdrg1xicXCkgU-A8y5oX21eDa7}H!F3c_0YrNXx{E<*y@270~ZY6m-
W26we!3635?;1EZ@bA`>Czy=r}e}f=<+<(=>-GK%<o!v&gJ<-
LA&}d~{wU_fwj5=gxY~R#SYMyMd=PTVl@ZfZ5)#T}YhpZ#?B;Kab6)4cC6y-m+hvnf9}Ox|+UX$MOEs+qO^NP3gCj5iahT-Cudz{
@=UxDX{(HrGU^y0_ydCeXEX6eodKX?QqwCP~EQmoi0fsP*=Qvw;dtP^!kmP23bGZyFQ_`S(RF}W3vd5<EI{9xc<JaJnfF${p0Wd{
kK1N|M74C`Pc3*|MQo>jh6G#KM{4y)pUeGpZ<}f;n_;_W;F{FF0Y=8Q0PvWf_7Gm_QL4@&0H{6={J=i+HU!I-
WBBY9!wFSU2TB&L1h*GXoK6yo$>jd(5g{O=R_1XYOv$e)zK5rtz9)dTeIB6l~mosgfb5=Iru2(&bszwxOFAj9E{EL=>sj=qT{<b`
q;%M)7?GsB=hIx+`|tZo}>KH`q*h&pkMI*IOK^NHr3_03LVPU$7iMI<1Sf`rn{ZW0rWPL;|tcFK1uMCH+{R3xI2S<u=~ip=OS-
=$aAx(`wnwERJtp(I{<chnnz_a3i0Ooo`%7$o$qfsiTYERFF5>y<F47=ihGyZLB%DdNjuAnlo}3RLGQ39>H4fI9Nk>d)0Z!#`u<*
;Oy-~0^kSDvc-r^-
^TXTce0VzXAI>I0%b}C!z!Tl^OSKQ+Y0HyOe)yN;w>F#M4mKU)<gRtRvd;O8VcJV2dHE3O(KfUU`mU48K|*~wlt~o%3{}$JY|Eww
xssE@c(^y)B&{zRG*l=P+v(Q3@4kNbfA+zM4g
"""


def _unissued_acceptance_fixture_bytes() -> bytes:
    """Return the exact pre-issuance fixture bytes, independent of repo state."""

    encoded = b"".join(_UNISSUED_ACCEPTANCE_FIXTURE_B85.split())
    raw = zlib.decompress(base64.b85decode(encoded))
    assert hashlib.sha256(raw).hexdigest() == _UNISSUED_ACCEPTANCE_FIXTURE_SHA256
    return raw


def _unissued_acceptance_fixture() -> dict:
    artifact = json.loads(_unissued_acceptance_fixture_bytes())
    assert _valid_acceptance_bound(artifact)
    return artifact


def _synthetic_issued_artifact() -> dict:
    """Return a schema-valid issued artifact for isolated consumer tests."""

    artifact = _unissued_acceptance_fixture()
    prior = artifact["prior_observation_set"]
    observations = [
        row for row in prior["observations"] if row["disposition"] == "valid"
    ]
    assert len(observations) == 19
    additions = (
        ("valid", 11),
        ("systematic-invalid", 2),
        ("ordinary-invalid", 6),
    )
    for disposition, count in additions:
        for index in range(count):
            token = f"synthetic-issued-{disposition}-{index}"
            observations.append(
                {
                    "content_id": hashlib.sha256(token.encode()).hexdigest(),
                    "epoch_id": "d079_epoch",
                    "disposition": disposition,
                    "attempt_id": token,
                }
            )
    head_digest = hashlib.sha256(b"synthetic-issued-head").hexdigest()
    artifact["schema_version"] = ACCEPTANCE_BOUND_SCHEMA
    artifact["artifact_role"] = "issued"
    artifact["issuance"] = {
        "status": "issued",
        "claim_eligible": True,
        "reason": "synthetic issued-artifact consumer regression",
    }
    artifact["ledger_cutoff"] = {
        "sequence": 76,
        "head_digest": head_digest,
        "ledger_schema": LEDGER_SCHEMA,
        "role": "issued_acceptance_baseline",
    }
    prior["cutoff"] = {
        key: artifact["ledger_cutoff"][key]
        for key in ("sequence", "head_digest", "ledger_schema")
    }
    prior["observations"] = observations
    artifact["backfill_candidate"].update(
        {
            "status": "issued",
            "candidate_inventory": {
                "ordinary-invalid": 6,
                "systematic-invalid": 2,
                "valid": 30,
            },
            "production_issuance_blocked": False,
            "required_verification": "complete: synthetic consumer regression",
        }
    )
    artifact["derivation_sha256"] = _canonical_sha256(
        {
            key: value
            for key, value in artifact.items()
            if key != "derivation_sha256"
        }
    )
    assert _valid_acceptance_bound(artifact)
    return artifact


def _synthetic_issued_snapshot(
    artifact: dict,
) -> CalibrationLedgerSnapshot:
    epoch = artifact["prior_observation_set"]["epoch_catalog"]["d079_epoch"]
    observations = tuple(
        LedgerObservation(
            sequence=2 * index,
            receipt_digest=hashlib.sha256(
                f"issued-receipt-{index}".encode()
            ).hexdigest(),
            attempt_id=row["attempt_id"],
            content_id=row["content_id"],
            artifact_sha256=MappingProxyType({}),
            identity_epoch=MappingProxyType(dict(epoch)),
            t1_bindings=MappingProxyType({field: None for field in V2_BINDING_FIELDS}),
            capture_wall_time_s="1.0",
            exact_bound_lexeme_s="0.025",
            disposition=row["disposition"],
            custody_locator=f"/synthetic-issued/{row['attempt_id']}",
            observation_kind="historical-import",
        )
        for index, row in enumerate(
            artifact["prior_observation_set"]["observations"], start=1
        )
    )
    cutoff = artifact["ledger_cutoff"]
    return CalibrationLedgerSnapshot(
        ledger_schema=LEDGER_SCHEMA,
        ledger_path=Path("synthetic-issued-ledger.jsonl"),
        head_sequence=cutoff["sequence"],
        head_digest=cutoff["head_digest"],
        receipts=(),
        observations=observations,
        refusal_reasons=(),
        baseline_sequence=cutoff["sequence"],
        baseline_digest=cutoff["head_digest"],
    )


def _fixture_snapshot(
    candidates: list[CalibrationCandidate],
    *,
    extra_observations: tuple[LedgerObservation, ...] = (),
) -> tuple[CalibrationLedgerSnapshot, list[CalibrationCandidate]]:
    """Build an explicitly synthetic authenticated snapshot for unit tests."""

    normalized: list[CalibrationCandidate] = []
    observations: list[LedgerObservation] = []
    for index, candidate in enumerate(candidates):
        attempt_id = candidate.attempt_id or f"fixture-attempt-{index}-{candidate.relative_path}"
        hashes = {
            "manifest.json": candidate.manifest_sha256,
            "instrument_evidence.json": candidate.evidence_sha256,
        }
        content_id = candidate.content_id or content_id_from_artifact_hashes(hashes)
        assert content_id is not None
        digest = candidate.ledger_receipt_digest or hashlib.sha256(
            attempt_id.encode("utf-8")
        ).hexdigest()
        bound = str(candidate.b_fiducial_s)
        normalized_candidate = replace(
            candidate,
            attempt_id=attempt_id,
            content_id=content_id,
            ledger_receipt_digest=digest,
        )
        normalized.append(normalized_candidate)
        observations.append(
            LedgerObservation(
                sequence=index + 2,
                receipt_digest=digest,
                attempt_id=attempt_id,
                content_id=content_id,
                artifact_sha256=MappingProxyType(hashes),
                identity_epoch=MappingProxyType(
                    {
                        field: candidate.bindings.get(field)
                        for field in (
                            "os_build",
                            "hardware_model",
                            "power_policy",
                            "sampling_interval_ms",
                            "estimator_revision",
                            "pulse_protocol_id",
                        )
                    }
                ),
                t1_bindings=MappingProxyType(
                    {field: candidate.bindings.get(field) for field in V2_BINDING_FIELDS}
                ),
                capture_wall_time_s=str(candidate.capture_wall_time_s),
                exact_bound_lexeme_s=bound,
                disposition="valid",
                custody_locator=candidate.relative_path,
            )
        )
    all_observations = (*observations, *extra_observations)
    return (
        CalibrationLedgerSnapshot(
            ledger_schema=LEDGER_SCHEMA,
            ledger_path=Path("fixture-ledger.jsonl"),
            head_sequence=len(all_observations) * 2,
            head_digest=(
                all_observations[-1].receipt_digest
                if all_observations
                else GENESIS_DIGEST
            ),
            receipts=(),
            observations=tuple(all_observations),
            refusal_reasons=(),
            baseline_sequence=0,
            baseline_digest=GENESIS_DIGEST,
        ),
        normalized,
    )


def _evaluate_with_unissued_acceptance(
    candidates: list[CalibrationCandidate] | tuple[CalibrationCandidate, ...],
    **kwargs: object,
) -> tuple[dict, tuple[str, ...]]:
    """Evaluate against the exact genesis fixture, never the live anchor."""

    with patch(
        "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
        return_value=_unissued_acceptance_fixture(),
    ):
        return _evaluate_calibration_bracket(candidates, **kwargs)


def evaluate_calibration_bracket(
    candidates: list[CalibrationCandidate], **kwargs: object
) -> tuple[dict, tuple[str, ...]]:
    snapshot, normalized = _fixture_snapshot(list(candidates))
    return _evaluate_with_unissued_acceptance(
        normalized,
        ledger_snapshot=snapshot,
        _allow_unissued_fixture=True,
        **kwargs,
    )


class CalibrationBracketingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bindings = {field: f"value-{field}" for field in V2_BINDING_FIELDS}
        self.bindings.update(
            {
                "hardware_model": "Mac15,9",
                "os_build": "25F84",
                "sampling_interval_ms": 100,
                "pulse_protocol_id": PROTOCOL_ID,
                "power_policy": "ac_high_power",
                "estimator_revision": RESIDUAL_REGION_METHOD,
                "protocol_sha256": PROTOCOL_V3_SHA256,
            }
        )
        self.policy = CalibrationBracketingPolicy(
            require_bracket=True,
            calibration_bracket_max_drift_s=0.010,
        )

    def test_explicit_unissued_fixture_cannot_license_claim_evaluation(self) -> None:
        snapshot, candidates = _fixture_snapshot(
            [
                self.candidate("pre", 99.0, "0.025"),
                self.candidate("post", 111.0, "0.026"),
            ]
        )
        with patch(
            "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
            return_value=_unissued_acceptance_fixture(),
        ):
            result, reasons = _evaluate_calibration_bracket(
                candidates,
                window_start_s=1_000.0,
                window_end_s=1_100.0,
                bindings=self.bindings,
                policy=self.policy,
                ledger_snapshot=snapshot,
            )

        self.assertEqual(reasons, ("calibration_acceptance_bound_stale",))
        self.assertEqual(
            result["acceptance"]["freshness"]["reason"],
            "acceptance_artifact_unissued_fixture",
        )

    def test_live_issued_anchor_authenticates_and_matches_committed_head_pin(
        self,
    ) -> None:
        raw = DEFAULT_ACCEPTANCE_BOUND_PATH.read_bytes()
        artifact = load_calibration_acceptance_bound()
        pin = json.loads(DEFAULT_HEAD_PIN_PATH.read_bytes())

        self.assertIsNotNone(artifact)
        self.assertEqual(artifact["artifact_role"], "issued")
        self.assertEqual(
            hashlib.sha256(raw).hexdigest(), ISSUED_ACCEPTANCE_BOUND_SHA256
        )
        self.assertTrue(_valid_acceptance_bound(artifact))
        self.assertTrue(artifact["issuance"]["claim_eligible"])
        self.assertEqual(
            {
                key: artifact["ledger_cutoff"][key]
                for key in ("sequence", "head_digest", "ledger_schema")
            },
            pin,
        )
        self.assertEqual(pin["sequence"], 76)
        self.assertEqual(
            pin["head_digest"],
            "08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7",
        )

    def test_issued_artifact_authenticates_and_becomes_claim_eligible(self) -> None:
        artifact = _synthetic_issued_artifact()
        snapshot = _synthetic_issued_snapshot(artifact)
        with patch(
            "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
            return_value=artifact,
        ):
            result, reasons = _evaluate_calibration_bracket(
                (),
                window_start_s=100.0,
                window_end_s=110.0,
                bindings=artifact["identity_epoch"],
                policy=self.policy,
                ledger_snapshot=snapshot,
            )

        self.assertEqual(reasons, ("instrument_calibration_bracket_missing",))
        self.assertTrue(result["acceptance"]["artifact"]["claim_eligible"])
        self.assertEqual(
            result["acceptance"]["artifact"]["artifact_role"], "issued"
        )

    def test_issued_artifact_wrong_head_digest_refuses(self) -> None:
        artifact = _synthetic_issued_artifact()
        snapshot = _synthetic_issued_snapshot(artifact)
        artifact["ledger_cutoff"]["head_digest"] = "f" * 64
        artifact["prior_observation_set"]["cutoff"]["head_digest"] = "f" * 64
        artifact["derivation_sha256"] = _canonical_sha256(
            {
                key: value
                for key, value in artifact.items()
                if key != "derivation_sha256"
            }
        )
        self.assertTrue(_valid_acceptance_bound(artifact))
        with patch(
            "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
            return_value=artifact,
        ):
            result, reasons = _evaluate_calibration_bracket(
                (),
                window_start_s=100.0,
                window_end_s=110.0,
                bindings=artifact["identity_epoch"],
                policy=self.policy,
                ledger_snapshot=snapshot,
            )

        self.assertEqual(reasons, ("calibration_ledger_baseline_missing",))
        self.assertFalse(result["acceptance"]["artifact"]["claim_eligible"])

    def test_issued_artifact_missing_ledger_refuses(self) -> None:
        artifact = _synthetic_issued_artifact()
        with patch(
            "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
            return_value=artifact,
        ):
            result, reasons = _evaluate_calibration_bracket(
                (),
                window_start_s=100.0,
                window_end_s=110.0,
                bindings=artifact["identity_epoch"],
                policy=self.policy,
                ledger_snapshot=None,
            )

        self.assertEqual(reasons, ("calibration_ledger_snapshot_required",))
        self.assertFalse(result["acceptance"]["artifact"]["claim_eligible"])

    def test_issued_artifact_committed_head_mismatch_refuses(self) -> None:
        artifact = _synthetic_issued_artifact()
        snapshot = replace(
            _synthetic_issued_snapshot(artifact),
            refusal_reasons=("calibration_ledger_head_mismatch",),
        )
        with patch(
            "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
            return_value=artifact,
        ):
            result, reasons = _evaluate_calibration_bracket(
                (),
                window_start_s=100.0,
                window_end_s=110.0,
                bindings=artifact["identity_epoch"],
                policy=self.policy,
                ledger_snapshot=snapshot,
            )

        self.assertEqual(reasons, ("calibration_ledger_head_mismatch",))
        self.assertFalse(result["acceptance"]["artifact"]["claim_eligible"])

    def test_issued_artifact_prior_set_divergence_refuses(self) -> None:
        artifact = _synthetic_issued_artifact()
        snapshot = _synthetic_issued_snapshot(artifact)
        artifact["prior_observation_set"]["observations"][19]["content_id"] = (
            hashlib.sha256(b"divergent-prior-member").hexdigest()
        )
        artifact["derivation_sha256"] = _canonical_sha256(
            {
                key: value
                for key, value in artifact.items()
                if key != "derivation_sha256"
            }
        )
        self.assertTrue(_valid_acceptance_bound(artifact))
        with patch(
            "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
            return_value=artifact,
        ):
            result, reasons = _evaluate_calibration_bracket(
                (),
                window_start_s=100.0,
                window_end_s=110.0,
                bindings=artifact["identity_epoch"],
                policy=self.policy,
                ledger_snapshot=snapshot,
            )

        self.assertEqual(reasons, ("calibration_ledger_baseline_missing",))
        self.assertFalse(result["acceptance"]["artifact"]["claim_eligible"])

    def test_issued_artifact_stale_derivation_sha256_refuses(self) -> None:
        artifact = _synthetic_issued_artifact()
        artifact["derivation_sha256"] = "0" * 64
        self.assertFalse(_valid_acceptance_bound(artifact))
        with patch(
            "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
            return_value=None,
        ):
            result, reasons = _evaluate_calibration_bracket(
                (),
                window_start_s=100.0,
                window_end_s=110.0,
                bindings=artifact["identity_epoch"],
                policy=self.policy,
                ledger_snapshot=_synthetic_issued_snapshot(
                    _synthetic_issued_artifact()
                ),
            )

        self.assertEqual(reasons, ("calibration_acceptance_bound_stale",))
        self.assertIsNone(result["acceptance"]["artifact"])

    def test_unknown_acceptance_artifact_role_refuses(self) -> None:
        artifact = _synthetic_issued_artifact()
        artifact["artifact_role"] = "unknown"
        artifact["derivation_sha256"] = _canonical_sha256(
            {
                key: value
                for key, value in artifact.items()
                if key != "derivation_sha256"
            }
        )
        self.assertFalse(_valid_acceptance_bound(artifact))

    @unittest.skipUnless(
        _REAL_D079_TABLE.is_file() and _REAL_D079_CUSTODY_MANIFEST.is_file(),
        "lead-reviewed D-079 import inputs are unavailable",
    )
    def test_production_path_authenticates_real_76_receipt_import_prefix(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            ledger = repo / "runs" / "calibration_observation_ledger.jsonl"
            pin = repo / "configs" / "calibration" / "calibration_ledger_head.json"
            pin.parent.mkdir(parents=True)
            pin.write_text(
                json.dumps(
                    {
                        "sequence": 0,
                        "head_digest": GENESIS_DIGEST,
                        "ledger_schema": LEDGER_SCHEMA,
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            plan = bootstrap_historical_import(
                ledger,
                head_pin_path=pin,
                checkout_root=Path("/Users/edr"),
                disposition_table_raw=_REAL_D079_TABLE.read_bytes(),
                expected_disposition_table_sha256=_REAL_D079_TABLE_SHA256,
                custody_manifest_raw=_REAL_D079_CUSTODY_MANIFEST.read_bytes(),
                expected_custody_manifest_sha256=(
                    _REAL_D079_CUSTODY_MANIFEST_SHA256
                ),
                execute=False,
                require_committed_pin=False,
                repo_root=repo,
            )
            source_raw = _unissued_acceptance_fixture_bytes()
            source = _unissued_acceptance_fixture()
            issued = _issued_acceptance_artifact(
                plan,
                source,
                source_artifact_raw=source_raw,
            )
            self.assertEqual(
                issued["derivation_corpus"], source["derivation_corpus"]
            )
            issued_path = repo / "issued-acceptance.json"
            issued_path.write_bytes(_issued_artifact_bytes(issued))
            loaded = load_calibration_acceptance_bound(issued_path)
            self.assertEqual(loaded, issued)

            ledger.parent.mkdir(parents=True)
            ledger.write_bytes(plan.ledger_bytes)
            pin.write_text(json.dumps(dict(plan.head_pin)) + "\n", encoding="utf-8")
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            subprocess.run(
                ["git", "config", "user.email", "tests@joulewise.invalid"],
                cwd=repo,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "JouleWise tests"],
                cwd=repo,
                check=True,
            )
            subprocess.run(
                ["git", "add", pin.relative_to(repo).as_posix()],
                cwd=repo,
                check=True,
            )
            subprocess.run(
                ["git", "commit", "-qm", "pin test ledger head"],
                cwd=repo,
                check=True,
            )
            snapshot = load_calibration_ledger_snapshot(
                ledger,
                pin,
                baseline_sequence=plan.final_sequence,
                baseline_digest=plan.head_digest,
                require_committed_pin=True,
                verify_custody=True,
                repo_root=repo,
            )
            self.assertEqual(snapshot.refusal_reasons, ())
            self.assertEqual(len(snapshot.observations), 38)
            self.assertTrue(all(row.is_historical_import for row in snapshot.observations))
            with patch(
                "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
                return_value=loaded,
            ):
                result, reasons = _evaluate_calibration_bracket(
                    (),
                    window_start_s=100.0,
                    window_end_s=110.0,
                    bindings=issued["identity_epoch"],
                    policy=self.policy,
                    ledger_snapshot=snapshot,
                )

        self.assertEqual(reasons, ("instrument_calibration_bracket_missing",))
        self.assertTrue(result["acceptance"]["artifact"]["claim_eligible"])
        self.assertEqual(
            result["acceptance"]["ledger_snapshot"]["baseline_sequence"], 76
        )

    def test_import_marker_is_excluded_by_discovery_and_trigger_paths(self) -> None:
        candidates = [
            self.candidate("pre", 99.0, "0.025"),
            self.candidate("post", 111.0, "0.026"),
        ]
        snapshot, registered = _fixture_snapshot(candidates)
        imported_hashes = {
            "manifest.json": "12" * 32,
            "instrument_evidence.json": "34" * 32,
        }
        imported = LedgerObservation(
            sequence=snapshot.head_sequence + 2,
            receipt_digest="56" * 32,
            attempt_id="historical-range-expander",
            content_id=content_id_from_artifact_hashes(imported_hashes),
            artifact_sha256=MappingProxyType(imported_hashes),
            identity_epoch=MappingProxyType(
                {
                    field: self.bindings[field]
                    for field in (
                        "os_build",
                        "hardware_model",
                        "power_policy",
                        "sampling_interval_ms",
                        "estimator_revision",
                        "pulse_protocol_id",
                    )
                }
            ),
            t1_bindings=MappingProxyType(
                {field: self.bindings[field] for field in V2_BINDING_FIELDS}
            ),
            capture_wall_time_s="105.0",
            exact_bound_lexeme_s="9.0",
            disposition="valid",
            custody_locator="/reviewed/historical-range-expander",
            observation_kind="historical-import",
        )
        snapshot = replace(
            snapshot,
            observations=(*snapshot.observations, imported),
            head_sequence=imported.sequence,
            head_digest=imported.receipt_digest,
        )
        by_attempt = {
            candidate.attempt_id: candidate for candidate in registered
        }
        with patch(
            "joulewise.calibration_bracketing._candidate_from_observation",
            side_effect=lambda observation: by_attempt.get(observation.attempt_id),
        ) as authenticate:
            discovered = discover_calibration_candidates(snapshot)
        self.assertEqual(discovered, tuple(registered))
        self.assertNotIn(
            imported.attempt_id,
            [call.args[0].attempt_id for call in authenticate.call_args_list],
        )

        result, reasons = _evaluate_with_unissued_acceptance(
            discovered,
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=self.bindings,
            policy=self.policy,
            ledger_snapshot=snapshot,
            _allow_unissued_fixture=True,
        )
        self.assertEqual(reasons, ())
        self.assertNotIn(
            "new_valid_same_identity_capture_expands_observed_range",
            result["acceptance"]["prospective_rederivation"]["observed_triggers"],
        )

    def test_acceptance_prior_set_must_equal_import_marked_cutoff_prefix(self) -> None:
        artifact = _unissued_acceptance_fixture()
        snapshot, registered = _fixture_snapshot(
            [
                self.candidate("pre", 99.0, "0.025"),
                self.candidate("post", 111.0, "0.026"),
            ]
        )
        imported = replace(
            snapshot.observations[0],
            observation_kind="historical-import",
        )
        artifact["ledger_cutoff"]["sequence"] = imported.sequence
        artifact["ledger_cutoff"]["head_digest"] = imported.receipt_digest
        snapshot = replace(
            snapshot,
            observations=(imported, *snapshot.observations[1:]),
            baseline_sequence=imported.sequence,
            baseline_digest=imported.receipt_digest,
        )
        with patch(
            "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
            return_value=artifact,
        ):
            _result, reasons = _evaluate_calibration_bracket(
                registered[1:],
                window_start_s=100.0,
                window_end_s=110.0,
                bindings=self.bindings,
                policy=self.policy,
                ledger_snapshot=snapshot,
                _allow_unissued_fixture=True,
            )
        self.assertEqual(reasons, ("calibration_ledger_baseline_missing",))

    def candidate(
        self,
        name: str,
        capture_s: float,
        bound_s: Decimal | str | float,
        *,
        protocol_id: str = PROTOCOL_ID,
        bindings: dict | None = None,
    ) -> CalibrationCandidate:
        corpus_alias = {
            "pre": "20260722T145535-e941c821",
            "post": "20260722T194118-9dc0749d",
            "pre-v3": "20260722T214220-1acdbbc0",
            "post-v3": "20260722T215127-eeef661a",
        }
        new_observation = name in {
            "range-expander",
            "current-pre",
            "current-post",
            "window-b-new-systematic-pre",
            "window-b-post",
        }
        manifest_sha256 = (
            hashlib.sha256(f"manifest:{name}".encode()).hexdigest()
            if new_observation
            else "ab" * 32
        )
        evidence_sha256 = (
            hashlib.sha256(f"evidence:{name}".encode()).hexdigest()
            if new_observation
            else "cd" * 32
        )
        return CalibrationCandidate(
            relative_path=(
                f"instrument_validation/{corpus_alias.get(name, name)}"
            ),
            manifest_sha256=manifest_sha256,
            evidence_sha256=evidence_sha256,
            protocol_id=protocol_id,
            capture_wall_time_s=capture_s,
            b_fiducial_s=bound_s,
            bindings=self.bindings if bindings is None else bindings,
        )

    def _bound_session_fixture(self):
        specifications = (
            ("neighbor-pre", 98.0, "0.025", None, None, 1),
            ("neighbor-post", 112.0, "0.026", None, None, 2),
            ("session-pre", 99.0, "0.024", "session-alpha", "pre", 4),
            ("session-post", 111.0, "0.027", "session-alpha", "post", 5),
        )
        observations = []
        candidates = []
        for name, capture, bound, session_id, slot, sequence in specifications:
            manifest = hashlib.sha256(f"manifest:{name}".encode()).hexdigest()
            evidence = hashlib.sha256(f"evidence:{name}".encode()).hexdigest()
            hashes = {
                "manifest.json": manifest,
                "instrument_evidence.json": evidence,
            }
            content_id = content_id_from_artifact_hashes(hashes)
            receipt_digest = hashlib.sha256(f"receipt:{name}".encode()).hexdigest()
            attempt_id = f"attempt-{name}"
            candidate = replace(
                self.candidate(name, capture, bound),
                manifest_sha256=manifest,
                evidence_sha256=evidence,
                attempt_id=attempt_id,
                content_id=content_id,
                ledger_receipt_digest=receipt_digest,
                bracket_session_id=session_id,
                bracket_slot=slot,
                bracket_window_id="window-alpha" if session_id else None,
                bracket_plan_id="plan-alpha" if session_id else None,
                bracket_plan_sha256="a" * 64 if session_id else None,
                bracket_evidence_root_id="evidence-alpha" if session_id else None,
                bracket_runs_root="/synthetic/root-alpha" if session_id else None,
            )
            candidates.append(candidate)
            observations.append(
                LedgerObservation(
                    sequence=sequence,
                    receipt_digest=receipt_digest,
                    attempt_id=attempt_id,
                    content_id=content_id,
                    artifact_sha256=MappingProxyType(hashes),
                    identity_epoch=MappingProxyType(
                        {
                            field: self.bindings[field]
                            for field in (
                                "os_build",
                                "hardware_model",
                                "power_policy",
                                "sampling_interval_ms",
                                "estimator_revision",
                                "pulse_protocol_id",
                            )
                        }
                    ),
                    t1_bindings=MappingProxyType(dict(self.bindings)),
                    capture_wall_time_s=str(capture),
                    exact_bound_lexeme_s=bound,
                    disposition="valid",
                    custody_locator=f"/synthetic/{name}",
                    observation_kind=(
                        "bracket-session-finalized" if session_id else "live-capture"
                    ),
                    bracket_session_id=session_id,
                    bracket_slot=slot,
                    bracket_window_id="window-alpha" if session_id else None,
                    bracket_plan_id="plan-alpha" if session_id else None,
                    bracket_plan_sha256="a" * 64 if session_id else None,
                    bracket_evidence_root_id="evidence-alpha" if session_id else None,
                    bracket_runs_root=(
                        "/synthetic/root-alpha" if session_id else None
                    ),
                )
            )
        by_slot = {
            observation.bracket_slot: observation
            for observation in observations
            if observation.bracket_slot is not None
        }
        capability_digest = hashlib.sha256(b"capability-alpha").hexdigest()
        session = CalibrationBracketSession(
            session_id="session-alpha",
            window_id="window-alpha",
            plan_id="plan-alpha",
            plan_sha256="a" * 64,
            evidence_root_id="evidence-alpha",
            runs_root="/synthetic/root-alpha",
            capability_receipt_digest=capability_digest,
            capability_sequence=3,
            slot_attempt_ids=MappingProxyType(
                {slot: observation.attempt_id for slot, observation in by_slot.items()}
            ),
            state="finalized",
            finalized_slots=MappingProxyType(by_slot),
        )
        receipt_digests = [
            observations[0].receipt_digest,
            observations[1].receipt_digest,
            capability_digest,
            by_slot["pre"].receipt_digest,
            by_slot["post"].receipt_digest,
        ]
        snapshot = CalibrationLedgerSnapshot(
            ledger_schema=LEDGER_SCHEMA,
            ledger_path=Path("synthetic-session-ledger.jsonl"),
            head_sequence=5,
            head_digest=by_slot["post"].receipt_digest,
            receipts=tuple(
                MappingProxyType({"receipt_digest": digest})
                for digest in receipt_digests
            ),
            observations=tuple(sorted(observations, key=lambda item: item.sequence)),
            refusal_reasons=(),
            bracket_sessions=(session,),
            baseline_sequence=0,
            baseline_digest=GENESIS_DIGEST,
        )
        binding = build_calibration_bracket_binding(
            snapshot,
            session_id="session-alpha",
            window_id="window-alpha",
            plan_id="plan-alpha",
            plan_sha256="a" * 64,
            evidence_root_id="evidence-alpha",
            runs_root="/synthetic/root-alpha",
        )
        return snapshot, candidates, binding

    def test_exact_session_binding_selects_reserved_pair_not_neighbors(self) -> None:
        snapshot, candidates, binding = self._bound_session_fixture()
        resolved = validate_calibration_bracket_binding(
            binding,
            snapshot,
            window_id="window-alpha",
            plan_id="plan-alpha",
            plan_sha256="a" * 64,
            evidence_root_id="evidence-alpha",
            runs_root="/synthetic/root-alpha",
        )
        self.assertIsNotNone(resolved)
        with patch(
            "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
            return_value=_unissued_acceptance_fixture(),
        ):
            result, reasons = _evaluate_calibration_bracket(
                candidates,
                window_start_s=100.0,
                window_end_s=110.0,
                bindings=self.bindings,
                policy=self.policy,
                ledger_snapshot=snapshot,
                bracket_binding=binding,
                bracket_window_id="window-alpha",
                bracket_plan_id="plan-alpha",
                bracket_plan_sha256="a" * 64,
                bracket_evidence_root_id="evidence-alpha",
                bracket_runs_root="/synthetic/root-alpha",
                _allow_unissued_fixture=True,
            )
        self.assertEqual(reasons, ())
        self.assertEqual(result["pre"]["attempt_id"], "attempt-session-pre")
        self.assertEqual(result["post"]["attempt_id"], "attempt-session-post")
        self.assertEqual(
            result["bracket_binding"]["binding_digest"],
            binding["binding_digest"],
        )

    def test_l5_later_same_t1_calibration_from_another_runs_root_cannot_be_borrowed(
        self,
    ) -> None:
        snapshot, candidates, binding = self._bound_session_fixture()
        later_other_root = replace(
            candidates[-1],
            relative_path="/synthetic/root-beta/instrument_validation/later-post",
            bracket_runs_root="/synthetic/root-beta",
        )
        supplied = [*candidates[:-1], later_other_root]
        with patch(
            "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
            return_value=_unissued_acceptance_fixture(),
        ):
            _result, reasons = _evaluate_calibration_bracket(
                supplied,
                window_start_s=100.0,
                window_end_s=110.0,
                bindings=self.bindings,
                policy=self.policy,
                ledger_snapshot=snapshot,
                bracket_binding=binding,
                bracket_window_id="window-alpha",
                bracket_plan_id="plan-alpha",
                bracket_plan_sha256="a" * 64,
                bracket_evidence_root_id="evidence-alpha",
                bracket_runs_root="/synthetic/root-alpha",
                _allow_unissued_fixture=True,
            )
        self.assertEqual(reasons, ("calibration_ledger_off_ledger_artifact",))

        with patch(
            "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
            return_value=_unissued_acceptance_fixture(),
        ):
            _result, reasons = _evaluate_calibration_bracket(
                candidates,
                window_start_s=100.0,
                window_end_s=110.0,
                bindings=self.bindings,
                policy=self.policy,
                ledger_snapshot=snapshot,
                bracket_binding=binding,
                bracket_window_id="window-alpha",
                bracket_plan_id="plan-alpha",
                bracket_plan_sha256="a" * 64,
                bracket_evidence_root_id="evidence-alpha",
                bracket_runs_root="/synthetic/root-beta",
                _allow_unissued_fixture=True,
            )
        self.assertEqual(reasons, ("calibration_bracket_binding_invalid",))

    def test_session_candidates_refuse_missing_neighbor_substituted_or_cross_window_binding(
        self,
    ) -> None:
        snapshot, candidates, binding = self._bound_session_fixture()
        self.assertIsNone(validate_calibration_bracket_binding(binding, snapshot))
        with patch(
            "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
            return_value=_unissued_acceptance_fixture(),
        ):
            _result, reasons = _evaluate_calibration_bracket(
                candidates,
                window_start_s=100.0,
                window_end_s=110.0,
                bindings=self.bindings,
                policy=self.policy,
                ledger_snapshot=snapshot,
                _allow_unissued_fixture=True,
            )
        self.assertEqual(reasons, ("calibration_bracket_binding_missing",))

        substituted = json.loads(json.dumps(binding))
        substituted["endpoints"]["pre"] = {
            "attempt_id": candidates[0].attempt_id,
            "receipt_digest": candidates[0].ledger_receipt_digest,
            "content_digest": candidates[0].content_id,
        }
        substituted["binding_digest"] = _canonical_sha256(
            {
                key: value
                for key, value in substituted.items()
                if key != "binding_digest"
            }
        )
        self.assertIsNone(
            validate_calibration_bracket_binding(
                substituted,
                snapshot,
                window_id="window-alpha",
                plan_id="plan-alpha",
                plan_sha256="a" * 64,
                evidence_root_id="evidence-alpha",
                runs_root="/synthetic/root-alpha",
            )
        )

        cross_window = json.loads(json.dumps(binding))
        cross_window["window_id"] = "window-beta"
        cross_window["binding_digest"] = _canonical_sha256(
            {
                key: value
                for key, value in cross_window.items()
                if key != "binding_digest"
            }
        )
        self.assertIsNone(
            validate_calibration_bracket_binding(
                cross_window,
                snapshot,
                window_id="window-alpha",
                plan_id="plan-alpha",
                plan_sha256="a" * 64,
                evidence_root_id="evidence-alpha",
                runs_root="/synthetic/root-alpha",
            )
        )

    def test_open_and_aborted_session_observations_never_leak_as_candidates(self) -> None:
        snapshot, candidates, _binding = self._bound_session_fixture()
        session = snapshot.bracket_sessions[0]
        open_session = replace(
            session,
            state="open",
            finalized_slots=MappingProxyType({"pre": session.finalized_slots["pre"]}),
        )
        open_snapshot = replace(
            snapshot,
            observations=tuple(
                observation
                for observation in snapshot.observations
                if observation.bracket_slot != "post"
            ),
            bracket_sessions=(open_session,),
            head_sequence=4,
            head_digest=session.finalized_slots["pre"].receipt_digest,
            receipts=(
                *snapshot.receipts[:2],
                MappingProxyType(
                    {
                        "event": "bracket-session-open",
                        "session_id": "session-alpha",
                        "predecessor_digest": snapshot.receipts[1]["receipt_digest"],
                        "receipt_digest": session.capability_receipt_digest,
                    }
                ),
                MappingProxyType(
                    {
                        "event": "bracket-session-slot-finalization",
                        "session_id": "session-alpha",
                        "receipt_digest": session.finalized_slots["pre"].receipt_digest,
                    }
                ),
            ),
            refusal_reasons=(
                "calibration_ledger_bracket_session_open",
                "calibration_ledger_head_mismatch",
            ),
            committed_head_sequence=2,
            committed_head_digest=snapshot.receipts[1]["receipt_digest"],
        )
        by_attempt = {candidate.attempt_id: candidate for candidate in candidates}
        with patch(
            "joulewise.calibration_bracketing._candidate_from_observation",
            side_effect=lambda observation: by_attempt[observation.attempt_id],
        ):
            open_candidates = discover_calibration_candidates(open_snapshot)
        self.assertEqual(
            [candidate.bracket_session_id for candidate in open_candidates],
            [None, None],
        )

        aborted_session = replace(open_session, state="aborted")
        aborted_snapshot = replace(
            open_snapshot,
            # Keep the finalized PRE in the R2 observation universe.  The
            # discovery filter must consult governed session state instead of
            # laundering a synthetic snapshot by assuming observations were
            # pre-filtered by the loader.
            observations=open_snapshot.observations,
            bracket_sessions=(aborted_session,),
            refusal_reasons=(),
        )
        with patch(
            "joulewise.calibration_bracketing._candidate_from_observation",
            side_effect=lambda observation: by_attempt[observation.attempt_id],
        ):
            discovered = discover_calibration_candidates(aborted_snapshot)
        self.assertEqual(
            [candidate.bracket_session_id for candidate in discovered],
            [None, None],
        )

    def test_claim_window_passes_and_embeds_never_zero_allowance_once(self) -> None:
        # Exact H2 defect shape: a single sample maximum used to stand in for
        # temporal instrument stability. Two causal endpoints now bracket it.
        result, reasons = evaluate_calibration_bracket(
            [self.candidate("pre", 99.0, 0.020), self.candidate("post", 111.0, 0.027)],
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=self.bindings,
            policy=self.policy,
        )
        self.assertEqual(reasons, ())
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["endpoint_max_b_fiducial_s"], 0.027)
        self.assertEqual(result["calibration_drift_allowance_s"], 0.010818)
        self.assertEqual(result["b_fiducial_s"], 0.037818)

    def test_missing_post_bracket_refuses_claim(self) -> None:
        result, reasons = evaluate_calibration_bracket(
            [self.candidate("pre", 99.0, 0.020)],
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=self.bindings,
            policy=self.policy,
        )
        self.assertEqual(result["status"], "failed")
        self.assertEqual(reasons, ("instrument_calibration_bracket_missing",))

    def test_claim_bracket_refuses_v2_only_candidates_but_accepts_v3_pair(self) -> None:
        # K4 defect shape: fresh, binding-matched v2 validation artifacts are
        # still reduction evidence, but do not carry v3's governed 95/95
        # claim calibration. Replacing only the protocol with v3 passes.
        v2 = [
            self.candidate("pre-v2", 99.0, 0.020, protocol_id=PROTOCOL_V2_ID),
            self.candidate("post-v2", 111.0, 0.027, protocol_id=PROTOCOL_V2_ID),
        ]
        result, reasons = evaluate_calibration_bracket(
            v2,
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=self.bindings,
            policy=self.policy,
        )
        self.assertEqual(result["status"], "failed")
        self.assertEqual(reasons, ("instrument_calibration_bracket_missing",))

        v3 = [
            self.candidate("pre-v3", 99.0, 0.020),
            self.candidate("post-v3", 111.0, 0.027),
        ]
        result, reasons = evaluate_calibration_bracket(
            v3,
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=self.bindings,
            policy=self.policy,
        )
        self.assertEqual(reasons, ())
        self.assertEqual(result["status"], "passed")

    def test_bracket_drift_over_d079_budget_refuses_claim(self) -> None:
        result, reasons = evaluate_calibration_bracket(
            [
                self.candidate("pre", 99.0, "0.020"),
                self.candidate("post", 111.0, "0.035"),
            ],
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=self.bindings,
            policy=self.policy,
        )
        self.assertAlmostEqual(result["drift_s"], 0.015)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(reasons, ("instrument_calibration_mismatch",))

    def test_d079_budgeted_drift_above_obsolete_cliff_passes_with_allowance(self) -> None:
        result, reasons = evaluate_calibration_bracket(
            [self.candidate("pre", 99.0, 0.020), self.candidate("post", 111.0, 0.031)],
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=self.bindings,
            policy=self.policy,
        )
        self.assertEqual(reasons, ())
        self.assertEqual(result["status"], "passed")
        self.assertEqual(
            result["acceptance"]["drift"]["status"], "passed_budgeted"
        )
        self.assertEqual(result["calibration_drift_allowance_s"], 0.011)
        self.assertEqual(result["b_fiducial_s"], 0.042)
        self.assertEqual(
            result["policy"]["calibration_bracket_max_drift_s_role"],
            "legacy_obsolete_not_an_acceptance_comparator",
        )

    def test_d079_drift_beyond_budget_refuses_with_recorded_basis(self) -> None:
        result, reasons = evaluate_calibration_bracket(
            [
                self.candidate("pre", 99.0, "0.020"),
                self.candidate("post", 111.0, "0.035"),
            ],
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=self.bindings,
            policy=self.policy,
        )
        self.assertEqual(result["status"], "failed")
        self.assertEqual(reasons, ("instrument_calibration_mismatch",))
        self.assertEqual(
            result["acceptance"]["drift"]["status"], "budget_exceeded"
        )
        self.assertEqual(
            result["acceptance"]["drift"]["excess_over_screen_s"],
            "0.004182",
        )
        self.assertEqual(
            result["acceptance"]["drift"][
                "excess_over_budget_ceiling_s"
            ],
            "0.002906833909406142",
        )
        self.assertEqual(
            result["acceptance"]["drift"]["budget_headroom_s"],
            "0.001275166090593858",
        )
        self.assertIsNone(result["calibration_drift_allowance_s"])
        self.assertNotIn("allowance", result["acceptance"])

    def test_d102_decimal_boundary_sweep_is_exact_and_inclusive(self) -> None:
        cases = (
            ("exact-screen", "0.030818", "passed", "0.010818"),
            (
                "exact-ceiling",
                "0.032093166090593858",
                "passed",
                "0.012093166090593858",
            ),
            (
                "one-decimal-unit-beyond",
                "0.032093166090593859",
                "failed",
                "0.012093166090593859",
            ),
        )
        for name, post, status, observed in cases:
            with self.subTest(name=name):
                result, reasons = evaluate_calibration_bracket(
                    [
                        self.candidate("pre", 99.0, "0.020"),
                        self.candidate("post", 111.0, post),
                    ],
                    window_start_s=100.0,
                    window_end_s=110.0,
                    bindings=self.bindings,
                    policy=self.policy,
                )
                self.assertEqual(result["status"], status)
                self.assertEqual(
                    result["acceptance"]["drift"]["observed_s"], observed
                )
                self.assertEqual(
                    reasons,
                    ()
                    if status == "passed"
                    else ("instrument_calibration_mismatch",),
                )
                drift = result["acceptance"]["drift"]
                self.assertEqual(
                    drift["budget_headroom_s"],
                    "0.001275166090593858",
                )
                expected_screen_excess = {
                    "exact-screen": "0",
                    "exact-ceiling": "0.001275166090593858",
                    "one-decimal-unit-beyond": "0.001275166090593859",
                }[name]
                expected_ceiling_excess = (
                    "0.000000000000000001"
                    if name == "one-decimal-unit-beyond"
                    else "0"
                )
                self.assertEqual(
                    drift["excess_over_screen_s"], expected_screen_excess
                )
                self.assertEqual(
                    drift["excess_over_budget_ceiling_s"],
                    expected_ceiling_excess,
                )
                if status == "passed":
                    self.assertEqual(
                        result["acceptance"]["allowance"]["value_s"],
                        observed,
                    )
                else:
                    self.assertNotIn("allowance", result["acceptance"])

        exact_ceiling = float(Decimal("0.032093166090593858"))
        one_binary64_ulp_beyond = math.nextafter(exact_ceiling, math.inf)
        result, reasons = evaluate_calibration_bracket(
            [
                self.candidate("pre", 99.0, 0.020),
                self.candidate("post", 111.0, one_binary64_ulp_beyond),
            ],
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=self.bindings,
            policy=self.policy,
        )
        self.assertEqual(result["status"], "failed")
        self.assertEqual(reasons, ("instrument_calibration_mismatch",))
        self.assertGreater(
            Decimal(result["acceptance"]["drift"]["observed_s"]),
            Decimal("0.012093166090593858"),
        )

        zero, reasons = evaluate_calibration_bracket(
            [
                self.candidate("pre", 99.0, "0.025"),
                self.candidate("post", 111.0, "0.025"),
            ],
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=self.bindings,
            policy=self.policy,
        )
        self.assertEqual(reasons, ())
        self.assertEqual(zero["acceptance"]["drift"]["observed_s"], "0.000")
        self.assertEqual(zero["acceptance"]["allowance"]["value_s"], "0.010818")

    def test_invalid_acceptance_arithmetic_refuses_before_drift_classification(self) -> None:
        candidates = [
            self.candidate("pre", 99.0, "0.020"),
            self.candidate("post", 111.0, "0.021"),
        ]
        snapshot, registered = _fixture_snapshot(candidates)
        artifact = _unissued_acceptance_fixture()
        artifact["decimal_derivation"]["ratified_operatives"][
            "max_budgetable_excess_s"
        ] = "0"
        artifact["derivation_sha256"] = _canonical_sha256(
            {
                key: value
                for key, value in artifact.items()
                if key != "derivation_sha256"
            }
        )
        self.assertFalse(_valid_acceptance_bound(artifact))
        with patch(
            "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
            return_value=artifact,
        ):
            result, reasons = _evaluate_calibration_bracket(
                registered,
                window_start_s=100.0,
                window_end_s=110.0,
                bindings=self.bindings,
                policy=self.policy,
                ledger_snapshot=snapshot,
                _allow_unissued_fixture=True,
            )
        self.assertEqual(reasons, ("invalid_acceptance_arithmetic",))
        self.assertEqual(
            result["acceptance"]["drift"]["status"],
            "invalid_acceptance_arithmetic",
        )
        self.assertIsNone(result["acceptance"]["preflight"])
        self.assertIsNone(result["calibration_drift_allowance_s"])
        self.assertNotIn("allowance", result["acceptance"])

    def test_t1_mismatched_candidate_remains_ineligible_under_d079_v2(self) -> None:
        mismatched = dict(self.bindings)
        mismatched["power_policy"] = "configs/campaign_policies/quiet_mac.json"
        result, reasons = evaluate_calibration_bracket(
            [
                self.candidate("pre", 99.0, 0.020),
                self.candidate("post-mismatch", 111.0, 0.020, bindings=mismatched),
            ],
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=self.bindings,
            policy=self.policy,
        )
        self.assertEqual(result["status"], "failed")
        self.assertIsNone(result["pre"])
        self.assertIsNone(result["post"])
        self.assertEqual(reasons, ("instrument_calibration_bracket_missing",))
        self.assertEqual(result["acceptance"]["freshness"]["status"], "fresh")

    def test_window_a_t1_mismatch_shape_still_cannot_form_bracket(self) -> None:
        window_a_post_bindings = dict(self.bindings)
        window_a_post_bindings["power_policy"] = (
            "configs/campaign_policies/quiet_mac_p2_production.json"
        )
        result, reasons = evaluate_calibration_bracket(
            [
                self.candidate("window-a-pre", 99.0, 0.022),
                self.candidate(
                    "window-a-deviation-post",
                    111.0,
                    0.024,
                    bindings=window_a_post_bindings,
                ),
            ],
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=self.bindings,
            policy=self.policy,
        )
        self.assertEqual(result["status"], "failed")
        self.assertIsNone(result["pre"])
        self.assertIsNone(result["post"])
        self.assertEqual(reasons, ("instrument_calibration_bracket_missing",))

    def test_identity_epoch_violation_refuses_stale_acceptance_bound(self) -> None:
        changed_epoch = dict(self.bindings)
        changed_epoch["os_build"] = "25F85"
        result, reasons = evaluate_calibration_bracket(
            [
                self.candidate("pre", 99.0, 0.020, bindings=changed_epoch),
                self.candidate("post", 111.0, 0.021, bindings=changed_epoch),
            ],
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=changed_epoch,
            policy=self.policy,
        )
        self.assertEqual(result["status"], "failed")
        self.assertEqual(
            reasons, ("calibration_acceptance_bound_stale",)
        )
        self.assertEqual(result["acceptance"]["freshness"]["status"], "stale")

    def test_f1_freshness_uses_six_field_epoch_not_full_t1(self) -> None:
        changed = dict(self.bindings)
        changed["mlx_version"] = "different-but-exactly-t1-matched"
        result, reasons = evaluate_calibration_bracket(
            [
                self.candidate("pre", 99.0, "0.025", bindings=changed),
                self.candidate("post", 111.0, "0.026", bindings=changed),
            ],
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=changed,
            policy=self.policy,
        )
        self.assertEqual(reasons, ())
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["acceptance"]["freshness"]["stale_fields"], [])

    def test_f2_estimator_digest_closure_is_exactly_four_modules(self) -> None:
        artifact = load_calibration_acceptance_bound()
        self.assertIsNotNone(artifact)
        self.assertEqual(
            set(artifact["prospective_rederivation"]["estimator_code_sha256"]),
            {
                "joulewise/powermetrics_fiducial.py",
                "joulewise/uncertainty_evidence.py",
                "joulewise/adapters/powermetrics.py",
                "joulewise/reduce.py",
            },
        )

    def test_systematic_preflight_level_failure_is_never_budgeted(self) -> None:
        result, reasons = evaluate_calibration_bracket(
            [self.candidate("pre", 99.0, 0.034), self.candidate("post", 111.0, 0.023)],
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=self.bindings,
            policy=self.policy,
        )
        self.assertEqual(result["status"], "failed")
        self.assertEqual(reasons, ("instrument_calibration_mismatch",))
        self.assertEqual(result["acceptance"]["preflight"]["status"], "failed")
        self.assertEqual(
            result["acceptance"]["preflight"]["failure_class"],
            "systematic_not_budgetable",
        )
        self.assertEqual(
            result["acceptance"]["prospective_rederivation"][
                "observed_triggers"
            ],
            ["new_systematic_failure_challenges_preflight_screen"],
        )
        self.assertIsNone(result["calibration_drift_allowance_s"])

    def test_window_b_systematic_failure_precedes_rederivation_staleness(self) -> None:
        result, reasons = evaluate_calibration_bracket(
            [
                self.candidate(
                    "window-b-new-systematic-pre",
                    99.0,
                    "0.035435840879704805",
                ),
                self.candidate("window-b-post", 111.0, "0.023"),
            ],
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=self.bindings,
            policy=self.policy,
        )
        self.assertEqual(result["status"], "failed")
        self.assertEqual(reasons, ("instrument_calibration_mismatch",))
        self.assertEqual(result["acceptance"]["preflight"]["status"], "failed")
        self.assertEqual(
            result["acceptance"]["prospective_rederivation"][
                "observed_triggers"
            ],
            [
                "new_valid_same_identity_capture_expands_observed_range",
                "new_systematic_failure_challenges_preflight_screen",
            ],
        )

    def test_unselected_same_identity_range_expander_stales_artifact(self) -> None:
        snapshot, registered = _fixture_snapshot(
            [
                replace(
                    self.candidate("range-expander", 99.0, "0.022"),
                    relative_path=(
                        "/authenticated-custody/another-root/"
                        "instrument_validation/range-expander"
                    ),
                ),
                self.candidate("current-pre", 199.0, "0.025"),
                self.candidate("current-post", 211.0, "0.026"),
            ]
        )
        reader = SimpleNamespace(
            measured_window=lambda: SimpleNamespace(start_s=200.0, end_s=210.0),
            metadata=lambda: {
                "instrument_calibration": {"bindings": self.bindings}
            },
        )

        def discover(source: object) -> tuple[CalibrationCandidate, ...]:
            return tuple(registered) if source is snapshot else ()

        with (
            patch(
                "joulewise.calibration_bracketing.BundleReader",
                return_value=reader,
            ),
            patch(
                "joulewise.calibration_bracketing.discover_calibration_candidates",
                side_effect=discover,
            ),
            patch(
                "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
                return_value=_unissued_acceptance_fixture(),
            ),
        ):
            result, reasons = calibration_bracket_for_bundles(
                Path("/caller-root"),
                [Path("/caller-root/window-member")],
                self.policy,
                ledger_snapshot=snapshot,
                _allow_unissued_fixture=True,
            )
        self.assertEqual(result["status"], "failed")
        self.assertEqual(reasons, ("calibration_acceptance_bound_stale",))
        self.assertEqual(result["acceptance"]["freshness"]["status"], "stale")
        self.assertEqual(
            result["acceptance"]["prospective_rederivation"][
                "candidate_set_boundary"
            ],
            "authenticated_calibration_ledger_snapshot_only",
        )
        self.assertFalse(
            result["acceptance"]["prospective_rederivation"][
                "global_runs_root_scan"
            ]
        )
        self.assertEqual(
            result["acceptance"]["prospective_rederivation"][
                "observed_triggers"
            ],
            ["new_valid_same_identity_capture_expands_observed_range"],
        )
        self.assertTrue(
            result["pre"]["relative_path"].endswith("current-pre")
        )
        self.assertTrue(
            result["post"]["relative_path"].endswith("current-post")
        )

    def test_off_ledger_candidate_refuses_even_beside_registered_pair(self) -> None:
        candidates = [
            self.candidate("pre", 99.0, "0.025"),
            self.candidate("post", 111.0, "0.026"),
        ]
        snapshot, registered = _fixture_snapshot(candidates)
        off_ledger = replace(
            self.candidate("unregistered-copy", 105.0, "0.0255"),
            attempt_id="off-ledger",
            content_id="f" * 64,
            ledger_receipt_digest="e" * 64,
        )
        result, reasons = _evaluate_with_unissued_acceptance(
            [*registered, off_ledger],
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=self.bindings,
            policy=self.policy,
            ledger_snapshot=snapshot,
            _allow_unissued_fixture=True,
        )
        self.assertEqual(result["status"], "failed")
        self.assertEqual(reasons, ("calibration_ledger_off_ledger_artifact",))

        _result, omitted_reasons = _evaluate_with_unissued_acceptance(
            registered[:1],
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=self.bindings,
            policy=self.policy,
            ledger_snapshot=snapshot,
            _allow_unissued_fixture=True,
        )
        self.assertEqual(
            omitted_reasons,
            ("calibration_ledger_off_ledger_artifact",),
        )

    def test_prior_set_subtraction_does_not_treat_known_holdout_as_new(self) -> None:
        result, reasons = evaluate_calibration_bracket(
            [
                self.candidate("pre", 99.0, "0.020"),
                self.candidate("post", 111.0, "0.020"),
            ],
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=self.bindings,
            policy=self.policy,
        )
        self.assertEqual(reasons, ())
        self.assertEqual(result["status"], "passed")
        self.assertEqual(
            result["acceptance"]["prospective_rederivation"][
                "observed_triggers"
            ],
            [],
        )

    def test_corpus_doubling_counts_38_total_valid_distinct_observations(self) -> None:
        artifact = _unissued_acceptance_fixture()
        candidates = []
        for index, member in enumerate(artifact["derivation_corpus"]["members"]):
            candidates.append(
                replace(
                    self.candidate(
                        f"prior-{index}",
                        (
                            99.0
                            if index == 0
                            else 111.0
                            if index == 1
                            else 120.0 + index
                        ),
                        "0.025",
                    ),
                    manifest_sha256=member["manifest_sha256"],
                    evidence_sha256=member["instrument_evidence_sha256"],
                )
            )
        for index in range(19):
            candidates.append(
                replace(
                    self.candidate(f"new-{index}", 200.0 + index, "0.025"),
                    manifest_sha256=hashlib.sha256(
                        f"new-manifest-{index}".encode()
                    ).hexdigest(),
                    evidence_sha256=hashlib.sha256(
                        f"new-evidence-{index}".encode()
                    ).hexdigest(),
                )
            )
        snapshot, registered = _fixture_snapshot(candidates)
        result, reasons = _evaluate_with_unissued_acceptance(
            registered,
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=self.bindings,
            policy=self.policy,
            ledger_snapshot=snapshot,
            _allow_unissued_fixture=True,
        )
        self.assertEqual(reasons, ("calibration_acceptance_bound_stale",))
        self.assertEqual(
            result["acceptance"]["prospective_rederivation"][
                "observed_triggers"
            ],
            ["corpus_doubles_from_19_to_38"],
        )

    def test_new_abandoned_observation_refuses_with_or_without_content(self) -> None:
        candidates = [
            self.candidate("pre", 99.0, "0.025"),
            self.candidate("post", 111.0, "0.026"),
        ]
        content_hashes = {
            "manifest.json": hashlib.sha256(b"abandoned-manifest").hexdigest(),
            "instrument_evidence.json": hashlib.sha256(
                b"abandoned-evidence"
            ).hexdigest(),
        }
        cases = (
            (
                "content-bearing",
                content_hashes,
                content_id_from_artifact_hashes(content_hashes),
            ),
            ("contentless", {}, None),
        )
        for label, hashes, content_id in cases:
            with self.subTest(label=label):
                abandoned = LedgerObservation(
                    sequence=6,
                    receipt_digest=hashlib.sha256(
                        f"abandoned-receipt-{label}".encode()
                    ).hexdigest(),
                    attempt_id=f"abandoned-attempt-{label}",
                    content_id=content_id,
                    artifact_sha256=MappingProxyType(hashes),
                    identity_epoch=MappingProxyType(
                        {
                            field: self.bindings.get(field)
                            for field in (
                                "os_build",
                                "hardware_model",
                                "power_policy",
                                "sampling_interval_ms",
                                "estimator_revision",
                                "pulse_protocol_id",
                            )
                        }
                    ),
                    t1_bindings=MappingProxyType(
                        {
                            field: self.bindings.get(field)
                            for field in V2_BINDING_FIELDS
                        }
                    ),
                    capture_wall_time_s="105.0",
                    exact_bound_lexeme_s=None,
                    disposition="abandoned",
                    custody_locator=(
                        f"/authenticated-custody/abandoned-attempt-{label}"
                    ),
                )
                snapshot, registered = _fixture_snapshot(
                    candidates,
                    extra_observations=(abandoned,),
                )
                result, reasons = _evaluate_with_unissued_acceptance(
                    registered,
                    window_start_s=100.0,
                    window_end_s=110.0,
                    bindings=self.bindings,
                    policy=self.policy,
                    ledger_snapshot=snapshot,
                    _allow_unissued_fixture=True,
                )
                self.assertEqual(result["status"], "failed")
                self.assertEqual(
                    reasons, ("calibration_observation_unclassifiable",)
                )

    def test_acceptance_artifact_rederives_from_decimal_member_table(self) -> None:
        artifact = load_calibration_acceptance_bound()
        self.assertIsNotNone(artifact)
        self.assertEqual(artifact["derivation_corpus"]["n"], 19)
        self.assertEqual(
            artifact["decimal_derivation"]["source_statistics"]["range_s"],
            "0.010817749309353528",
        )
        tampered = json.loads(json.dumps(artifact))
        tampered["derivation_corpus"]["members"][0]["b_fiducial_s"] = "0.030"
        tampered["derivation_sha256"] = _canonical_sha256(
            {
                key: value
                for key, value in tampered.items()
                if key != "derivation_sha256"
            }
        )
        self.assertFalse(_valid_acceptance_bound(tampered))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tampered.json"
            path.write_text(json.dumps(tampered), encoding="utf-8")
            self.assertIsNone(load_calibration_acceptance_bound(path))

    def test_rekeyed_self_consistent_artifact_is_not_authenticated(self) -> None:
        artifact = load_calibration_acceptance_bound()
        self.assertIsNotNone(artifact)
        rekeyed = json.loads(json.dumps(artifact))
        rekeyed["identity_epoch"]["os_build"] = "25F85"
        rekeyed["prior_observation_set"]["epoch_catalog"]["d079_epoch"][
            "os_build"
        ] = "25F85"
        rekeyed["derivation_sha256"] = _canonical_sha256(
            {
                key: value
                for key, value in rekeyed.items()
                if key != "derivation_sha256"
            }
        )
        # The arithmetic document remains self-consistent; only the checked-in
        # byte pin supplies the missing authority and must reject it.
        self.assertTrue(_valid_acceptance_bound(rekeyed))
        changed = dict(self.bindings)
        changed["os_build"] = "25F85"
        result, reasons = evaluate_calibration_bracket(
            [
                self.candidate("pre", 99.0, "0.025", bindings=changed),
                self.candidate("post", 111.0, "0.026", bindings=changed),
            ],
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=changed,
            policy=self.policy,
            acceptance_bound=rekeyed,
        )
        self.assertEqual(result["status"], "failed")
        self.assertEqual(reasons, ("calibration_acceptance_bound_stale",))
        self.assertEqual(result["acceptance"]["freshness"]["status"], "stale")

    def test_estimator_module_byte_change_stales_artifact_at_load(self) -> None:
        with patch(
            "joulewise.calibration_bracketing._current_estimator_code_sha256",
            return_value={
                "joulewise/powermetrics_fiducial.py": "0" * 64,
                "joulewise/uncertainty_evidence.py": "1" * 64,
                "joulewise/adapters/powermetrics.py": "2" * 64,
                "joulewise/reduce.py": "3" * 64,
            },
        ):
            self.assertIsNotNone(load_calibration_acceptance_bound())
            result, reasons = evaluate_calibration_bracket(
                [
                    self.candidate("pre", 99.0, "0.025"),
                    self.candidate("post", 111.0, "0.026"),
                ],
                window_start_s=100.0,
                window_end_s=110.0,
                bindings=self.bindings,
                policy=self.policy,
            )
        self.assertEqual(reasons, ("calibration_acceptance_bound_stale",))
        self.assertIn(
            "protocol_or_estimator_byte_change",
            result["acceptance"]["prospective_rederivation"][
                "observed_triggers"
            ],
        )

    def test_hash_rekeyed_candidate_cannot_bypass_binding_authentication(self) -> None:
        # H2 validity defect shape: rewriting a binding and then rehashing the
        # evidence/manifest must not create an authenticated bracket endpoint.
        bindings = dict(self.bindings)
        bindings.update(
            {
                "anchor_method_version": (
                    "powermetrics_native_second_censored_intersection_v1"
                ),
                "pulse_protocol_id": PROTOCOL_ID,
                "protocol_sha256": PROTOCOL_V3_SHA256,
                "estimator_revision": RESIDUAL_REGION_METHOD,
            }
        )
        canonical = json.dumps(
            bindings,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
        events = b'{"timestamp_s":99.0}\n'
        raw = b"authenticated-by-patched-physics"
        evidence = {
            "schema_version": "joulewise.instrument_evidence.v1",
            "protocol_id": PROTOCOL_ID,
            "pulse_count": PULSE_COUNT,
            "anchor_method_version": bindings["anchor_method_version"],
            "residual_region_method": RESIDUAL_REGION_METHOD,
            "residual_region_coverage_assumption": "complete accepted region",
            "residual_region_coverage_resolution_s": (
                REGION_COVERAGE_RESOLUTION_S
            ),
            "capture_wall_time_s": 99.0,
            "b_fiducial_s": 0.02,
            "max_age_s": MAX_AGE_S,
            "bindings": bindings,
            "binding_evidence": {
                "schema_version": "joulewise.instrument_binding_evidence.v1",
                "binding_vector_sha256": hashlib.sha256(canonical).hexdigest(),
                "powermetrics_binary": {
                    "path": "/usr/bin/powermetrics",
                    "sha256": bindings["powermetrics_sha256"],
                },
                "power_policy": {"id": bindings["power_policy"]},
            },
            "artifact_sha256": {
                "events.jsonl": hashlib.sha256(events).hexdigest(),
                "raw/powermetrics.plist": hashlib.sha256(raw).hexdigest(),
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            directory = root / "instrument_validation" / "candidate"
            (directory / "raw").mkdir(parents=True)
            (directory / "events.jsonl").write_bytes(events)
            (directory / "raw/powermetrics.plist").write_bytes(raw)

            def write_evidence_and_manifest() -> None:
                evidence_raw = json.dumps(evidence, sort_keys=True).encode()
                (directory / "instrument_evidence.json").write_bytes(evidence_raw)
                artifacts = {
                    "events.jsonl": hashlib.sha256(events).hexdigest(),
                    "raw/powermetrics.plist": hashlib.sha256(raw).hexdigest(),
                    "instrument_evidence.json": hashlib.sha256(
                        evidence_raw
                    ).hexdigest(),
                }
                (directory / "manifest.json").write_text(
                    json.dumps(
                        {
                            "schema_version": (
                                "joulewise.instrument_validation_manifest.v1"
                            ),
                            "protocol_id": PROTOCOL_ID,
                            "pulse_count": PULSE_COUNT,
                            "artifacts": artifacts,
                        }
                    )
                )

            write_evidence_and_manifest()
            with patch(
                "joulewise.calibration_bracketing.verify_stored_evidence_physics",
                return_value=0.02,
            ):
                candidate = load_calibration_candidate(
                    directory, runs_root=root
                )
                self.assertIsNotNone(candidate)
                self.assertEqual(candidate.b_fiducial_s, "0.02")
                evidence["bindings"]["hardware_model"] = "tampered-model"
                write_evidence_and_manifest()
                self.assertIsNone(
                    load_calibration_candidate(directory, runs_root=root)
                )


if __name__ == "__main__":
    unittest.main()
