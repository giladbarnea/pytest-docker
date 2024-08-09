from pathlib import Path

import click
import dotenv

from scripts import util

DEFAUALT_DOCKER_COMPOSE_PATH = "docker-compose.yaml"
DEFAUALT_DOTENV_FILE = "app/.env"
default_click_context_settings = dict(
    show_default=True,
    help_option_names=["-h", "--help"],
    allow_extra_args=True,
    ignore_unknown_options=True,
    terminal_width=150,
)

def os_system(command, verbosity=0):
    exit_code = subprocess.call(
        command,
        shell=True,
        env=os.environ,
    )
    ok = exit_code == 0
    return ok, exit_code
  
def main(
    docker_compose_path=DEFAUALT_DOCKER_COMPOSE_PATH,
    docker_profile: str = None,
    env_file=DEFAUALT_DOTENV_FILE,
    verbosity: int = 0,
    *extra_docker_compose_up_options,
) -> tuple:
    dotenv.load_dotenv(env_file, verbose=True, override=True)
    docker_compose_options = f"docker-compose --env-file={env_file} -f {docker_compose_path} "
    if docker_profile and "profiles:" in Path(docker_compose_path).read_text():
        docker_compose_options += f"--profile {docker_profile} "
    docker_compose_up_options = f"-d --remove-orphans "
    for docker_compose_up_option in extra_docker_compose_up_options:
        docker_compose_up_options += f"{docker_compose_up_option} "
    command = docker_compose_options + "up " + docker_compose_up_options
    ok, exitcode = os_system(command, verbosity=verbosity)
    if not ok:
        return ok, exitcode
    return os_system("docker ps -a", verbosity=verbosity)


@click.command(context_settings=default_click_context_settings)
@click.argument("docker_compose_path", type=click.Path(exists=True), default=DEFAUALT_DOCKER_COMPOSE_PATH)
@click.option(
    "-d",
    "--profile",
    "docker_profile",
    metavar="DOCKER_PROFILE",
    default="full",
)
@click.option("-e", "--env-file", type=click.Path(exists=True), default=DEFAUALT_DOTENV_FILE)
@click.option("-v", "--verbosity", type=click.Choice(range(3)), count=True)
@click.argument("docker_compose_up_options", nargs=-1, type=click.UNPROCESSED)
def main_cli(
    docker_compose_path,
    docker_profile: str,
    env_file,
    verbosity: int,
    docker_compose_up_options: tuple,
):
    return main(
        docker_compose_path,
        docker_profile,
        env_file,
        verbosity,
        *docker_compose_up_options,
    )


if __name__ == "__main__":
    main_cli()
