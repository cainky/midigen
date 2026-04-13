# Midigen Architecture Refactor

## Goal

Restructure midigen into explicit architectural layers with clean dependency boundaries, reduce implementation duplication via data-driven patterns, eliminate circular imports, and make the codebase trivially navigable — every file has real code, no shims, no ghosts.

## Current State

- 6,055 lines of source across 14 files + 1 subdirectory in a flat `midigen/` package
- `Chord` class: 44 methods (22 are copy-paste factory methods with identical structure)
- Circular import between `Song` ↔ `MidiCompiler` (late import hack at EOF)
- `MidiCompiler`: 9 direct dependencies (orchestration hub)
- Inconsistent factory patterns (free functions vs classmethods vs static methods)
- `Section`: no validation, fails deep in compilation with confusing errors
- No explicit layer boundaries — all modules at same package level
- `Track`: 22 methods — fine, but imports composition types it only needs for type hints
- `song_example.py` uses deprecated API (`song.generate()`)
- Tests ship in PyPI wheel (pre-existing, note for later)

## Target Architecture

```
midigen/
├── theory/              # Zero internal deps. Pure music logic.
│   ├── __init__.py      # Exports: Note, Key, KEY_MAP, VALID_KEYS, Scale, TimeConverter, roman helpers
│   ├── note.py          # Note class
│   ├── key.py           # Key class + KEY_MAP + VALID_KEYS
│   ├── scale.py         # Scale class (@staticmethod — stays unchanged)
│   ├── roman.py         # Roman numeral parsing (parse_roman_numeral, get_chord_pitches, etc.)
│   └── time_utils.py    # TimeConverter (pure math, no external imports)
│
├── composition/         # Depends ONLY on theory/
│   ├── __init__.py      # Exports: Chord, CHORD_TYPES, ChordProgression, Arpeggio, ArpeggioPattern, Melody, DrumKit, Drum, GM1_DRUM_MAP, Section
│   ├── chord.py         # Chord class (container + voicings + data-driven factories)
│   ├── progression.py   # ChordProgression (roman numeral → chord sequence)
│   ├── arpeggio.py      # Arpeggio + ArpeggioPattern
│   ├── melody.py        # Melody generation
│   ├── drums.py         # DrumKit, Drum, GM1_DRUM_MAP
│   └── section.py       # Section with validation
│
├── protocol/            # Depends on theory/ at runtime, TYPE_CHECKING only for composition/
│   ├── __init__.py      # Exports: Track, MAX_MIDI_TICKS, ChannelPool, ChannelExhaustedError, INSTRUMENT_MAP
│   ├── track.py         # Track (note collection + MIDI compilation, single class)
│   ├── channel_pool.py  # ChannelPool, ChannelExhaustedError
│   └── instruments.py   # INSTRUMENT_MAP
│
├── api/                 # Depends on all layers
│   ├── __init__.py      # Exports: Song, MidiGen, MidiCompiler
│   ├── song.py          # Song (pure data container)
│   ├── midigen.py       # MidiGen (low-level MidiFile wrapper)
│   └── compiler.py      # MidiCompiler (orchestration)
│
├── tests/               # Test suite (stays in place)
│   ├── __init__.py
│   └── test_*.py        # All imports updated to new paths
│
└── __init__.py          # Public API re-exports (the ONLY backwards-compat layer)
```

**No shim files.** The old `midigen/chord.py`, `midigen/track.py`, etc. are GONE — moved to their new locations via `git mv`. The only backwards-compat mechanism is the top-level `__init__.py` which re-exports all public names.

## Dependency Rules

1. `theory/` imports NOTHING from midigen
2. `composition/` imports ONLY from `theory/`
3. `protocol/` imports from `theory/` at runtime. Uses `from __future__ import annotations` + `TYPE_CHECKING` for composition/ type annotations only.
4. `api/` imports from all three layers freely
5. NO circular imports — compiler.py imports Song at top level (no late-import hack)
6. Top-level `__init__.py` re-exports the full public API

## Key Design Decisions

### Decision 1: No Shim Files

Shim files (re-export stubs at old locations) create:
- 14 extra files cluttering the package root
- Developer confusion (opening `midigen/chord.py` and finding a 3-line redirect)
- A maintenance trap (3 places to update for each new export)
- The illusion of backwards compat while actually making navigation worse

Instead: the top-level `__init__.py` is the single public API surface. `from midigen import Chord` works. `from midigen.chord import Chord` does NOT work (old path deleted). All internal imports (tests, source, examples) are updated to canonical paths.

