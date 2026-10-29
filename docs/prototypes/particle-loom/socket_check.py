# Does a three-rule "socket" model reproduce the SM tree-level vertex list (Romao & Silva) exactly?
from itertools import combinations_with_replacement as cwr
# sockets: Q electric charge, C color, I weak (left-handed doublet), M mass (Higgs coupling)
FERM = {"u": "QCIM", "d": "QCIM", "l": "QIM", "n": "I"}          # up-type, down-type, charged lepton, neutrino
BOS = {"g": "C", "A": "", "W": "QIM", "Z": "M", "H": "M"}        # A = photon
KEY = {"A": "Q", "g": "C", "W": "I", "Z": "I", "H": "M"}
GAUGE = {"A", "g", "W", "Z"}
PARTNER = {"u": "d", "d": "u", "l": "n", "n": "l"}
Qcharge = {"A": 0, "g": 0, "Z": 0, "H": 0}                       # W pair is W+ W-; single W keys carry charge
derived = set()
# Rule 1: a key latches only its matching socket. Rule 2: fermion lines take exactly one key;
# a boson pair takes one or two keys, two only if both gauge or both Higgs. Rule 3: charge is conserved
# (a single W key changes a fermion line to its partner; a W pair with one W key is forbidden).
for f, s in FERM.items():
    for k, sock in KEY.items():
        if sock in s:
            if k == "W": derived.add(tuple(sorted([f, PARTNER[f], "W"])))
            else: derived.add(tuple(sorted([f, f, k])))
for b, s in BOS.items():
    for n in (1, 2):
        for ks in cwr(KEY, n):
            if not all(KEY[k] in s for k in ks): continue
            if n == 2 and not (all(k in GAUGE for k in ks) or all(k == "H" for k in ks)): continue
            if b != "W" and "W" in ks: continue                 # W key on a neutral pair would carry net charge
            if b == "W" and ks.count("W") % 2: continue          # W+ W- pair plus an odd number of W keys: charge not conserved
            derived.add(tuple(sorted([b, b, *ks])))
ferm_expected = {tuple(sorted(v)) for v in [
  ("u","u","A"),("d","d","A"),("l","l","A"),("u","u","g"),("d","d","g"),
  ("u","d","W"),("l","n","W"),("u","u","Z"),("d","d","Z"),("l","l","Z"),("n","n","Z"),
  ("u","u","H"),("d","d","H"),("l","l","H")]}
bos_expected = {tuple(sorted(v)) for v in [
  ("g","g","g"),("g","g","g","g"),("W","W","A"),("W","W","Z"),("W","W","A","A"),("W","W","Z","Z"),("W","W","Z","A"),
  ("W","W","W","W"),("H","W","W"),("H","Z","Z"),("H","H","W","W"),("H","H","Z","Z"),("H","H","H"),("H","H","H","H")]}
exp = ferm_expected | bos_expected
print("derived but not in SM:", sorted(derived - exp))
print("in SM but not derived:", sorted(exp - derived))
print("count derived", len(derived), "expected", len(exp))
