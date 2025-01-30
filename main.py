import curses


def display_contact(stdscr, contact):
    stdscr.clear()
    stdscr.addstr(1, 1, f"Name: {contact['name']}")
    stdscr.addstr(2, 1, f"Phone: {contact['phone']}")
    stdscr.addstr(3, 1, f"Email: {contact['email']}")
    stdscr.addstr(5, 1, "Use left/right arrows to navigate, 'q' to quit")
    stdscr.refresh()

def main(stdscr):
    curses.curs_set(0)
    contacts = [
        {"name": "John Doe", "phone": "123-456-7890", "email": "john@example.com"},
        {"name": "Jane Smith", "phone": "098-765-4321", "email": "jane@example.com"}
    ]
    current_contact = 0

    while True:
        display_contact(stdscr, contacts[current_contact])
        key = stdscr.getch()

        if key == ord('q'):
            break
        elif key == curses.KEY_RIGHT:
            current_contact = (current_contact + 1) % len(contacts)
        elif key == curses.KEY_LEFT:
            current_contact = (current_contact - 1) % len(contacts)

curses.wrapper(main)
