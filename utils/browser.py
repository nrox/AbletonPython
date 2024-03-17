import inspect


class Browser:

    def __init__(self, client):
        self.client = client


def parse_items(items_str):
    """Parse items_str=result[0] in get_folder code."""
    items = eval(items_str)

    def concatenate(aggregated: list, rest):
        if isinstance(rest, tuple):
            if len(rest) == 2:
                return aggregated + [rest[1]]
            if len(rest) == 3:
                return concatenate(aggregated + [rest[1]], rest[2])
        if isinstance(rest, list):
            return [concatenate(aggregated, r) for r in rest]
        raise ValueError("Unexpected state aggregated = %s; rest = %s" % (aggregated, rest))

    return concatenate([], *items)[0][0]


def get_folder(Live, result, group, *folders):
    # Runs with exec or eval in Live.

    def get_children(dev):
        if not dev:
            return []
        if hasattr(dev, 'iter_children'):
            return [c for c in enumerate(dev.iter_children)]
        if hasattr(dev, 'children'):
            return [c for c in enumerate(dev.children)]

    def get_tree(dev, *paths):
        children = get_children(dev)
        if paths:
            return [(i, c.name, get_tree(c, *paths[1:])) for i, c in children if c.name == paths[0]]
        return [(i, c.name) for i, c in children]

    browser = Live.Application.get_application().browser
    device = getattr(browser, group)
    tree = get_tree(device, *folders)
    result.append(tree)


def get_preview(Live, result, group, *folders):
    def get_children(dev):
        if not dev:
            return []
        if hasattr(dev, 'iter_children'):
            return [c for c in enumerate(dev.iter_children)]
        if hasattr(dev, 'children'):
            return [c for c in enumerate(dev.children)]

    def get_item(dev, *paths):
        if not paths:
            return dev
        children = get_children(dev)
        return [get_item(c, *paths[1:]) for i, c in children if c.name == paths[0]][0]

    browser = Live.Application.get_application().browser
    device = getattr(browser, group)
    item = get_item(device, *folders)
    result.append(item.name)
    browser = Live.Application.get_application().browser
    browser.stop_preview()
    browser.preview_item(item)


def preview(cli, instrument_path: list[str]):
    code = inspect.getsource(get_preview)
    folders = [f"'{i}'" for i in instrument_path]
    code = code + "\n" + f"get_preview(Live, result, 'instruments', {','.join(folders)})"
    return cli.query("/live/exec", (code,), timeout=2)
