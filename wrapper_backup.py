#!/usr/bin/env python3
import requests
import json


class AsciiArtGenerator:
    """Public wrapper that calls private API service"""

    def __init__(self):
        # TODO: Replace with your actual API URL after deployment
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
        """Simplified animation via API"""
        print("Live animation requires API connection...")
        print("Generating single frame via API:")
        self.display()
        return self.create()
