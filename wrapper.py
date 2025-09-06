#!/usr/bin/env python3
import requests
import json


class AsciiArtGenerator:
    """Public wrapper that calls private API service"""

    def __init__(self):
        self.api_url = "https://ascii-art-api-e3rw.onrender.com"

    def create(self, steps=None):
        """Create static art via API"""
        try:
            payload = {"steps": steps} if steps else {}
            response = requests.post(
                f"{self.api_url}/generate", json=payload, timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"art": f"API unavailable: {e}", "status": "error"}

    def display(self, show_info=True):
        """Display static art"""
        result = self.create()
        if show_info and result.get("status") != "error":
            print(f"\nNon-Repeating ASCII Art Generator")
            print(
                f"Creation #{result.get('creation', 1)} | Evolution Steps: {result.get('steps', 'N/A')}"
            )
            print(f"Generated: {result.get('timestamp', 'N/A')}")
            print("=" * 80)

        print(result.get("art", "Generation failed"))

        if show_info and result.get("status") != "error":
            print("=" * 80)
            print("This pattern is mathematically guaranteed to never repeat.")

    def save_to_file(self, filename=None):
        """Save art to file"""
        result = self.create()
        if result.get("status") == "error":
            return None

        if filename is None:
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ascii_art_{timestamp}.txt"

        with open(filename, "w") as f:
            f.write("Non-Repeating ASCII Art Generator\n")
            f.write("=" * 80 + "\n\n")
            f.write(result.get("art", ""))
            f.write(f"\n\n" + "=" * 80)

        return filename

    def animate(self, max_generations=None, delay=0.5):
        """Rate-limited live animation via API"""
        import time
        import os

        try:
            # Request animation from API
            payload = {"max_generations": min(max_generations or 11, 11)}
            response = requests.post(
                f"{self.api_url}/animate", json=payload, timeout=120
            )

            if response.status_code == 429:
                # Rate limited - fall back to single frame
                rate_info = response.json()
                print("Daily animation limit reached (11 generations)")
                print(f"Limit resets: {rate_info.get('limit_reset', 'in 24 hours')}")
                print("Showing single generation instead:")
                return self.display()

            response.raise_for_status()
            data = response.json()

            print("Live Evolution Animation")
            print(
                f"Generations: {len(data['frames'])}/11 | Remaining today: {data.get('remaining_today', 0)}"
            )
            print("4-second transitions | Press Ctrl+C to stop\n")

            # Display frames with 4-second delays
            for i, frame in enumerate(data["frames"]):
                print("\033c", end="")

                print("Live Non-Repeating ASCII Art Evolution")
                print(
                    f"Generation: {frame['generation']}/{len(data['frames'])} | Remaining today: {data.get('remaining_today', 0)}"
                )
                print("=" * 80)
                print(frame["art"])
                print("=" * 80)
                print("Mathematical evolution in progress... (4s transitions)")

                if i < len(data["frames"]) - 1:  # Don't delay after last frame
                    time.sleep(4.0)  # 4 second transitions

            print(
                f"\nAnimation complete! Used {len(data['frames'])}/11 daily generations"
            )
            rate_info = data.get("rate_limit_info", {})
            if rate_info:
                print(
                    f"Daily limit resets: {rate_info.get('reset_time', 'in 24 hours')}"
                )

        except requests.exceptions.RequestException as e:
            print("Animation unavailable - showing single generation:")
            self.display()
        except KeyboardInterrupt:
            print("\nAnimation stopped by user")
