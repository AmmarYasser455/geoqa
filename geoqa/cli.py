"""
CLI interface for GeoQA.

Provides command-line access to geospatial data profiling and quality
assessment via the `geoqa` command.

Author: Ammar Yasser Abdalazim
"""

from __future__ import annotations


import click

from geoqa import __version__


@click.group()
@click.version_option(version=__version__, prog_name="geoqa")
def main():
    """GeoQA: Geospatial Data Quality Assessment & Interactive Profiling.

    Profile geospatial datasets, run quality checks, and generate reports
    from the command line.

    Examples:

        geoqa profile data.shp

        geoqa report data.shp --output report.html

        geoqa check data.geojson
    """
    pass


@main.command()
@click.argument("filepath", type=click.Path(exists=True))
@click.option("--name", "-n", default=None, help="Display name for the dataset.")
def profile(filepath: str, name: str | None):
    """Profile a geospatial dataset and display summary.

    FILEPATH: Path to a vector file (Shapefile, GeoJSON, GeoPackage, etc.)
    """
    from geoqa.core import GeoProfile

    click.echo(f"\n GeoQA — Profiling: {filepath}\n")

    try:
        gp = GeoProfile(filepath, name=name)
        gp.summary(print_output=True)
    except Exception as e:
        click.echo(f" Error: {e}", err=True)
        raise SystemExit(1)


@main.command()
@click.argument("filepath", type=click.Path(exists=True))
@click.option("--output", "-o", default="geoqa_report.html", help="Output HTML file path.")
@click.option("--name", "-n", default=None, help="Display name for the dataset.")
def report(filepath: str, output: str, name: str | None):
    """Generate an HTML quality report for a geospatial dataset.

    FILEPATH: Path to a vector file (Shapefile, GeoJSON, GeoPackage, etc.)
    """
    from geoqa.core import GeoProfile

    click.echo(f"\n GeoQA — Generating report for: {filepath}\n")

    try:
        gp = GeoProfile(filepath, name=name)
        out_path = gp.to_html(output)
        click.echo(f" Report saved to: {out_path}")
    except Exception as e:
        click.echo(f" Error: {e}", err=True)
        raise SystemExit(1)


@main.command()
@click.argument("filepath", type=click.Path(exists=True))
def check(filepath: str):
    """Run quality checks on a geospatial dataset.

    FILEPATH: Path to a vector file (Shapefile, GeoJSON, GeoPackage, etc.)
    """
    from geoqa.core import GeoProfile

    click.echo(f"\n GeoQA — Quality checks for: {filepath}\n")

    try:
        gp = GeoProfile(filepath)
        checks_df = gp.quality_checks()

        for _, row in checks_df.iterrows():
            status_icon = (
                "" if row["Status"] == "PASS" else ("" if row["Status"] == "FAIL" else "")
            )
            click.echo(f"  {status_icon} {row['Check']}: {row['Details']}")

        click.echo(f"\n   Quality Score: {gp.quality_score:.1f}/100\n")
    except Exception as e:
        click.echo(f" Error: {e}", err=True)
        raise SystemExit(1)


@main.command()
@click.argument("filepath", type=click.Path(exists=True))
@click.option("--output", "-o", default=None, help="Save map to HTML file.")
def show(filepath: str, output: str | None):
    """Display an interactive map of a geospatial dataset.

    FILEPATH: Path to a vector file (Shapefile, GeoJSON, GeoPackage, etc.)
    """
    from geoqa.core import GeoProfile

    click.echo(f"\n GeoQA — Mapping: {filepath}\n")

    try:
        gp = GeoProfile(filepath)
        m = gp.show_map()

        if output:
            m.save(output)
            click.echo(f" Map saved to: {output}")
        else:
            # Save to temp and open in browser
            import tempfile
            import webbrowser

            with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
                m.save(f.name)
                webbrowser.open(f"file://{f.name}")
                click.echo("  Map opened in browser.")
    except Exception as e:
        click.echo(f" Error: {e}", err=True)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
