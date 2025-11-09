from my_agents.meeting_scheduler import schedule_meeting
from my_agents.meeting_canceller import cancel_meeting


def main():
    print("AI Meeting Agent Test")
    print("Type '1' to schedule, '2' to cancel, 'q' to quit")

    while True:
        choice = input("Enter choice: ")
        if choice == '1':
            name = input("Enter meeting name: ")
            time = input("Enter time: ")
            print(schedule_meeting(name, time))
        elif choice == '2':
            name = input("Enter meeting name to cancel: ")
            print(cancel_meeting(name))
        elif choice.lower() == 'q':
            print("Exiting...")
            break
        else:
            print("Invalid choice!")


if __name__ == "__main__":
    main()
