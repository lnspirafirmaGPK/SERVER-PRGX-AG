import argparse
import asyncio
from pathlib import Path

from prgx_ag.logging_config import configure_logging
from prgx_ag.orchestrator import PRGXAGNexus


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PRGX-AG Nexus CLI")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--continuous", action="store_true")
    parser.add_argument("--scan-only", action="store_true")
    parser.add_argument("--interval", type=int, default=10)
    return parser


async def _run(args: argparse.Namespace) -> None:
    nexus = PRGXAGNexus(root=Path.cwd())
    if args.scan_only:
        await nexus.prgx1.publish_issue_report()
        return
    if args.continuous:
        await nexus.run_continuous(interval_seconds=args.interval)
        return
    await nexus.run_once()


def main() -> None:
    args = build_parser().parse_args()
    configure_logging()
    asyncio.run(_run(args))


if __name__ == "__main__":
    main()
