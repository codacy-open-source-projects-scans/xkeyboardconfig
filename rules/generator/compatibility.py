# SPDX-License-Identifier: MIT

from __future__ import annotations

import dataclasses
import functools
import re
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Iterable, Self, Sequence

ROOT = Path(__file__).parent.parent.parent
RULES = ROOT / "rules"
SYMBOLS = ROOT / "symbols"
# Some checks in case we move this script
assert RULES.is_dir(), (
    f"Unexpected directory tree, expected '{RULES}/' - did this script move?"
)
assert SYMBOLS.is_dir(), (
    f"Unexpected directory tree, expected '{SYMBOLS}/' - did this script move?"
)


@functools.total_ordering
@dataclass(frozen=True, order=False)
class Layout:
    PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"(?P<layout>[^(:]+)(?:\((?P<variant>[^)]+)\))?(?::(?P<modifier>\d+))?"
    )
    DEFAULT_MODEL: ClassVar[str] = "*"
    DEFAULT_SYMBOLS_PREFIX: ClassVar[str] = "pc"

    layout: str
    variant: str
    modifier: str = ""
    model: str = DEFAULT_MODEL
    symbols_prefix: str = DEFAULT_SYMBOLS_PREFIX

    def __str__(self) -> str:
        modifier = f":{self.modifier}" if self.modifier else ""
        if self.variant:
            return f"{self.layout}({self.variant}){modifier}"
        else:
            return self.layout + modifier

    def __lt__(self, other):
        """
        Custom compare function in order to deal with missing variant.
        """
        if not isinstance(other, self.__class__):
            return NotImplemented
        elif self.model != other.model:
            return self._lt(self.model, other.model)
        elif self.layout != other.layout:
            return self._lt(self.layout, other.layout)
        elif self.variant != other.variant:
            return self._lt(self.variant, other.variant)
        else:
            return False

    @classmethod
    def _lt(cls, a: str, b: str) -> bool:
        if (not a or a == "*") ^ (not b or b == "*"):
            return not b or b == "*"
        elif a.startswith("$") ^ b.startswith("$"):
            return b.startswith("$")
        else:
            return a < b

    @classmethod
    def parse(
        cls,
        raw: str,
        model: str = DEFAULT_MODEL,
        symbols_prefix: str = DEFAULT_SYMBOLS_PREFIX,
    ) -> Self:
        if m := cls.PATTERN.match(raw):
            return cls(
                layout=m.group("layout"),
                variant=m.group("variant") or "",
                modifier=m.group("modifier") or "",
                model=model,
                symbols_prefix=symbols_prefix,
            )
        else:
            raise ValueError(raw)


@dataclass(frozen=True, order=True)
class CompatSymbolsMapping:
    source: Layout
    destination: tuple[Layout, ...]
    _destination_single: tuple[Layout, ...] = ()

    @classmethod
    def parse(cls, raw: str, is_vendor_symbols: bool) -> Self:
        # Drop comment
        raw = raw.split("//")[0]
        parts = raw.split()
        destination_single: tuple[Layout, ...] = ()

        if is_vendor_symbols:
            if not (4 <= len(parts) <= 5):
                raise ValueError(raw)
            source = Layout.parse(parts[2], model=parts[0])
            destination = tuple(
                Layout.parse(p, symbols_prefix=parts[1]) for p in parts[3].split("+")
            )
            if len(parts) > 4:
                destination_single = tuple(
                    Layout.parse(p, symbols_prefix=parts[1])
                    for p in parts[4].split("+")
                )
        elif len(parts) == 2:
            source = Layout.parse(parts[0])
            destination = tuple(map(Layout.parse, parts[1].split("+")))
        else:
            raise ValueError(raw)

        return cls(
            source=source,
            destination=destination,
            _destination_single=destination_single,
        )

    @classmethod
    def parse_iter(
        cls, lines: Iterable[str], is_vendor_symbols: bool
    ) -> Iterable[Self]:
        for line in lines:
            line, *_ = line.split("//")
            line = line.strip()
            if not line:
                continue
            yield cls.parse(line, is_vendor_symbols)

    @classmethod
    def parse_array(cls, raw: str, is_vendor_symbols: bool) -> Iterable[Self]:
        lines = textwrap.dedent(raw).splitlines()
        yield from cls.parse_iter(lines, is_vendor_symbols=is_vendor_symbols)

    @property
    def destination_single(self) -> tuple[Layout, ...]:
        return self._destination_single or self.destination

    def join(self, destination: tuple[Layout, ...], modifier: str = "", sep: str = "+"):
        return sep.join(
            str(dataclasses.replace(d, modifier=modifier) if modifier else d)
            for d in destination
        )


@dataclass(frozen=True)
class CompatMappings:
    migrations: Sequence[CompatSymbolsMapping]
    vendors: Sequence[CompatSymbolsMapping]

    @classmethod
    def load(
        cls,
        migrations_path: Path | None = None,
        vendors_path: Path | None = None,
        skip_if_source_file_exists: bool = True,
    ) -> Self:
        def check_symbols(layout: Layout, skip_if_source_file_exists: bool) -> bool:
            return skip_if_source_file_exists == (
                not (SYMBOLS / layout.source.layout).is_file()
            )

        if migrations_path:
            with migrations_path.open("rt", encoding="utf-8") as fd:
                migrations = sorted(
                    filter(
                        functools.partial(
                            check_symbols,
                            skip_if_source_file_exists=skip_if_source_file_exists,
                        ),
                        CompatSymbolsMapping.parse_iter(fd, is_vendor_symbols=False),
                    )
                )
        else:
            migrations = []

        if vendors_path:
            with vendors_path.open("rt", encoding="utf-8") as fd:
                vendors = sorted(
                    CompatSymbolsMapping.parse_iter(fd, is_vendor_symbols=True)
                )
        else:
            vendors = []

        return cls(migrations=migrations, vendors=vendors)
