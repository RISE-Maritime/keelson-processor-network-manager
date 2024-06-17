import zenoh
import logging
import warnings
import atexit
import json
import time
import keelson
from terminal_inputs import terminal_inputs
from keelson.payloads.NetworkPing_pb2 import NetworkPing, NetworkResults

session = None
args = None


def query_ping(query):
    """
    Query for testing the network connection

    - Loop time of the message should be measured

    Args:
        query (zenoh.Query): Zenoh query object
    Returns:
        envelope (bytes) with compressed payload
    """

    query_key = query.selector
    logging.debug(f">> [Query Ping] Received key: {query_key}")

    query_payload = query.value
    logging.debug(f">> [Query Ping] Received payload: {query_payload}")

    query.reply(
        zenoh.Sample(str(query.selector), query_payload)
    )  # Send the reply on same key as the query


def query_ping_upload_and_download(query):
    """
    Query for testing the network connection

      -  Loping the message payload back to sender with timestamp

    Args:
        query (zenoh.Query): Zenoh query object
    Returns:
        envelope (bytes) with compressed payload
    """

    ingress_timestamp = time.time_ns()

    query_key = query.selector
    logging.debug(f">> [Query] Received query key {query_key}")

    query_payload = query.value.payload
    # logging.debug(f">> [Query] Received query payload {query_payload}")

    received_at, enclosed_at, content = keelson.uncover(query_payload)
    message_received = NetworkPing.FromString(content)

    # logging.debug(message_received.timestamp_sender)

    # Re-Packing with new timestamp and ping count
    payload = NetworkPing()
    payload.timestamp_sender.FromNanoseconds(
        message_received.timestamp_sender.ToNanoseconds()
    )
    payload.timestamp_receiver.FromNanoseconds(ingress_timestamp)
    payload.id_sender = message_received.id_sender
    payload.id_receiver = args.entity_id
    payload.ping_count = message_received.ping_count + 1
    payload.payload_description = message_received.payload_description
    payload.payload_size_mb = message_received.payload_size_mb
    payload.payload_size_bytes = message_received.payload_size_bytes
    payload.dummy_payload = message_received.dummy_payload
    serialized_payload = payload.SerializeToString()
    envelope = keelson.enclose(serialized_payload)

    query.reply(
        zenoh.Sample(str(query.selector), envelope)
    )  # Send the reply on same key as the query


def query_ping_upload(query):
    """
    Query for testing the network connection

      -  Message payload upload to the responder returning empty message

    Args:
        query (zenoh.Query): Zenoh query object
    Returns:
        envelope (bytes) with compressed payload
    """

    ingress_timestamp = time.time_ns()

    query_key = query.selector
    logging.debug(f">> [Query] Received query key {query_key}")

    query_payload = query.value.payload
    # logging.debug(f">> [Query] Received query payload {query_payload}")

    received_at, enclosed_at, content = keelson.uncover(query_payload)
    message_received = NetworkPing.FromString(content)

    # logging.debug(message_received.timestamp_sender)

    # Re-Packing with new timestamp and ping count
    payload = NetworkPing()
    payload.timestamp_sender.FromNanoseconds(
        message_received.timestamp_sender.ToNanoseconds()
    )
    payload.timestamp_receiver.FromNanoseconds(ingress_timestamp)
    payload.id_sender = message_received.id_sender
    payload.id_receiver = args.entity_id
    payload.ping_count = message_received.ping_count + 1
    payload.payload_description = message_received.payload_description
    payload.payload_size_mb = message_received.payload_size_mb
    payload.payload_size_bytes = message_received.payload_size_bytes
    serialized_payload = payload.SerializeToString()
    envelope = keelson.enclose(serialized_payload)

    query.reply(
        zenoh.Sample(str(query.selector), envelope)
    )  # Send the reply on same key as the query


