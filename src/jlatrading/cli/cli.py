from typing import Annotated
import typer

from ..common.utils import DateFormat
from ..common.utils import DateUtils as du
from .. import __version__
from ..common.config import AppConfig
from ..core import core


# Initialize the main Typer application
# app = typer.Typer(help="Research Trading Project.")
app = typer.Typer(no_args_is_help=True)


def run():
    core.setup()
    app()


def show_version():
    """Function that prints the version and exits immediately."""
    app_version = __version__
    typer.echo(f"jla-trading v{app_version}")
    raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        help="Show the application version and exit.",
        is_eager=True,
    ),
) -> None:
    if version:
        show_version()
        raise typer.Exit()


@app.command()
def hello():
    print("Hello!! JLA Alg Trad is working")


@app.command()
def daily_bar_history(tickers: Annotated[list[str] | None, typer.Argument(help="Selected tickers.")] = None,
                      start_date: Annotated[str, typer.Option(help="Lower limit operation date from in format '2020-01-20'")] = "",
                      end_date: Annotated[str, typer.Option(help="Upper limit from operation date '2020-01-20'")] = ""):
    """
    Retrieves daily bar information for tickers.
    If no tickers are provided, it using default from env
    """
    valid_tickers: list[str] = []
    if tickers is not None:
        valid_tickers = [ticker.strip() for ticker in tickers if ticker.strip()]
    else:
        valid_tickers = AppConfig.get_typed_value("DEFAULT_TICKERS", []).to_strlist()
        typer.echo("Missing tickers parameter, using default tickers from config: " + ", ".join(valid_tickers))

    if start_date and not du.is_valid_yyyymmdd_str(start_date):
        typer.echo("Invalid start date format. Expected '2026-01-20'.")

    if end_date and not du.is_valid_yyyymmdd_str(end_date):
        typer.echo("Invalid end date format. Expected '2026-01-20'.")

    if start_date == "":
        start_date = du.first_of_curr_month_yyyymmdd_str()
        typer.echo(f"Using 1st of this month as start date since it was not provided: {start_date}")

    if end_date == "":
        end_date = du.now_yyyymmdd_str()
        typer.echo(f"Using today as end date since it was not provided: {end_date}")

    if not du.is_valid_yyyymmdd_str(start_date) or not du.is_valid_yyyymmdd_str(end_date):
        raise typer.BadParameter(f"Invalid start date format. Please provide dates in the format '2026-01-20'.")

    if not du.is_valid_yyyymmdd_str(end_date):
        raise typer.BadParameter(f"Invalid end date format. Please provide dates in the format '2026-01-20'.")

    if not du.is_valid_date_range(start_date, end_date):
        typer.echo("Start date must be less than or equal to end date.")

    typer.echo(f"Getting data for period : {start_date} to {end_date}")

    records = core.download_daily_bar(valid_tickers, start_date=start_date, end_date=end_date)
    typer.echo(f"Downloaded and saved {records} records for tickers: {valid_tickers} from {start_date} to {end_date}")


@app.command()
def instruments_prices():
    records = core.download_instruments_prices()
    typer.echo(f"Downloaded and saved {records} records for instruments prices.")
