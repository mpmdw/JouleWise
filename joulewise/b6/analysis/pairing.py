"""GAMMA's floor pairing by registered round (registration §6.2; design §5).

For a GAMMA session of round k and each floor pack P (ALPHA, BETA):

1. ``same_round``: P's counting session of round k;
2. ``later_round``: otherwise P's counting session of the smallest round greater than k;
3. ``earlier_round``: otherwise P's counting session of the largest round smaller than k;
4. ``block5``: otherwise block 5's analysed session of P, "floor from block 5" (S-17).
   Block 5's floors exist only after its release, so such a pairing runs in the
   cross-block phase.

Two counting sessions of P in one round (possible after a held pack is
resumed): the earlier t0 (design §18 D16).  Pairing reads round, t0 and
counting, never an energy.  Rules 2 and 3 can change while sessions still
arrive, so a pairing is final only once the loop has closed (``final``).
"""
from __future__ import annotations

from dataclasses import dataclass

from joulewise.b6.analysis.census import Census, SessionEntry

BLOCK5 = "block5"
FLOOR_PACKS = ("alpha", "beta")
RULES = ("same_round", "later_round", "earlier_round", "block5")


@dataclass(frozen=True)
class Floor:
    pack: str
    session_id: str          # a block-6 session id, or BLOCK5
    rule: str

    @property
    def from_block5(self) -> bool:
        return self.session_id == BLOCK5


@dataclass(frozen=True)
class Pairing:
    gamma: str
    round: int
    alpha: Floor
    beta: Floor
    final: bool

    @property
    def floors(self) -> tuple[Floor, Floor]:
        return (self.alpha, self.beta)

    @property
    def floor_from_block5(self) -> bool:
        return any(f.from_block5 for f in self.floors)

    def as_record(self) -> dict:
        return {"gamma": self.gamma, "round": self.round, "final": self.final,
                **{f.pack: {"session_id": f.session_id, "rule": f.rule} for f in self.floors}}


def _first(entries):
    return min(entries, key=lambda e: (e.round, e.t0, e.session_id))


def floor_for(round_number: int, counting: tuple[SessionEntry, ...], pack: str) -> Floor:
    same = [e for e in counting if e.round == round_number]
    if same:
        return Floor(pack, _first(same).session_id, "same_round")
    later = [e for e in counting if e.round > round_number]
    if later:
        return Floor(pack, _first(later).session_id, "later_round")
    earlier = [e for e in counting if e.round < round_number]
    if earlier:
        latest = max(e.round for e in earlier)
        return Floor(pack, _first([e for e in earlier if e.round == latest]).session_id, "earlier_round")
    return Floor(pack, BLOCK5, "block5")


def pair(census: Census, gamma: SessionEntry) -> Pairing:
    """Pair one GAMMA session.  A non-counting GAMMA session analysed for the
    flagged-inclusive line (§11.4) pairs by the same rule with counting floor
    sessions only (design §18 D17); its own counting never matters (§6.2)."""
    if gamma.pack != "gamma":
        raise ValueError("pairing takes a GAMMA session")
    floors = [floor_for(gamma.round, census.counting(p), p) for p in FLOOR_PACKS]
    return Pairing(gamma.session_id, gamma.round, floors[0], floors[1], final=census.closed)


def pair_all(census: Census, gammas=None) -> tuple[Pairing, ...]:
    chosen = census.counting("gamma") if gammas is None else tuple(gammas)
    return tuple(pair(census, g) for g in chosen)
