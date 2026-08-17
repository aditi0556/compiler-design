import socket
import struct
import sys
import os
import hashlib
import random
import time
SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000
CHUNK_SIZE = 1024
TIMEOUT = 1.0
MAX_RETRIES = 10
BUFFER_SIZE = 2048
def calculate_sha256(filename):
    sha256 = hashlib.sha256()
    with open(filename, "rb") as f:
        while True:
            data = f.read(4096)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()

def send_file(filename):
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    sock.settimeout(TIMEOUT)
    server_addr = ( SERVER_IP, SERVER_PORT)
    original_hash = calculate_sha256(filename)
    print(f"[CLIENT] Original SHA256:")
    print(original_hash)
    filename_bytes = os.path.basename(filename).encode()

    start_packet = (struct.pack("!BI", 1, len(filename_bytes)) + filename_bytes)
    print( f"\n[CLIENT] Sending START packet")
    sock.sendto( start_packet, server_addr)
    while True:
        try:
            packet, _ = sock.recvfrom(BUFFER_SIZE)
            if len(packet) >= 5:
                packet_type = packet[0]
                if packet_type == 2:
                    ack_seq = struct.unpack( "!I", packet[1:5])[0]
                    if ack_seq == 0:
                        print("[CLIENT] START acknowledged" )
                        break
        except socket.timeout:
            print("[CLIENT] START timeout, ""retransmitting...")
            sock.sendto(start_packet,server_addr )
    sequence_number = 0
    with open(filename, "rb") as f:
        while True:
            data = f.read(CHUNK_SIZE)
            if not data:
                break
            packet = (struct.pack("!BI",3,sequence_number)+ data)
            retries = 0
            while True:
                print(f"\n[CLIENT] Sending DATA "f"seq={sequence_number}")
                sock.sendto( packet,server_addr)
                try:
                    while True:
                        ack_packet, _ = sock.recvfrom(BUFFER_SIZE)
                        if len(ack_packet) < 5:
                            continue
                        ack_type = ack_packet[0]
                        if ack_type != 2:
                            continue
                        ack_seq = struct.unpack(
                            "!I",
                            ack_packet[1:5]
                        )[0]
                        print(
                            f"[CLIENT] Received ACK "
                            f"{ack_seq}"
                        )

                        if ack_seq == sequence_number:

                            print(
                                f"[CLIENT] DATA "
                                f"{sequence_number} "
                                f"successfully delivered"
                            )

                            break

                    break

                except socket.timeout:

                    retries += 1

                    print(
                        f"[CLIENT] TIMEOUT for seq="
                        f"{sequence_number}"
                    )

                    print(
                        f"[CLIENT] Retransmission "
                        f"{retries}/{MAX_RETRIES}"
                    )

                    if retries >= MAX_RETRIES:

                        print(
                            "[CLIENT] Maximum retries "
                            "reached."
                        )

                        sock.close()

                        return

            sequence_number += 1

    # --------------------------------------------------
    # END packet
    # --------------------------------------------------

    print("\n[CLIENT] Sending FIN")

    fin_packet = bytes([4])

    sock.sendto(
        fin_packet,
        server_addr
    )

    # Wait for DONE
    try:

        packet, _ = sock.recvfrom(BUFFER_SIZE)

        if packet == b"DONE":

            print(
                "[CLIENT] Server confirmed "
                "successful transfer."
            )

    except socket.timeout:

        print(
            "[CLIENT] Did not receive final "
            "confirmation."
        )

    sock.close()

    print("\n================================")
    print("FILE TRANSFER SUCCESSFUL")
    print("================================")

    print(
        f"Original SHA256 : {original_hash}"
    )


if __name__ == "__main__":

    if len(sys.argv) != 2:

        print(
            "Usage: python client.py <filename>"
        )

        sys.exit(1)

    send_file(sys.argv[1])
