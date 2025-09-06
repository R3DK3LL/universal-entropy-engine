#!/usr/bin/env python3
import requests
import json
import time
import os
from datetime import datetime


class NeuralPathwayRenderer:
    def __init__(self):
        self.neuron_symbols = ["◉", "●", "○", "◯", "⊙", "⊗"]
        self.pathway_symbols = {
            "horizontal": "━",
            "vertical": "┃",
            "cross": "╋",
            "junction_t_up": "┻",
            "junction_t_down": "┳",
            "junction_t_left": "┫",
            "junction_t_right": "┣",
            "corner_tl": "┏",
            "corner_tr": "┓",
            "corner_bl": "┗",
            "corner_br": "┛",
            "branch": "┼",
        }

    def analyze_8_neighborhood(self, grid, i, j):
        height, width = len(grid), len(grid[0])
        neighbors = []
        positions = [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        ]

        for di, dj in positions:
            ni, nj = i + di, j + dj
            if 0 <= ni < height and 0 <= nj < width:
                neighbors.append(grid[ni][nj])
            else:
                neighbors.append(0)

        return neighbors

    def get_connection_pattern(self, grid, i, j):
        if grid[i][j] == 0:
            return " "

        neighbors = self.analyze_8_neighborhood(grid, i, j)

        up, down = neighbors[1], neighbors[6]
        left, right = neighbors[3], neighbors[4]
        ul, ur = neighbors[0], neighbors[2]
        dl, dr = neighbors[5], neighbors[7]

        active_count = sum(neighbors)

        if active_count == 0:
            return self.neuron_symbols[0]

        has_vertical = up or down
        has_horizontal = left or right
        has_diagonal = ul or ur or dl or dr

        if has_vertical and has_horizontal:
            if active_count >= 4:
                return self.pathway_symbols["cross"]
            else:
                return self.pathway_symbols["branch"]
        elif has_vertical:
            if up and down:
                return self.pathway_symbols["vertical"]
            elif up:
                return self.pathway_symbols["junction_t_up"]
            else:
                return self.pathway_symbols["junction_t_down"]
        elif has_horizontal:
            if left and right:
                return self.pathway_symbols["horizontal"]
            elif left:
                return self.pathway_symbols["junction_t_left"]
            else:
                return self.pathway_symbols["junction_t_right"]
        elif has_diagonal:
            if active_count == 1:
                return self.neuron_symbols[1]
            else:
                return self.pathway_symbols["branch"]
        else:
            symbol_index = min(active_count - 1, len(self.neuron_symbols) - 1)
            return self.neuron_symbols[symbol_index]

    def render_neural_grid(self, grid):
        neural_lines = []
        for i, row in enumerate(grid):
            line = ""
            for j, cell in enumerate(row):
                symbol = self.get_connection_pattern(grid, i, j)
                line += symbol
            neural_lines.append(line.rstrip())
        return "\n".join(neural_lines)

    def analyze_network_properties(self, grid):
        height, width = len(grid), len(grid[0])
        total_cells = height * width
        active_cells = sum(sum(row) for row in grid)

        clusters = self.find_connected_components(grid)
        largest_cluster = max(len(cluster) for cluster in clusters) if clusters else 0

        return {
            "active_ratio": active_cells / total_cells,
            "cluster_count": len(clusters),
            "largest_cluster": largest_cluster,
            "network_density": active_cells / total_cells,
            "fragmentation": len(clusters) / max(1, active_cells),
        }

    def find_connected_components(self, grid):
        height, width = len(grid), len(grid[0])
        visited = [[False] * width for _ in range(height)]
        components = []

        def dfs(i, j, component):
            if (
                i < 0
                or i >= height
                or j < 0
                or j >= width
                or visited[i][j]
                or grid[i][j] == 0
            ):
                return

            visited[i][j] = True
            component.append((i, j))

            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    if di != 0 or dj != 0:
                        dfs(i + di, j + dj, component)

        for i in range(height):
            for j in range(width):
                if grid[i][j] == 1 and not visited[i][j]:
                    component = []
                    dfs(i, j, component)
                    if component:
                        components.append(component)

        return components