This means: any external user doing `from midigen.chord import Chord` needs to change to `from midigen import Chord`. One-line fix. Justified at version 1.0.0.

### Decision 2: Don't Split Track

Track has 22 methods serving one concept. The `compile()` method is 40 lines. Not worth splitting.

**What we fix:** Add `from __future__ import annotations` and move Chord/ChordProgression/Arpeggio/DrumKit behind `if TYPE_CHECKING:`. Track's convenience methods duck-type (call `.get_chord()`, `.get_progression()`, etc.) — they don't need these types at runtime.

Note: `Key` stays as a runtime import because `set_key_signature()` does `isinstance(key, Key)`.

### Decision 3: Data-Driven Chord Factories

Add a `CHORD_TYPES` dict mapping string names to interval tuples:
```python
CHORD_TYPES = {
    "major_triad": (0, 4, 7),
    "minor_triad": (0, 3, 7),
    "sus2": (0, 2, 7),
    "sus4": (0, 5, 7),
    "augmented": (0, 4, 8),
    "diminished": (0, 3, 6),
    "dominant_seventh": (0, 4, 7, 10),
    "major_seventh": (0, 4, 7, 11),
    "minor_seventh": (0, 3, 7, 10),
    # ... all 22 types
}
```

Add `Chord.build(chord_type: str, root: Note) -> Chord` classmethod.
Keep ALL 22 `create_*` classmethods as one-line wrappers: `return cls.build("sus2", root)`.

**Why keep the wrappers:** Zero API breakage. External code calling `Chord.create_sus2(root)` still works. Tests don't change. But internally, adding a new chord type is now one dict entry.

**Why add build():** Programmatic access. Users can list available types via `CHORD_TYPES.keys()`, build chords dynamically, and register custom types in the future.

### Decision 4: Extract ChordProgression and Arpeggio

These are genuinely separate concerns from Chord:
- ChordProgression: parses roman numerals, manages chord sequences, handles timing
- Arpeggio: extends Chord with sequential playback patterns and looping

Extracting them gives each its own file with a single clear purpose.

### Decision 5: Song Decoupling

Remove from Song: `_get_compiler()`, `_compiler`, `generate()`, `save()`, `midigen` property, `available_channels` property. Song becomes a 40-line data container.

