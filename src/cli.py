import json
import logging
from pathlib import Path

import typer

from src.core import ZipRepositoryAnalyzer
from src.logger import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

app = typer.Typer(help="📦 ZIP to AI Chat")


@app.command()
def main(zip_path: Path = typer.Argument(..., exists=True, help="Path to ZIP archive")):
    """
    Analyze a repository ZIP archive and save results
    """
    output_dir = Path("out")
    output_dir.mkdir(exist_ok=True)

    # Формируем путь для выходного файла
    output = output_dir / f"{zip_path.stem}_analysis.json"

    try:
        typer.secho(f"🔍 Analyzing archive: {zip_path}", fg=typer.colors.BLUE)
        result = ZipRepositoryAnalyzer(str(zip_path)).analyze()

        typer.secho(f"✅ Results saved to: {output}", fg=typer.colors.GREEN)
        typer.echo(f"\nRepository structure:\n{result['structure_console']}")
        typer.echo(f"\n📊 Analyzed files: {len(result['contents'])}")

        del result['structure_console']

        with open(output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=4, ensure_ascii=False)

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
