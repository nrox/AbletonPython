from . import client  # type: ignore


def test_post_eval(client):
    rv = client.query("/live/eval", ("Live.Application.get_application()",), timeout=1)
    assert "get_major_version" in str(rv)
    for i in rv:
        print(i)


def test_post_execl(client):
    rv = client.query("/live/exec", ("result.append(Live.Application.get_application())",), timeout=1)
    assert "Application" in str(rv)
    for i in rv:
        print(i)
