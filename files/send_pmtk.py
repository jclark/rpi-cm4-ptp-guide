import argparse
import serial
import time

def calculate_checksum(sentence):
    checksum = 0
    for char in sentence:
        checksum ^= ord(char)
    return f"{checksum:02X}"

def build_pmtk_command(command_num, data=None):
    base = f"PMTK{command_num}"
    if data:
        base += f",{data}"
    checksum = calculate_checksum(base)
    return f"${base}*{checksum}\r\n"

def send_pmtk(port, baudrate, command_num, data):
    cmd = build_pmtk_command(command_num, data)
    print(f"Sending to {port} at {baudrate} baud:\n{cmd.strip()}")
    with serial.Serial(port, baudrate, timeout=1) as ser:
        ser.write(cmd.encode('ascii'))
        return True
    return False

def listen_for_responses(port, baudrate, timeout=None, show_all=False):
    print(f"Listening on {port} at {baudrate} baud... Press Ctrl+C to stop.")
    start_time = time.time()
    try:
        with serial.Serial(port, baudrate, timeout=0.5) as ser:
            while True:
                line = ser.readline().decode('ascii', errors='ignore').strip()
                if line:
                    if show_all or "PMTK" in line:
                        print(line)
                if timeout and (time.time() - start_time > timeout):
                    break
    except KeyboardInterrupt:
        print("\nStopped by user.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send PMTK command and/or listen to GPS output")
    parser.add_argument("command", nargs="?", help="PMTK command number (e.g., 000, 220)")
    parser.add_argument("data", nargs="?", default=None, help="Optional PMTK command data")
    parser.add_argument("--port", default="/dev/ttyAMA0", help="Serial port (default: /dev/ttyAMA0)")
    parser.add_argument("--baud", type=int, default=9600, help="Baud rate (default: 9600)")
    parser.add_argument("--listen", action="store_true", help="Just listen to all GPS output (like cat)")
    parser.add_argument("--timeout", type=int, default=5, help="Response timeout in seconds (default: 5)")

    args = parser.parse_args()

    if args.listen and not args.command:
        listen_for_responses(args.port, args.baud, show_all=True)
    elif args.command:
        if send_pmtk(args.port, args.baud, args.command, args.data):
            listen_for_responses(args.port, args.baud, timeout=args.timeout, show_all=False)
    else:
        parser.print_help()
