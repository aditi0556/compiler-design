import socket
import struct
import random
import hashlib
import os

HOST = "0.0.0.0"
PORT = 5000

CHUNK_SIZE = 1024
LOSS_RATE = 0.60       # 30% simulated packet loss
BUFFER_SIZE = 2048


def send_ack(sock, addr, seq):
    """
    Send an ACK packet.

    Packet format:
        1 byte  : type = ACK
        4 bytes : sequence number
    """

    packet = struct.pack("!BI", 2, seq)

    # Simulate ACK loss
    if random.random() < LOSS_RATE:
        print(f"[SIMULATED LOSS] ACK {seq} was dropped")
        return

    sock.sendto(packet, addr)
    print(f"[SERVER] Sent ACK {seq}")


def receive_file():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))

    print(f"[SERVER] Listening on {HOST}:{PORT}")

    expected_seq = 0
    file = None
    filename = None
    received_bytes = 0

    while True:

        packet, client_addr = sock.recvfrom(BUFFER_SIZE)
        packet_type = packet[0]
        if packet_type!=4 and len(packet) < 5:
            continue
        if packet_type == 1:
            name_length = struct.unpack("!I", packet[1:5])[0]
            filename = packet[5:5 + name_length].decode()
            print(f"\n[SERVER] Receiving file: {filename}")
            file = open("received_" + filename, "wb")
            expected_seq = 0
            received_bytes = 0
            send_ack(sock, client_addr, 0)
        elif packet_type == 3:
            seq = struct.unpack("!I", packet[1:5])[0]

            data = packet[5:]

            print(
                f"[SERVER] Received DATA seq={seq}, "
                f"{len(data)} bytes"
            )

            # Correct packet
            if seq == expected_seq:

                file.write(data)
                received_bytes += len(data)

                print(
                    f"[SERVER] Accepted seq={seq}"
                )

                send_ack(sock, client_addr, seq)

                expected_seq += 1

            # Duplicate packet
            elif seq < expected_seq:

                print(
                    f"[SERVER] Duplicate seq={seq}, "
                    f"expected={expected_seq}"
                )

                # Send ACK again
                send_ack(sock, client_addr, seq)

            # Out-of-order packet
            else:

                print(
                    f"[SERVER] Out-of-order seq={seq}, "
                    f"expected={expected_seq}"
                )

                # ACK last correctly received packet
                if expected_seq > 0:
                    send_ack(
                        sock,
                        client_addr,
                        expected_seq - 1
                    )

        # --------------------------------------------------
        # END packet
        # --------------------------------------------------

        elif packet_type == 4:

            print("\n[SERVER] File transfer completed.")

            file.close()

            # Calculate SHA256
            sha256 = hashlib.sha256()

            with open("received_" + filename, "rb") as f:
                while True:
                    data = f.read(4096)

                    if not data:
                        break

                    sha256.update(data)

            digest = sha256.hexdigest()

            print(
                f"[SERVER] Received bytes: {received_bytes}"
            )

            print(
                f"[SERVER] SHA256: {digest}"
            )

            # Send DONE
            done_packet = b"DONE"

            sock.sendto(done_packet, client_addr)

            break

    sock.close()


if __name__ == "__main__":
    receive_file()
