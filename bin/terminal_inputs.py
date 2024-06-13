import argparse


def terminal_inputs():
    """Parse the terminal inputs and return the arguments"""

    parser = argparse.ArgumentParser(
        prog="whoami",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Who Am I, is a tool for checking network health check and stresses test",
    )

    # Standard arguments

    parser.add_argument(
        "-l",
        "--log-level",
        type=int,
        default=30,
        help="Log level 10=DEBUG, 20=INFO, 30=WARN, 40=ERROR, 50=CRITICAL 0=NOTSET",
    )
    parser.add_argument(
        "--connect",
        action="append",
        type=str,
        help="Endpoints to connect to, in case multicast is not working. ex. tcp/localhost:7447",
    )
    parser.add_argument(
        "-r",
        "--realm",
        default="rise",
        type=str,
        help="Unique id for a domain/realm ex. rise",
    )
    parser.add_argument(
        "-e",
        "--entity-id",
        required=True,
        type=str,
        help="Entity being a unique id representing an entity within the realm ex, boatswain",
    )

    # Add arguments for the specific processor


    ## Parse arguments and start doing our thing
    args = parser.parse_args()

    return args
