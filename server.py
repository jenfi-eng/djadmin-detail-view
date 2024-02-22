import uvicorn
from uvicorn.supervisors import ChangeReload

if __name__ == "__main__":
    # Way more complex due to reload hanging waiting on connections
    # https://github.com/encode/uvicorn/issues/675#issue-619136127
    config = uvicorn.Config(
        "example_project.asgi:application",
        reload=True,
        reload_dirs=["djadmin_detail_view", "example_project"],
        reload_includes=["*.html", "*.md"],
        reload_excludes="test_*.py",
        ssl_keyfile="./docker/support/lvh-key.pem",
        ssl_certfile="./docker/support/lvh-cert.pem",
    )
    server = uvicorn.Server(config)
    server.force_exit = True

    sock = config.bind_socket()
    supervisor = ChangeReload(config, target=server.run, sockets=[sock])
    supervisor.run()