def query_ping_download(query):
    """
    Query for testing the network connection

      -  Message payload download to responder incoming message is empty

    Args:
        query (zenoh.Query): Zenoh query object
    Returns:
        envelope (bytes) with compressed payload
    """

    ingress_timestamp = time.time_ns()

    query_key = query.selector
    logging.debug(f">> [Query] Received query key {query_key}")

    query_payload = query.value.payload
    # logging.debug(f">> [Query] Received query payload {query_payload}")

    received_at, enclosed_at, content = keelson.uncover(query_payload)
    message_received = NetworkPing.FromString(content)

    size_in_bytes = message_received.payload_size_mb * 1024 * 1024
    dummy_payload = bytes(bytearray(int(size_in_bytes)))

    payload = NetworkPing()
    payload.timestamp_sender.FromNanoseconds(
        message_received.timestamp_sender.ToNanoseconds()
    )
    payload.timestamp_receiver.FromNanoseconds(ingress_timestamp)
    payload.id_sender = message_received.id_sender
    payload.id_receiver = args.entity_id
    payload.ping_count = message_received.ping_count
    payload.payload_description = message_received.payload_description
    payload.payload_size_mb = message_received.payload_size_mb
    payload.payload_size_bytes = message_received.payload_size_mb * 1024 * 1024
    payload.dummy_payload = dummy_payload
    serialized_payload = payload.SerializeToString()
    envelope = keelson.enclose(serialized_payload)

    query.reply(
        zenoh.Sample(str(query.selector), envelope)
    )  # Send the reply on same key as the query


