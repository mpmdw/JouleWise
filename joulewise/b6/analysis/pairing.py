"""GAMMA's floor pairing by registered round (registration §6.2).

For a GAMMA session of round k and each floor pack P (ALPHA, BETA):

1. P's counting session of round k, if it exists;
2. otherwise P's first counting session of a later round;
3. otherwise P's last counting session of an earlier round, and failing that
   block 5's analysed session of P, labelled "floor from block 5" (S-17).

Pairing reads which sessions count and their rounds, never an energy.  Before
the close (§5.3) a later counting session may still appear, so a pairing made
then is marked provisional.
"""
from __future__ import annotations

from dataclasses import dataclass

from joulewise.b6.analysis.census import Census, SessionEntry

BLOCK5 = "block5"
FLOOR_PACKS = ("alpha", "beta")


@dataclass(frozen=True)
class Floor:
    pack: str
    session_id: str          # a block-6 session id, or BLOCK5
    rule: str                # "same_round", "next_counting", "last_earlier", "floor_from_block_5"

    @property
    def from_block5(self) -> bool:
        return self.session_id == BLOCK5


@dataclass(frozen=True)
class Pairing:
    gamma: str
    round: int
    alpha: Floor
    beta: Floor
    provisional: bool

    @property
    def floors(self) -> tuple[Floor, Floor]:
        return (self.alpha, self.beta)

    @property
    def floor_from_block5(self) -> bool:
        return any(f.from_block5 for f in self.floors)

    def as_record(self) -> dict:
        return {"gamma": self.gamma, "round": self.round, "provisional": self.provisional,
                **{f.pack: {"session_id": f.session_id, "rule": f.rule} for f in self.floors}}


def floor_for(round_number: int, counting: tuple[SessionEntry, ...], pack: str) -> Floor:
    same = [e for e in counting if e.round == round_number]
    if same:
        return Floor(pack, same[0].session_id, "same_round")
    later = sorted((e for e in counting if e.round > round_number), key=lambda e: e.round)
    if later:
        return Floor(pack, later[0].session_id, "next_counting")
    earlier = sorted((e for e in counting if e.round < round_number), key=lambda e: e.round)
    if earlier:
        return Floor(pack, earlier[-1].session_id, "last_earlier")
    return Floor(pack, BLOCK5, "floor_from_block_5")


def pair(census: Census, gamma: SessionEntry) -> Pairing:
    """Pair one GAMMA session.  A non-counting GAMMA session added to the
    flagged-inclusive line (§11.4) is paired by the same rule: pairing never
    depends on the GAMMA session's own counting (§6.2)."""
    if gamma.pack != "gamma":
        raise ValueError("pairing takes a GAMMA session")
    floors = [floor_for(gamma.round, census.counting(p), p) for p in FLOOR_PACKS]
    # Rules 2 and 3 can change while later rounds may still arrive.
    provisional = not census.closed and any(f.rule != "same_round" for f in floors)
    return Pairing(gamma.session_id, gamma.round, floors[0], floors[1], provisional)


def pair_all(census: Census, gammas=None) -> tuple[Pairing, ...]:
    chosen = census.counting("gamma") if gammas is None else tuple(gammas)
    return tuple(pair(census, g) for g in chosen)
