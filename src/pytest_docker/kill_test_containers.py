import json
import subprocess
from typing import Optional

import scripts
POSTGRES_PORT = ...

def kill_test_container() -> bool:
    test_container = get_test_container()
    if not test_container:
        return False
    ok, exitcode = scripts.os_system(f"docker kill {test_container}")
    return ok

def get_test_container() -> Optional[str]:
    containers = docker_containers()
    for container_name, container_info in containers.items():
        if str(POSTGRES_PORT) in container_info["ports"]:
            return container_name
    return None
  
def docker_containers() -> dict[str, dict]:
    container_info_lines = subprocess.getoutput("docker container ls -a").splitlines()[1:]
    containers: dict[str, dict] = {}
    for line in container_info_lines:
        container_id, image, command, *_, ports, name = line.split()
        containers[name] = {"id": container_id, "image": image, "command": command, "ports": ports}
    return containers


def is_container_running(container: str) -> bool:
    return json.loads(subprocess.getoutput(f"docker container inspect {container}"))[0]["State"]["Running"]


# ---[ Pytest Hooks ]---

def pytest_sessionfinish(session, exitstatus):
    tests_succeeded: bool = exitstatus == 0

    docker_kill = session.config.getoption('--docker-kill')
    should_docker_kill = (
        docker_kill == "always"
        or (docker_kill == "on-success" and tests_succeeded)
        or (docker_kill == "on-failure" and not tests_succeeded)
    )
    if should_docker_kill:
        kill_test_container()

def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        '--docker-kill',
        choices=["always", "never", "on-failure", "on-success"],
        default="never",
    )

