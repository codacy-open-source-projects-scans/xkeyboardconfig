xkeyboard-config [2.42](https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/tree/xkeyboard-config-2.42) - 2024-06-07
===================================================================================================================================

## Models

### Breaking

- Removed the old Macs
- Removed the MacBook 78/79
- Removed the Intel Classmate
- Removed a few old Nokia devices


## Layouts

### Breaking change

- `dz`: Renamed `la` to `azerty-oss`.
- `br`: Removed the default `Scroll_Lock` mapping.

### New

- `ara(mac-phonetic)`: use new dead key `dead_hamza`.
- `dz`: Added `kab` to the language list.
- `fr`: Added Ergo‑L layout and variant (`ergol`, `ergol_iso`).
- `gr`: Added missing characters from `cp1253` and `varEpsilon`.
- `hu`: Added Old Hungarian layouts for users in SK
- symbols: Added grab and srvrkeys with a single section
- `ru`: Updated Rulemak to latest version.
- `ru(ruu)`: Added `Ukrainian_i` as `Cyrillic_i` alternative to the
   3rd level of `<AB05>`.
- `ua`: Enabled typing “g” with `AltGr`.

### Fixes

- `fr(oss)`: Updated behaviour of space key to match doc.
  [#439](https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/issues/439)
- `fr(bepo_afnor)`: Removed unnecessary include.
  [#448](https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/issues/448)


## Options

## New

- Added `eurosign:E`.
  [#444](https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/issues/444)
- Added `caps:digits_row` for Azerty layouts.
- Added `scrolllock:mod3`.


Older versions
==============

Unfortunately there is no detailed changelog for recent versions. Please see
[`ChangeLog.old`](ChangeLog.old) for versions up to `1.8` (2010) or use the
[git log](https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/commits/master).
