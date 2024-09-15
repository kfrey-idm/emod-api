#! /usr/bin/env python3
from io import BytesIO
from urllib.error import URLError
import sys
import numpy as np
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def run(input_file: Path, parameters: dict) -> None:
    """
    Run a client that tries to connect the url given in parameters. The client will do a Post operation with
    the parameters given in parameters.

    Args:
        input_file: Path to the demographics file.
        parameters: Dictionary containing the server url and the parameters for model calculation.

    """

    with input_file.open("r") as file:
        contents = file.read()
        jason = contents.encode("utf-8")    # we will need a bytes object rather than string

    # rate = k*(m1^a)*(m2^b)/(d^c) => p0 = k, p1 = a, p2 = b, p3 = -c
    url = parameters['url'] + f"?{urlencode(parameters['params'])}"
    print("Trying to connect to webservice: ", url)

    headers = {"Content-Type": "application/json"}
    request = Request(url=url, headers=headers, data=jason, method="POST")

    try:
        with urlopen(request) as source:
            rates = np.load(BytesIO(source.read()))
    except URLError as e:
        # this exception is triggered by
        # (a) not being connected to the (IDM) network
        # (b) by a non-existing url
        # (c) server not running
        print(e.reason)
        sys.exit(1)

    return rates