if __name__ == "__main__":
    # Input arguments and configurations
    args = terminal_inputs()
    # Setup logger
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s %(message)s", level=args.log_level
    )
    logging.captureWarnings(True)
    warnings.filterwarnings("once")

    ## Construct session
    logging.info("Opening Zenoh session...")
    conf = zenoh.Config()
    if args.mode is not None:
        conf.insert_json5(zenoh.config.MODE_KEY, json.dumps(args.mode))
    if args.connect is not None:
        conf.insert_json5(zenoh.config.CONNECT_KEY, json.dumps(args.connect))
    session = zenoh.open(conf)

    def _on_exit():
        session.close()

    atexit.register(_on_exit)
    logging.info(f"Zenoh session established: {session.info()}")

    #################################################
    # Setting up QUERYABLE´s

    # Ping test queryable (empty payload)
    key_exp_query_ping = keelson.construct_req_rep_key(
        realm=args.realm,
        entity_id=args.entity_id,
        responder_id="network",
        procedure="ping",
    )
    query_network_ping = session.declare_queryable(key_exp_query_ping, query_ping)
    logging.info(f"Created queryable: {key_exp_query_ping}")

    # Ping test UP and DOWN load queryable
    key_exp_query_ping_up_down = keelson.construct_req_rep_key(
        realm=args.realm,
        entity_id=args.entity_id,
        responder_id="network",
        procedure="ping_up_down",
    )
    query_network_ping_up_down = session.declare_queryable(
        key_exp_query_ping_up_down, query_ping_upload_and_download
    )
    logging.info(f"Created queryable: {key_exp_query_ping_up_down}")

    # Ping test UP load queryable
    key_exp_query_ping_up = keelson.construct_req_rep_key(
        realm=args.realm,
        entity_id=args.entity_id,
        responder_id="network",
        procedure="ping_up",
    )
    query_network_ping_up = session.declare_queryable(
        key_exp_query_ping_up, query_ping_upload
    )
    logging.info(f"Created queryable: {key_exp_query_ping_up}")

    # Ping test DOWN load queryable
    key_exp_query_ping_down = keelson.construct_req_rep_key(
        realm=args.realm,
        entity_id=args.entity_id,
        responder_id="network",
        procedure="ping_down",
    )
    query_network_ping_down = session.declare_queryable(
        key_exp_query_ping_down, query_ping_download
    )
    logging.info(f"Created queryable: {key_exp_query_ping_down}")

    #################################################
    # Setting up PUBLISHER´s

    # Network ping result publisher
    key_exp_pub_results = keelson.construct_pub_sub_key(
        realm=args.realm,
        entity_id=args.entity_id,
        subject="network_ping",  # Needs to be a supported subject
        source_id="results",
    )
    pub_results = session.declare_publisher(
        key_exp_pub_results,
        priority=zenoh.Priority.INTERACTIVE_HIGH(),
        congestion_control=zenoh.CongestionControl.DROP(),
    )
    logging.info(f"Created publisher: {key_exp_pub_results}")

    #################################################

    try:

        if args.trigger == "ping":
            logging.info("Trigger Ping")
            while True:
                for platform in args.ping_common_key:
                    timestamp_init = time.time_ns()

                    for reply in session.get(
                        platform + "/rpc/network/ping", zenoh.Queue(), value=None
                    ):
                        try:
                            timestamp_received = time.time_ns()
                            time_diff = (timestamp_received - timestamp_init) / 1000000
                            logging.info(
                                f"TIME DIFF (0 MB): {time_diff} ms  '{reply.ok.key_expr}' "
                            )

                            result_payload = NetworkResults()
                            result_payload.timestamp.FromNanoseconds(timestamp_received)
                            result_payload.id_sender = args.entity_id
                            result_payload.id_receiver = platform.split("/")[-1]
                            result_payload.ping_count = 0
                            result_payload.payload_description = "Ping"
                            result_payload.latency_ms = time_diff
                            result_payload.payload_size_mb = 0
                            serialized_payload = result_payload.SerializeToString()
                            envelope = keelson.enclose(serialized_payload)
                            pub_results.put(envelope)

                        except Exception as e:
                            logging.debug(f"ERROR: '{e}'")
                            logging.debug(
                                f"Received ERROR: '{reply.err.payload.decode('utf-8')}'"
                            )
                time.sleep(1)

        elif args.trigger == "ping_up_down":
            logging.info("Trigger Ping Up and Down")

            for platform in args.ping_common_key:

                mb = args.start_mb
                count = 0

                while mb <= args.end_mb:
                    timestamp_init = time.time_ns()

                    size_in_bytes = mb * 1024 * 1024
                    dummy_payload = bytes(bytearray(int(size_in_bytes)))

                    payload = NetworkPing()
                    payload.timestamp_sender.FromNanoseconds(timestamp_init)
                    payload.id_sender = args.entity_id
                    payload.id_receiver = platform.split("/")[-1]
                    payload.ping_count = count
                    payload.payload_description = "Ping test upp and down"
                    payload.payload_size_mb = mb
                    payload.payload_size_bytes = size_in_bytes
                    payload.dummy_payload = dummy_payload

                    serialized_payload = payload.SerializeToString()
                    envelope = keelson.enclose(serialized_payload)

                    for reply in session.get(
                        platform + "/rpc/network/ping_up_down",
                        zenoh.Queue(),
                        value=envelope,
                    ):
                        try:
                            timestamp_received = time.time_ns()
                            time_diff = (timestamp_received - timestamp_init) / 1000000
                            logging.info(
                                f"TIME DIFF ({mb} MB): {time_diff} ms  '{reply.ok.key_expr}' "
                            )

                            result_payload = NetworkResults()
                            result_payload.timestamp.FromNanoseconds(timestamp_received)
                            result_payload.id_sender = args.entity_id
                            result_payload.id_receiver = platform.split("/")[-1]
                            result_payload.ping_count = count
                            result_payload.payload_description = "Ping"
                            result_payload.latency_ms = time_diff
                            result_payload.payload_size_mb = mb
                            serialized_payload = result_payload.SerializeToString()
                            envelope = keelson.enclose(serialized_payload)
                            pub_results.put(envelope)
                            time.sleep(1)

                        except Exception as e:
                            logging.debug(f"ERROR: '{e}'")
                            logging.warning(
                                f"Received ERROR: '{reply.err.payload.decode('utf-8')}'"
                            )

                    count += 1
                    mb += args.step_mb
                    time.sleep(1)
                    # END OF LOOP

        elif args.trigger == "ping_up":
            logging.info("Trigger Ping UP")

            for platform in args.ping_common_key:

                mb = args.start_mb
                count = 0

                while mb <= args.end_mb:
                    timestamp_init = time.time_ns()

                    size_in_bytes = mb * 1024 * 1024
                    dummy_payload = bytes(bytearray(int(size_in_bytes)))

                    payload = NetworkPing()
                    payload.timestamp_sender.FromNanoseconds(timestamp_init)
                    payload.id_sender = args.entity_id
                    payload.id_receiver = platform.split("/")[-1]
                    payload.ping_count = count
                    payload.payload_description = "Ping test upp"
                    payload.payload_size_mb = mb
                    payload.payload_size_bytes = size_in_bytes
                    payload.dummy_payload = dummy_payload

                    serialized_payload = payload.SerializeToString()
                    envelope = keelson.enclose(serialized_payload)

                    for reply in session.get(
                        platform + "/rpc/network/ping_up_down",
                        zenoh.Queue(),
                        value=envelope,
                    ):
                        try:
                            timestamp_received = time.time_ns()
                            time_diff = (timestamp_received - timestamp_init) / 1000000
                            logging.debug(
                                f"TIME DIFF ({mb} MB UP): {time_diff} ms  '{reply.ok.key_expr}' "
                            )
                            result_payload = NetworkResults()
                            result_payload.timestamp.FromNanoseconds(timestamp_received)
                            result_payload.id_sender = args.entity_id
                            result_payload.id_receiver = platform.split("/")[-1]
                            result_payload.ping_count = count
                            result_payload.payload_description = "Ping"
                            result_payload.latency_ms = time_diff
                            result_payload.payload_size_mb = mb
                            serialized_payload = result_payload.SerializeToString()
                            envelope = keelson.enclose(serialized_payload)
                            pub_results.put(envelope)
                            time.sleep(1)

                        except Exception as e:
                            logging.debug(f"ERROR: '{e}'")
                            logging.debug(
                                f"Received ERROR: '{reply.err.payload.decode('utf-8')}'"
                            )

                    count += 1
                    mb += args.step_mb
                    time.sleep(1)
                    # END OF LOOP

        elif args.trigger == "ping_down":
            logging.info("Trigger Ping DOWN")

            for platform in args.ping_common_key:

                mb = args.start_mb
                count = 0

                while mb <= args.end_mb:

                    timestamp_init = time.time_ns()

                    payload = NetworkPing()
                    payload.timestamp_sender.FromNanoseconds(timestamp_init)
                    payload.id_sender = args.entity_id
                    payload.id_receiver = platform.split("/")[-1]
                    payload.payload_description = "Ping test down"
                    payload.start_mb = args.start_mb
                    payload.end_mb = args.end_mb
                    payload.step_mb = args.step_mb
                    payload.ping_count = count
                    payload.payload_size_mb = mb

                    serialized_payload = payload.SerializeToString()
                    envelope = keelson.enclose(serialized_payload)

                    for reply in session.get(
                        platform + "/rpc/network/ping_up_down",
                        zenoh.Queue(),
                        value=envelope,
                    ):
                        try:
                            timestamp_received = time.time_ns()
                            time_diff = (timestamp_received - timestamp_init) / 1000000
                            # received_at, enclosed_at, content = keelson.uncover(reply.ok.payload)
                            # message_received = NetworkPing.FromString(content)
                            # logging.debug(f"RES MSG:{message_received}")
                            logging.debug(
                                f"TIME DIFF ({mb} MB DOWN): {time_diff} ms  '{reply.ok.key_expr}' "
                            )
                            result_payload = NetworkResults()
                            result_payload.timestamp.FromNanoseconds(timestamp_received)
                            result_payload.id_sender = args.entity_id
                            result_payload.id_receiver = platform.split("/")[-1]
                            result_payload.ping_count = count
                            result_payload.payload_description = "Ping"
                            result_payload.latency_ms = time_diff
                            result_payload.payload_size_mb = mb
                            serialized_payload = result_payload.SerializeToString()
                            envelope = keelson.enclose(serialized_payload)
                            pub_results.put(envelope)
                            time.sleep(1)

                        except Exception as e:
                            logging.debug(f"ERROR: '{e}'")
                            logging.debug(
                                f"Received ERROR: '{reply.err.payload.decode('utf-8')}'"
                            )

                    count += 1
                    mb += args.step_mb
                    time.sleep(1)

        else:
            logging.info("No trigger specified, waiting for queries...")
            logging.info("Ctrl-C / Ctrl-Z to exit.")

            while True:
                time.sleep(1)

    except KeyboardInterrupt:
        logging.info("Program ended due to user request (Ctrl-C)")
    except Exception as e:
        logging.error(f"Program ended due to error: {e}")
    finally:
        logging.info("Closing Zenoh session...")
        session.close()
        logging.info("Zenoh session closed.")
