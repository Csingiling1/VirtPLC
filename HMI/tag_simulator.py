#!/usr/bin/env python3
"""
VirtPLC HMI Tag Simulator
Simulates tag values for testing the ControlPanel view
"""

import time
import math
import random

def simulate_conveyor_tags():
    """Simulate conveyor belt operations"""
    # Conveyor 1 simulation
    conveyor1_running = False
    conveyor1_speed = 0.0
    conveyor1_target = 25.0

    # Conveyor 2 simulation
    conveyor2_running = False
    conveyor2_speed = 0.0
    conveyor2_target = 30.0

    while True:
        # Simulate conveyor 1
        if conveyor1_running:
            # Gradually approach target speed
            if abs(conveyor1_speed - conveyor1_target) > 0.5:
                conveyor1_speed += (conveyor1_target - conveyor1_speed) * 0.1
            else:
                conveyor1_speed = conveyor1_target + random.uniform(-1, 1)
        else:
            # Slow down when stopped
            conveyor1_speed *= 0.95
            if conveyor1_speed < 0.1:
                conveyor1_speed = 0.0

        # Simulate conveyor 2
        if conveyor2_running:
            if abs(conveyor2_speed - conveyor2_target) > 0.5:
                conveyor2_speed += (conveyor2_target - conveyor2_speed) * 0.1
            else:
                conveyor2_speed = conveyor2_target + random.uniform(-1.5, 1.5)
        else:
            conveyor2_speed *= 0.95
            if conveyor2_speed < 0.1:
                conveyor2_speed = 0.0

        # Randomly toggle conveyor states
        if random.random() < 0.02:  # 2% chance per second
            conveyor1_running = not conveyor1_running
        if random.random() < 0.015:  # 1.5% chance per second
            conveyor2_running = not conveyor2_running

        print("2d")
        print(f"Conveyor1/Running={int(conveyor1_running)}")
        print(f"Conveyor1/Speed={conveyor1_speed:.2f}")
        print(f"Conveyor2/Running={int(conveyor2_running)}")
        print(f"Conveyor2/Speed={conveyor2_speed:.2f}")
        print("")

        time.sleep(0.5)

def simulate_machine_tags():
    """Simulate machine operations"""
    machine_running = False
    is_ready = False
    is_done = False
    pos_x = 0.0
    pos_y = 0.0

    # Movement parameters
    center_x, center_y = 0.0, 0.0
    radius = 80.0
    angle = 0.0
    speed = 0.02  # radians per update

    while True:
        # Simulate machine states
        if machine_running:
            # Machine is operating
            is_ready = True

            # Simulate circular movement
            angle += speed
            pos_x = center_x + radius * math.cos(angle)
            pos_y = center_y + radius * math.sin(angle)

            # Randomly complete operations
            if random.random() < 0.01:  # 1% chance per second
                is_done = not is_done
        else:
            # Machine is stopped
            is_ready = False
            is_done = False
            pos_x *= 0.98  # Gradually return to center
            pos_y *= 0.98

        # Randomly toggle machine state
        if random.random() < 0.005:  # 0.5% chance per second
            machine_running = not machine_running

        print("2d")
        print(f"Machine1/Running={int(machine_running)}")
        print(f"Machine1/IsReady={int(is_ready)}")
        print(f"Machine1/IsDone={int(is_done)}")
        print(f"Machine1/PositionX={pos_x:.2f}")
        print(f"Machine1/PositionY={pos_y:.2f}")
        print("")

        time.sleep(0.5)

if __name__ == "__main__":
    print("VirtPLC HMI Tag Simulator")
    print("========================")
    print("")
    print("This script simulates tag values for testing the ControlPanel view.")
    print("Run this in a separate terminal while testing the HMI.")
    print("")
    print("Tag updates will be printed to stdout in a format that can be")
    print("piped to Ignition Edge for testing.")
    print("")
    print("Press Ctrl+C to stop simulation")
    print("")

    try:
        # Run both simulations concurrently
        import threading

        conveyor_thread = threading.Thread(target=simulate_conveyor_tags, daemon=True)
        machine_thread = threading.Thread(target=simulate_machine_tags, daemon=True)

        conveyor_thread.start()
        machine_thread.start()

        # Keep main thread alive
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nSimulation stopped.")