class AsciiArtGenerator:
    def __init__(self):
        self.api_url = "https://ascii-art-api-e3rw.onrender.com"
        self.session_count = 0
        self.max_sessions = 11
        self.metrics_file = "mathematical_metrics_log.txt"
        self.renderer = NeuralPathwayRenderer()

    def create(self, steps=None):
        if self.session_count >= self.max_sessions:
            return {
                "art": f"Session limit reached ({self.max_sessions}/11)",
                "status": "limit_reached",
            }

        try:
            payload = {"steps": steps} if steps else {}
            response = requests.post(
                f"{self.api_url}/generate", json=payload, timeout=30
            )
            response.raise_for_status()

            result = response.json()
            self.session_count += 1

            self._save_metrics_to_file(result, "static")

            return result
        except Exception as e:
            return {"art": f"API unavailable: {e}", "status": "error"}

    def _convert_art_to_grid(self, art_string):
        lines = art_string.strip().split("\n")
        max_width = max(len(line) for line in lines) if lines else 0

        grid = []
        for line in lines:
            row = []
            padded_line = line.ljust(max_width)
            for char in padded_line:
                row.append(1 if char != " " else 0)
            grid.append(row)

        return grid

    def display(self, show_info=True, show_metrics=True):
        result = self.create()

        if result.get("status") == "error":
            print(result.get("art", "Generation failed"))
            return

        if result.get("status") == "limit_reached":
            print(result.get("art"))
            print(f"Metrics saved to: {self.metrics_file}")
            return

        if show_info and result.get("status") != "error":
            print(f"\nNeural Pathway ASCII Art Generator")
            print(
                f"Creation #{result.get('creation', 1)} | Evolution Steps: {result.get('steps', 'N/A')}"
            )
            print(f"Generated: {result.get('timestamp', 'N/A')}")
            print("=" * 80)

        original_art = result.get("art", "")
        grid = self._convert_art_to_grid(original_art)
        neural_art = self.renderer.render_neural_grid(grid)
        network_props = self.renderer.analyze_network_properties(grid)

        print("ORIGINAL ASCII:")
        print(original_art)
        print("\nNEURAL PATHWAY VISUALIZATION:")
        print(neural_art)

        if show_metrics and "metrics" in result:
            self._display_mathematical_metrics(
                result["metrics"],
                result.get("calculation_breakdowns", {}),
                network_props,
            )

        if show_info and result.get("status") != "error":
            print("=" * 80)
            print(
                "Neural pathways derived from mathematical cellular automaton evolution."
            )
            print(
                f"Session {self.session_count}/{self.max_sessions} | Metrics logged to {self.metrics_file}"
            )

    def _display_mathematical_metrics(self, metrics, breakdowns, network_props):
        print("\n┌─────────────────────────────────────────┐")
        print("│         MATHEMATICAL METRICS            │")
        print("├─────────────────────────────────────────┤")

        print(f"│  generation: {metrics.get('generation', 'N/A'):<26} [▼]│")
        print(f"│  active_cells: {metrics.get('active_cells', 'N/A'):<22} [▼]│")
        print(f"│  entropy: {metrics.get('entropy', 'N/A'):<27} [▼]│")
        print(f"│  autocorrelation: {metrics.get('autocorrelation', 'N/A'):<19} [▼]│")
        print("├─────────────────────────────────────────┤")
        print("│         NEURAL NETWORK ANALYSIS         │")
        print("├─────────────────────────────────────────┤")
        print(
            f"│  network_density: {network_props['network_density']:.4f}          [▼]│"
        )
        print(f"│  cluster_count: {network_props['cluster_count']:<21} [▼]│")
        print(f"│  largest_cluster: {network_props['largest_cluster']:<19} [▼]│")
        print(f"│  fragmentation: {network_props['fragmentation']:.4f}           [▼]│")
        print("└─────────────────────────────────────────┘")

        print("\nPress Enter for dropdown examples, or type metric name:")
        user_input = input("> ").strip().lower()

        if user_input in ["entropy", "e"] and breakdowns:
            self._show_metric_breakdown("entropy", breakdowns)
        elif user_input in ["network_density", "n"]:
            self._show_network_analysis(network_props)
        elif user_input == "" and breakdowns:
            available_metrics = list(breakdowns.keys())[:2]
            for metric in available_metrics:
                self._show_metric_breakdown(metric, breakdowns)

    def _show_metric_breakdown(self, metric_name, breakdowns):
        if metric_name not in breakdowns:
            print(f"No breakdown available for {metric_name}")
            return

        breakdown = breakdowns[metric_name]
        print(f"\n┌─ {metric_name.upper()} CALCULATION BREAKDOWN")
        print(f"│  Formula: {breakdown.get('formula', 'N/A')}")
        print("│  Steps:")

        for i, step in enumerate(breakdown.get("steps", []), 1):
            print(f"│    {i}. {step}")

        if "computation" in breakdown:
            print(f"│  Computation: {breakdown['computation']}")

        print(f"│  Result: {breakdown.get('result', 'N/A')}")
        print("└─────────────────────────────────────────")

    def _show_network_analysis(self, network_props):
        print(f"\n┌─ NEURAL NETWORK ANALYSIS")
        print(f"│  Network Density: {network_props['network_density']:.4f}")
        print(f"│  Total Clusters: {network_props['cluster_count']}")
        print(f"│  Largest Cluster Size: {network_props['largest_cluster']}")
        print(f"│  Fragmentation Index: {network_props['fragmentation']:.4f}")
        print("│  Interpretation:")
        if network_props["fragmentation"] < 0.1:
            print("│    Highly connected neural network")
        elif network_props["fragmentation"] < 0.3:
            print("│    Moderately fragmented pathways")
        else:
            print("│    Sparse, isolated neural clusters")
        print("└─────────────────────────────────────────")

    def save_to_file(self, filename=None):
        result = self.create()
        if result.get("status") in ["error", "limit_reached"]:
            return None

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"neural_pathway_art_{timestamp}.txt"

        original_art = result.get("art", "")
        grid = self._convert_art_to_grid(original_art)
        neural_art = self.renderer.render_neural_grid(grid)
        network_props = self.renderer.analyze_network_properties(grid)

        with open(filename, "w") as f:
            f.write("Neural Pathway ASCII Art Generator\n")
            f.write("=" * 80 + "\n\n")
            f.write("ORIGINAL ASCII:\n")
            f.write(original_art)
            f.write("\n\nNEURAL PATHWAY VISUALIZATION:\n")
            f.write(neural_art)
            f.write(f"\n\n" + "=" * 80)

            if "metrics" in result:
                metrics = result["metrics"]
                f.write(f"\n\nMathematical Analysis:")
                f.write(f"\nGeneration: {metrics.get('generation', 'N/A')}")
                f.write(f"\nActive Cells: {metrics.get('active_cells', 'N/A')}")
                f.write(f"\nEntropy: {metrics.get('entropy', 'N/A')}")
                f.write(f"\nNetwork Density: {network_props['network_density']:.4f}")
                f.write(f"\nCluster Count: {network_props['cluster_count']}")

        return filename

    def _save_metrics_to_file(self, result, run_type):
        try:
            try:
                with open(self.metrics_file, "r") as f:
                    existing_data = json.loads(f.read())
            except (FileNotFoundError, json.JSONDecodeError):
                existing_data = {"runs": [], "total_sessions": 0}

            if len(existing_data["runs"]) >= self.max_sessions:
                return

            original_art = result.get("art", "")
            grid = self._convert_art_to_grid(original_art)
            network_props = self.renderer.analyze_network_properties(grid)

            run_data = {
                "session_id": self.session_count,
                "type": run_type,
                "timestamp": result.get("timestamp", datetime.now().isoformat()),
                "metrics": result.get("metrics", {}),
                "neural_analysis": network_props,
                "evolution_steps": result.get(
                    "steps", result.get("evolution_steps", 0)
                ),
            }

            existing_data["runs"].append(run_data)
            existing_data["total_sessions"] = len(existing_data["runs"])

            with open(self.metrics_file, "w") as f:
                json.dump(existing_data, f, indent=2)

        except Exception as e:
            print(f"Warning: Could not save metrics to file: {e}")

    def animate(self, max_generations=None, delay=0.5):
        if self.session_count >= self.max_sessions:
            print(f"Session limit reached ({self.max_sessions}/11)")
            print(f"Metrics saved to: {self.metrics_file}")
            return self.display()

        try:
            payload = {"max_generations": min(max_generations or 11, 11)}
            response = requests.post(
                f"{self.api_url}/animate", json=payload, timeout=120
            )

            if response.status_code == 429:
                rate_info = response.json()
                print("Daily animation limit reached (11 generations)")
                print(f"Limit resets: {rate_info.get('limit_reset', 'in 24 hours')}")
                print("Showing single generation instead:")
                return self.display()

            response.raise_for_status()
            data = response.json()
            self.session_count += 1

            if "frames" in data and data["frames"]:
                final_frame = data["frames"][-1]
                animation_result = {
                    "timestamp": data.get("timestamp", datetime.now().isoformat()),
                    "metrics": final_frame.get("metrics", {}),
                    "art": final_frame.get("art", ""),
                    "steps": len(data["frames"]),
                }
                self._save_metrics_to_file(animation_result, "animation")

            print("Live Neural Pathway Evolution Animation")
            print(
                f"Generations: {len(data.get('frames', []))}/11 | Session: {self.session_count}/{self.max_sessions}"
            )
            print(f"Delay: {delay}s transitions | Press Ctrl+C to stop\n")

            for i, frame in enumerate(data.get("frames", [])):
                os.system("clear" if os.name == "posix" else "cls")

                print("Live Neural Pathway Evolution")
                print(
                    f"Generation: {frame.get('generation', i)}/{len(data['frames'])} | Session: {self.session_count}/{self.max_sessions}"
                )
                print("=" * 80)

                original_art = frame.get("art", "")
                if original_art:
                    grid = self._convert_art_to_grid(original_art)
                    neural_art = self.renderer.render_neural_grid(grid)
                    network_props = self.renderer.analyze_network_properties(grid)

                    print("NEURAL PATHWAYS:")
                    print(neural_art)
                    print("=" * 80)

                    if "metrics" in frame:
                        metrics = frame["metrics"]
                        print(
                            f"Active: {metrics.get('active_cells', 'N/A')} | ", end=""
                        )
                        print(f"Entropy: {metrics.get('entropy', 'N/A')} | ", end="")
                        print(f"Clusters: {network_props['cluster_count']}")

                print("Neural network evolution in progress...")

                if i < len(data["frames"]) - 1:
                    time.sleep(delay)

            print(
                f"\nAnimation complete! Session {self.session_count}/{self.max_sessions}"
            )
            print(f"Metrics logged to: {self.metrics_file}")

            if data.get("frames") and "metrics" in data["frames"][-1]:
                final_frame = data["frames"][-1]
                final_art = final_frame.get("art", "")
                if final_art:
                    final_grid = self._convert_art_to_grid(final_art)
                    final_network_props = self.renderer.analyze_network_properties(
                        final_grid
                    )
                    print("\nFinal Neural Network State:")
                    self._display_mathematical_metrics(
                        final_frame["metrics"],
                        final_frame.get("calculation_breakdowns", {}),
                        final_network_props,
                    )

        except requests.exceptions.RequestException as e:
            print("Animation unavailable - showing single generation:")
            self.display()
        except KeyboardInterrupt:
            print(
                f"\nAnimation stopped by user. Session {self.session_count}/{self.max_sessions}"
            )
            print(f"Metrics logged to: {self.metrics_file}")

    def get_session_status(self):
        return {
            "current_session": self.session_count,
            "max_sessions": self.max_sessions,
            "remaining": self.max_sessions - self.session_count,
            "metrics_file": self.metrics_file,
        }

    def view_metrics_log(self):
        try:
            with open(self.metrics_file, "r") as f:
                data = json.loads(f.read())

            print(
                f"\n=== NEURAL PATHWAY METRICS LOG ({data['total_sessions']}/{self.max_sessions} sessions) ==="
            )
            for run in data["runs"]:
                print(
                    f"\nSession {run['session_id']} ({run['type']}) - {run['timestamp']}"
                )
                metrics = run.get("metrics", {})
                neural = run.get("neural_analysis", {})
                print(f"  Generation: {metrics.get('generation', 'N/A')}")
                print(f"  Active Cells: {metrics.get('active_cells', 'N/A')}")
                print(f"  Network Clusters: {neural.get('cluster_count', 'N/A')}")
                print(f"  Network Density: {neural.get('network_density', 'N/A')}")

        except (FileNotFoundError, json.JSONDecodeError):
            print("No metrics log found.")


