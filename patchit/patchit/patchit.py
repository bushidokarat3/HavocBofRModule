# patchit.py - Havoc extension for AMSI/ETW patching BOF
#
# An all-in-one BOF to patch, check and revert AMSI and ETW for x64 processes.
#
# Usage:
#   patchit check      - Check if AMSI & ETW are patched
#   patchit all        - Patch both AMSI and ETW
#   patchit amsi       - Patch AMSI only
#   patchit etw        - Patch ETW only
#   patchit revertAll  - Revert both AMSI and ETW
#   patchit revertAmsi - Revert AMSI only
#   patchit revertEtw  - Revert ETW only

from struct import pack, calcsize
from havoc import Demon, RegisterCommand

# Command IDs (must match patchit.c)
CMD_CHECK = 1
CMD_ALL = 2
CMD_AMSI = 3
CMD_ETW = 4
CMD_REVERT_ALL = 5
CMD_REVERT_AMSI = 6
CMD_REVERT_ETW = 7

# BOF paths
BOF_X64 = "./dist/patchit.x64.o"
BOF_X86 = "./dist/patchit.x86.o"


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


def patchit_command(demon_id, *args):
    """AMSI/ETW patching commands."""
    demon = Demon(demon_id)

    if len(args) < 1:
        demon.ConsoleWrite(demon.CONSOLE_INFO, "Usage: patchit <command>")
        demon.ConsoleWrite(demon.CONSOLE_INFO, "")
        demon.ConsoleWrite(demon.CONSOLE_INFO, "Commands:")
        demon.ConsoleWrite(demon.CONSOLE_INFO, "  check      - Check if AMSI & ETW are patched")
        demon.ConsoleWrite(demon.CONSOLE_INFO, "  all        - Patch both AMSI and ETW")
        demon.ConsoleWrite(demon.CONSOLE_INFO, "  amsi       - Patch AMSI only")
        demon.ConsoleWrite(demon.CONSOLE_INFO, "  etw        - Patch ETW only")
        demon.ConsoleWrite(demon.CONSOLE_INFO, "  revertAll  - Revert both AMSI and ETW")
        demon.ConsoleWrite(demon.CONSOLE_INFO, "  revertAmsi - Revert AMSI only")
        demon.ConsoleWrite(demon.CONSOLE_INFO, "  revertEtw  - Revert ETW only")
        return False

    subcommand = args[0].lower()

    # Map subcommand to command ID
    command_map = {
        "check": (CMD_CHECK, "Checking AMSI & ETW patch status..."),
        "all": (CMD_ALL, "Patching AMSI and ETW..."),
        "amsi": (CMD_AMSI, "Patching AMSI..."),
        "etw": (CMD_ETW, "Patching ETW..."),
        "revertall": (CMD_REVERT_ALL, "Reverting AMSI and ETW..."),
        "revertamsi": (CMD_REVERT_AMSI, "Reverting AMSI..."),
        "revertetw": (CMD_REVERT_ETW, "Reverting ETW..."),
    }

    if subcommand not in command_map:
        demon.ConsoleWrite(demon.CONSOLE_ERROR, f"Unknown command: {args[0]}")
        demon.ConsoleWrite(demon.CONSOLE_ERROR, "Use 'patchit' without arguments to see usage")
        return False

    cmd_id, task_msg = command_map[subcommand]

    # Pack arguments
    packer = Packer()
    packer.addint(cmd_id)

    # Get appropriate BOF for architecture
    arch = demon.ProcessArch
    if "64" in str(arch) if arch else True:
        bof_path = BOF_X64
    else:
        bof_path = BOF_X86

    # Create task
    task_id = demon.ConsoleWrite(demon.CONSOLE_TASK, task_msg)

    # Execute BOF
    demon.InlineExecute(task_id, "go", bof_path, packer.getbuffer(), False)

    return task_id


# Register the command
RegisterCommand(
    patchit_command,
    "",
    "patchit",
    "Patch, check, or revert AMSI and ETW (defense evasion)",
    0,
    "<check|all|amsi|etw|revertAll|revertAmsi|revertEtw>",
    "patchit all"
)
