import asyncio
import curses
import pyatv
from pyatv.interface import BaseConfig
import pyatv.exceptions
from pyatv.const import Protocol

async def remote_control_device(device: BaseConfig, stdscr, loop):
    atv = await pyatv.connect(device, loop=loop)
    stdscr.addstr(f"Connected to: {device.name}\n")
    stdscr.refresh()

    while True:
        try:
            key = stdscr.getch()

            if key == curses.KEY_UP:
                await atv.remote_control.up()
            elif key == curses.KEY_DOWN:
                await atv.remote_control.down()
            elif key == curses.KEY_LEFT:
                await atv.remote_control.left()
            elif key == curses.KEY_RIGHT:
                await atv.remote_control.right()
            elif key == ord('q') or key == 27:  # 'q' or ESC key to exit
                break
        except Exception as e:
            atv.close()
            stdscr.addstr(f"Error: {str(e)}\n")
            stdscr.refresh()
            pass

async def choose_device(stdscr, loop):
    selected_device = None
    selected_index = 0
    devices = []

    stdscr.clear()
    stdscr.addstr("Scanning for available Apple TVs...\n")
    stdscr.refresh()

    devices = await pyatv.scan(loop=loop)

    if not devices:
        stdscr.addstr("No Apple TVs found.\n")
        stdscr.refresh()
        stdscr.getch()  # Wait for a keypress to exit
        return None

    while True:
        stdscr.clear()
        stdscr.addstr("Available Apple TVs:\n")
        for i, device in enumerate(devices, start=1):
            if i - 1 == selected_index:
                stdscr.addstr(f"> {i}. {device.name} ({device.address})\n")
            else:
                stdscr.addstr(f"  {i}. {device.name} ({device.address})\n")
        stdscr.refresh()

        key = stdscr.getch()
        if key == curses.KEY_UP:
            selected_index = max(0, selected_index - 1)
        elif key == curses.KEY_DOWN:
            selected_index = min(len(devices) - 1, selected_index + 1)
        elif key == 10:  # Enter key
            selected_device = devices[selected_index]
            break

    return selected_device

def main(stdscr):
    # Set up curses
    curses.curs_set(0)  # Hide the cursor
    stdscr.keypad(1)    # Enable special keys (e.g., arrow keys)

    loop = asyncio.get_event_loop()
    device = loop.run_until_complete(choose_device(stdscr, loop))

    if device:
        stdscr.addstr(f"Connecting to {device.name}\n")
        stdscr.refresh()
        loop.run_until_complete(remote_control_device(device, stdscr, loop))

    # Reset the terminal settings
    curses.endwin()

if __name__ == "__main__":
    curses.wrapper(main)