def test_neural_renderer():
    print("Testing Neural Pathway Renderer...")

    renderer = NeuralPathwayRenderer()

    test_grid = [[1, 1, 0, 1], [0, 1, 1, 1], [1, 0, 1, 0], [1, 1, 1, 1]]

    neural_output = renderer.render_neural_grid(test_grid)
    network_props = renderer.analyze_network_properties(test_grid)

    print("Test Grid:")
    for row in test_grid:
        print(" ".join(str(cell) for cell in row))

    print("\nNeural Visualization:")
    print(neural_output)

    print("\nNetwork Properties:")
    for key, value in network_props.items():
        print(f"  {key}: {value}")

    print("Neural renderer test complete.")
    return True


def main():
    gen = AsciiArtGenerator()

    print("Neural Pathway ASCII Art Generator")
    print("Powered by mathematical cellular automaton with 8-neighborhood connectivity")
    print(f"\nSession Limit: {gen.max_sessions} runs")

    while True:
        status = gen.get_session_status()
        print(
            f"\nSession {status['current_session']}/{status['max_sessions']} | Remaining: {status['remaining']}"
        )

        if status["remaining"] <= 0:
            print("Session limit reached. View saved metrics or restart.")
            choice = input("Options: [v]iew metrics, [q]uit: ").lower()
            if choice == "v":
                gen.view_metrics_log()
            break

        print("\nOptions:")
        print("  [Enter] - Generate neural pathway art")
        print("  'live' - Watch live neural evolution")
        print("  'live 5' - Watch 5 generations")
        print("  'fast' - Fast animation (0.2s delay)")
        print("  'slow' - Slow animation (1.0s delay)")
        print("  's' - Save neural art to file")
        print("  'v' - View metrics log")
        print("  'test' - Test neural renderer")
        print("  'q' - Quit")

        user_input = input("\n> ").strip().lower()

        if user_input == "q":
            print("Thank you for exploring neural pathway visualization.")
            status = gen.get_session_status()
            print(
                f"Sessions used: {status['current_session']}/{status['max_sessions']}"
            )
            if status["current_session"] > 0:
                print(f"Metrics saved to: {status['metrics_file']}")
            break
        elif user_input == "s":
            filename = gen.save_to_file()
            if filename:
                print(f"Neural pathway art saved to {filename}")
        elif user_input == "v":
            gen.view_metrics_log()
        elif user_input == "test":
            test_neural_renderer()
        elif user_input.startswith("live"):
            parts = user_input.split()
            if len(parts) > 1 and parts[1].isdigit():
                max_gen = int(parts[1])
                gen.animate(max_generations=max_gen, delay=0.5)
            else:
                gen.animate()
        elif user_input == "fast":
            gen.animate(delay=0.2)
        elif user_input == "slow":
            gen.animate(delay=1.0)
        else:
            os.system("clear" if os.name == "posix" else "cls")
            gen.display()


if __name__ == "__main__":
    main()