MidiCompiler imports Song at the top of the file (no circular dependency since Song doesn't reference MidiCompiler). The late-import hack at EOF of midi_compiler.py is deleted.

### Decision 6: Section Validation

Section.__init__ validates the chord progression string:
- Non-empty
- Split on '-', each token passed to `parse_roman_numeral()`
- Raises ValueError with clear message on first invalid token

### Decision 7: Feature Branch

All work on `refactor/architecture-layers`. Merge via PR after full verification.

### Decision 8: Scale Stays Unchanged

Scale uses `@staticmethod`. It's never instantiated, never subclassed. No reason to change to `@classmethod`. Don't standardize for standardization's sake.

## Import Updates Required

53 submodule imports across 19 files need updating. Examples:

| Old Path | New Path |
|---|---|
| `from midigen.note import Note` | `from midigen.theory.note import Note` |
| `from midigen.chord import Chord, ChordProgression` | `from midigen.composition.chord import Chord` + `from midigen.composition.progression import ChordProgression` |
| `from midigen.track import Track, MAX_MIDI_TICKS` | `from midigen.protocol.track import Track, MAX_MIDI_TICKS` |
| `from midigen.midigen import MidiGen` | `from midigen.api.midigen import MidiGen` |
| `from midigen.compiler import MidiCompiler` | `from midigen.api.compiler import MidiCompiler` |
| `from midigen.drums import DrumKit, Drum, GM1_DRUM_MAP` | `from midigen.composition.drums import DrumKit, Drum, GM1_DRUM_MAP` |
| `from midigen.key import Key, KEY_MAP, VALID_KEYS` | `from midigen.theory.key import Key, KEY_MAP, VALID_KEYS` |
| `from midigen.channel_pool import ChannelPool` | `from midigen.protocol.channel_pool import ChannelPool` |
| `from midigen.instruments import INSTRUMENT_MAP` | `from midigen.protocol.instruments import INSTRUMENT_MAP` |
| `from midigen.time_utils import TimeConverter` | `from midigen.theory.time_utils import TimeConverter` |
| `from midigen.roman import parse_roman_numeral, ...` | `from midigen.theory.roman import parse_roman_numeral, ...` |
| `from midigen.scale import Scale` | `from midigen.theory.scale import Scale` |

Tests that use `from midigen import X` (via __init__.py) don't need changes.

## Tests That Change

**Deleted tests** (test deprecated API that's being removed):
- `test_song.py::TestLegacyAPI` (3 tests: test_legacy_generate, test_legacy_available_channels, test_deprecation_warning_on_generate)

**Modified tests:**
- `test_golden_master.py::test_song_progression_i_v_vi_iv`: rewrite from `song.generate()` → MidiCompiler, verify MIDI output is byte-identical
- `test_integration.py`: remove 5 calls to deprecated `track.add_note_off_messages()`
- All test files: update submodule import paths (mechanical find-replace)

**New tests:**
- Section validation: empty string, malformed tokens, double dashes, trailing dashes
- `Chord.build()`: verify all CHORD_TYPES produce correct intervals, invalid type name raises KeyError

## Non-Test Files That Change

- `example.py`: update imports to `from midigen import MidiGen, Note, Chord, Key, KEY_MAP`
- `song_example.py`: rewrite to use MidiCompiler instead of deprecated song.generate()/save()
- `README.md`: update all code examples to current API

## Execution Order

0. Create feature branch `refactor/architecture-layers`
1. Create package skeleton (theory/, composition/, protocol/, api/ with __init__.py)
2. Move theory layer (git mv note, key, scale, roman, time_utils → theory/) + update internal imports + update __init__.py → tests WILL break (imports wrong), fix test imports → tests pass
3. Refactor Chord: add CHORD_TYPES dict + build() method + convert create_* to wrappers. Extract ChordProgression → composition/progression.py. Extract Arpeggio → composition/arpeggio.py. Move chord.py → composition/. Update imports everywhere. → tests pass
4. Move melody, drums, section → composition/. Add Section validation. Update imports. Add new Section validation tests. → tests pass
5. Move track, channel_pool, instruments → protocol/. Add `from __future__ import annotations` + TYPE_CHECKING to track.py. Update imports. → tests pass
6. Decouple Song + move song, midigen, compiler → api/. Remove deprecated Song methods. Delete TestLegacyAPI tests. Rewrite golden master test. Update imports. → tests pass
7. Remove Track.add_note_off_messages() + remove calls in test_integration.py → tests pass, zero DeprecationWarnings
8. Update example.py, song_example.py, README.md
9. Final verification (layer isolation, golden masters, all public imports)
10. PR to main

## Success Criteria

1. All tests pass (some deleted, some modified, some added)
2. No circular imports (import each subpackage in isolation)
3. Layer isolation verified: `python -c "from midigen.theory.note import Note"` doesn't pull in composition/protocol/api
4. `Chord.build()` exists and CHORD_TYPES is a public dict
5. `Section("x", 1, "garbage")` raises ValueError
6. `grep -r "MidiCompiler\|_compiler\|generate\|\.save" midigen/api/song.py` returns nothing
7. Golden master MIDI output is byte-identical after test rewrite
8. `from midigen import Chord, Song, MidiCompiler, Track, Note, Key, ...` works (full public API via __init__)
9. Zero DeprecationWarnings in pytest output
10. example.py and song_example.py use current API and run successfully
11. README shows current, non-deprecated usage

## What This Plan Does NOT Do

- Split Track (compile() is 40 lines, not a class)
- Reorganize test directory (cosmetic, risky)
- Change Scale's @staticmethod pattern (no reason)
- Delete any public API method (all create_* stay as wrappers)
- Add Protocol types or builder patterns (future)
- Add comprehensive error messages (future)
- Fix tests-in-wheel issue (note for separate PR)
- Create shim/redirect files (they're worse than the problem they solve)

## Known Risks

1. **`from midigen.chord import Chord` breaks for external users.** Mitigated: top-level `from midigen import Chord` is the documented API. Anyone using submodule paths fixes with one-line change. This is 1.0.0 — submodule layout is an implementation detail.
2. **Step 6 is highest risk**: removing Song deprecated methods + rewriting golden master test. Must verify MIDI binary is identical before/after.
3. **`from __future__ import annotations` in track.py**: Makes all annotations strings. Fine because Track never does isinstance checks against Chord/ChordProgression — only against Note and Key (both runtime-imported from theory/).
4. **Section validation could reject currently-working input**: If any existing test or example passes a string that `parse_roman_numeral()` can't handle, the validation will break it. Must verify all existing Section usages parse cleanly.
5. **CHORD_TYPES interval overlap with roman.py CHORD_INTERVALS**: Different dicts for different purposes. roman.py maps ChordQuality enums → intervals (for parsing). CHORD_TYPES maps string names → intervals (for construction). Not worth unifying — different keys, different consumers.
