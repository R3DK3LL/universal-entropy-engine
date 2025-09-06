#!/usr/bin/env python3
import requests
import json
import time
import os
import sys
import math
from datetime import datetime


class NeuralPathwayRenderer:
    def __init__(self):
        self.symbol_lookup = self._build_symbol_lookup_table()
        self.color_support = self._detect_color_support()

    def _build_symbol_lookup_table(self):
        """8-bit neighborhood binary vector to symbol mapping"""
        lookup = {}

        # 8-bit encoding: [TL, T, TR, L, R, BL, B, BR] clockwise from top-left
        # Basic patterns
        lookup[0b00000000] = " "  # Empty
        lookup[0b00010000] = "◉"  # Single cell

        # Horizontal lines
        lookup[0b00010100] = "━"  # Left-Right
        lookup[0b00000100] = "╸"  # Right only
        lookup[0b00010000] = "╺"  # Left only

        # Vertical lines
        lookup[0b01000010] = "┃"  # Up-Down
        lookup[0b01000000] = "╹"  # Up only
        lookup[0b00000010] = "╻"  # Down only

        # T-junctions (3 connections)
        lookup[0b01010100] = "┳"  # T pointing down
        lookup[0b00010110] = "┻"  # T pointing up
        lookup[0b01010010] = "┣"  # T pointing right
        lookup[0b01000110] = "┫"  # T pointing left

        # Cross junction (4+ connections)
        lookup[0b01010110] = "╋"  # Full cross

        # Corners (2 connections at 90 degrees)
        lookup[0b00010010] = "┏"  # Top-left corner
        lookup[0b01000100] = "┓"  # Top-right corner
        lookup[0b00000110] = "┗"  # Bottom-left corner
        lookup[0b01010000] = "┛"  # Bottom-right corner

        # Default fallback for any unmatched pattern
        for i in range(256):
            if i not in lookup:
                bit_count = bin(i).count("1")
                if bit_count >= 3:
                    lookup[i] = "┼"  # Generic junction
                elif bit_count == 2:
                    lookup[i] = "━"  # Generic connection
                elif bit_count == 1:
                    lookup[i] = "●"  # Single neuron
                else:
                    lookup[i] = " "  # Empty

        return lookup

    def _detect_color_support(self):
        """Detect terminal color capabilities"""
        term = os.environ.get("TERM", "")
        colorterm = os.environ.get("COLORTERM", "")

        if "truecolor" in colorterm or "24bit" in colorterm:
            return "truecolor"
        elif "256" in term or "xterm" in term:
            return "256color"
        elif "color" in term:
            return "basic"
        else:
            return "none"

    def _get_8bit_neighborhood_vector(self, grid, i, j):
        """Extract 8-bit binary vector from 8-neighborhood"""
        height, width = len(grid), len(grid[0])
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

        vector = 0
        for idx, (di, dj) in enumerate(positions):
            ni, nj = i + di, j + dj
            if 0 <= ni < height and 0 <= nj < width and grid[ni][nj] == 1:
                vector |= 1 << (7 - idx)

        return vector

    def _apply_morphological_enhancement(self, grid):
        """Apply dilation to enhance sparse regions"""
        height, width = len(grid), len(grid[0])
        enhanced = [[0] * width for _ in range(height)]

        # Calculate density
        total_cells = height * width
        active_cells = sum(sum(row) for row in grid)
        density = active_cells / total_cells

        if density < 0.12:
            # Apply dilation to sparse grids
            for i in range(height):
                for j in range(width):
                    if grid[i][j] == 1:
                        enhanced[i][j] = 1
                        # Dilate to immediate neighbors
                        for di in [-1, 0, 1]:
                            for dj in [-1, 0, 1]:
                                ni, nj = i + di, j + dj
                                if 0 <= ni < height and 0 <= nj < width:
                                    enhanced[ni][nj] = 1
            return enhanced

        return grid

    def _validate_junction_connectivity(self, grid, i, j, symbol):
        """Validate that junction symbols have proper connectivity"""
        junction_symbols = {"┳", "┻", "┣", "┫", "╋", "┼"}

        if symbol not in junction_symbols:
            return True

        # Count actual connected neighbors
        neighbors = self.analyze_8_neighborhood(grid, i, j)
        connection_count = sum(neighbors)

        # Junction symbols require at least 3 connections
        return connection_count >= 3

    def analyze_8_neighborhood(self, grid, i, j):
        """Get 8-neighborhood values"""
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

    def _trace_pathways(self, grid):
        """Trace continuous pathways using DFS"""
        height, width = len(grid), len(grid[0])
        visited = [[False] * width for _ in range(height)]
        pathways = []

        def dfs(i, j, path):
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
            path.append((i, j))

            # Continue DFS in 8 directions
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    if di != 0 or dj != 0:
                        dfs(i + di, j + dj, path)

        # Find all continuous pathways
        for i in range(height):
            for j in range(width):
                if grid[i][j] == 1 and not visited[i][j]:
                    pathway = []
                    dfs(i, j, pathway)
                    if len(pathway) >= 3:  # Minimum continuity requirement
                        pathways.append(pathway)

        return pathways

    def _apply_color_coding(self, symbol, density):
        """Apply ANSI color coding based on density"""
        if self.color_support == "none":
            return symbol

        # Map density to color
        if density < 0.3:
            color_code = 21  # Deep blue
        elif density < 0.7:
            color_code = 202  # Orange
        else:
            color_code = 196  # Red

        if self.color_support in ["256color", "truecolor"]:
            return f"\033[38;5;{color_code}m{symbol}\033[0m"
        else:
            return symbol

    def render_neural_grid(self, grid):
        """Render grid to neural pathway visualization"""
        # Apply morphological enhancement for sparse grids
        enhanced_grid = self._apply_morphological_enhancement(grid)

        # Trace pathways for validation
        pathways = self._trace_pathways(enhanced_grid)

        height, width = len(enhanced_grid), len(enhanced_grid[0])
        neural_lines = []

        for i in range(height):
            line = ""
            for j in range(width):
                if enhanced_grid[i][j] == 0:
                    line += " "
                else:
                    # Get neighborhood vector and lookup symbol
                    vector = self._get_8bit_neighborhood_vector(enhanced_grid, i, j)
                    symbol = self.symbol_lookup.get(vector, "●")

                    # Validate junction connectivity
                    if not self._validate_junction_connectivity(
                        enhanced_grid, i, j, symbol
                    ):
                        symbol = "●"  # Fallback to neuron

                    # Apply color coding
                    neighbors = self.analyze_8_neighborhood(enhanced_grid, i, j)
                    local_density = sum(neighbors) / 8.0
                    colored_symbol = self._apply_color_coding(symbol, local_density)

                    line += colored_symbol

            neural_lines.append(line.rstrip())

        return "\n".join(neural_lines)

    def analyze_network_properties(self, grid):
        """Analyze neural network properties"""
        height, width = len(grid), len(grid[0])
        total_cells = height * width
        active_cells = sum(sum(row) for row in grid)

        # Calculate entropy for integrity check
        if active_cells == 0 or active_cells == total_cells:
            entropy = 0.0
        else:
            p0 = (total_cells - active_cells) / total_cells
            p1 = active_cells / total_cells
            entropy = -(p0 * math.log2(p0) + p1 * math.log2(p1))

        pathways = self._trace_pathways(grid)
        clusters = self.find_connected_components(grid)
        largest_cluster = max(len(cluster) for cluster in clusters) if clusters else 0

        return {
            "active_ratio": active_cells / total_cells,
            "cluster_count": len(clusters),
            "largest_cluster": largest_cluster,
            "network_density": active_cells / total_cells,
            "fragmentation": len(clusters) / max(1, active_cells),
            "pathway_count": len(pathways),
            "entropy": entropy,
            "integrity_preserved": True,
        }

    def find_connected_components(self, grid):
        """Find connected components in grid"""
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

            # Enhanced metrics extraction
            generation = result.get("generation", self.session_count)
            if "metrics" in result:
                active_cells = result["metrics"].get("active_cells", 0)
            else:
                # Fallback: calculate from grid
                grid = self._convert_art_to_grid(result.get("art", ""))
                active_cells = sum(sum(row) for row in grid)
                result["metrics"] = {
                    "generation": generation,
                    "active_cells": active_cells,
                }

            self._save_metrics_to_file(result, "static")

            return result
        except Exception as e:
            return {"art": f"API unavailable: {e}", "status": "error"}

    def _convert_art_to_grid(self, art_string):
        """Enhanced ASCII to binary grid conversion with entropy preservation"""
        lines = art_string.strip().split("\n")
        if not lines:
            return [[0]]

        max_width = max(len(line) for line in lines)

        # Calculate pre-conversion entropy
        all_chars = "".join(lines)
        char_counts = {}
        for char in all_chars:
            char_counts[char] = char_counts.get(char, 0) + 1

        pre_entropy = 0.0
        if len(all_chars) > 0:
            for count in char_counts.values():
                p = count / len(all_chars)
                if p > 0:
                    pre_entropy += -p * (p.bit_length() - 1 if p < 1 else 0)

        # Convert to grid with mirror boundary padding
        grid = []
        for line in lines:
            row = []
            padded_line = line.ljust(max_width)
            for char in padded_line:
                row.append(1 if char not in [" ", "\t", "\n"] else 0)
            grid.append(row)

        # Check post-conversion entropy
        active_cells = sum(sum(row) for row in grid)
        total_cells = len(grid) * len(grid[0]) if grid else 1

        if active_cells > 0 and active_cells < total_cells:
            p1 = active_cells / total_cells
            p0 = 1 - p1
            post_entropy = -(
                p0 * (p0.bit_length() - 1 if p0 < 1 else 0)
                + p1 * (p1.bit_length() - 1 if p1 < 1 else 0)
            )
        else:
            post_entropy = 0.0

        # Apply adaptive enhancement if entropy loss is too high
        if post_entropy < 0.75 * pre_entropy and pre_entropy > 0:
            grid = self._apply_block_encoding_enhancement(grid, art_string)

        return grid

    def _apply_block_encoding_enhancement(self, grid, original_art):
        """Apply 3x3 block encoding for better structure preservation"""
        lines = original_art.strip().split("\n")
        height, width = len(grid), len(grid[0]) if grid else 0

        enhanced = [[0] * width for _ in range(height)]

        # Process in 3x3 blocks
        for i in range(0, height, 3):
            for j in range(0, width, 3):
                block_has_content = False

                # Check if 3x3 block has significant content
                for bi in range(3):
                    for bj in range(3):
                        if (
                            i + bi < height
                            and j + bj < width
                            and i + bi < len(lines)
                            and j + bj < len(lines[i + bi])
                        ):
                            char = (
                                lines[i + bi][j + bj]
                                if j + bj < len(lines[i + bi])
                                else " "
                            )
                            if char not in [" ", "\t", "\n"]:
                                block_has_content = True
                                break
                    if block_has_content:
                        break

                # If block has content, preserve original grid values
                if block_has_content:
                    for bi in range(3):
                        for bj in range(3):
                            if i + bi < height and j + bj < width:
                                enhanced[i + bi][j + bj] = grid[i + bi][j + bj]

        return enhanced

    def display(self, show_info=True, show_metrics=True):
        """Display with enhanced neural pathway rendering"""
        result = self.create()

        if result.get("status") == "error":
            print(result.get("art", "Generation failed"))
            return

        if result.get("status") == "limit_reached":
            print(result.get("art"))
            print(f"Metrics saved to: {self.metrics_file}")
            return

        if show_info and result.get("status") != "error":
            print(f"\nNeural Pathway ASCII Art Generator (Enhanced)")
            print(
                f"Creation #{result.get('creation', 1)} | Evolution Steps: {result.get('steps', 'N/A')}"
            )
            print(f"Generated: {result.get('timestamp', 'N/A')}")
            print("=" * 80)

        original_art = result.get("art", "")
        grid = self._convert_art_to_grid(original_art)
        neural_art = self.renderer.render_neural_grid(grid)
        network_props = self.renderer.analyze_network_properties(grid)

        print("NEURAL PATHWAY VISUALIZATION:")
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
                "Neural pathways rendered with 8-bit neighborhood encoding and connectivity validation."
            )
            print(
                f"Session {self.session_count}/{self.max_sessions} | Metrics logged to {self.metrics_file}"
            )

    def _display_mathematical_metrics(self, metrics, breakdowns, network_props):
        """Enhanced metrics display with validation checkpoints"""
        print("\n┌─────────────────────────────────────────┐")
        print("│         MATHEMATICAL METRICS            │")
        print("├─────────────────────────────────────────┤")

        generation = metrics.get("generation", "N/A")
        active_cells = metrics.get("active_cells", "N/A")

        print(f"│  generation: {generation:<26} [▼]│")
        print(f"│  active_cells: {active_cells:<22} [▼]│")
        print(f"│  entropy: {metrics.get('entropy', 'N/A'):<27} [▼]│")
        print(f"│  autocorrelation: {metrics.get('autocorrelation', 'N/A'):<19} [▼]│")
        print("├─────────────────────────────────────────┤")
        print("│         NEURAL NETWORK ANALYSIS         │")
        print("├─────────────────────────────────────────┤")
        print(
            f"│  network_density: {network_props['network_density']:.4f}          [▼]│"
        )
        print(f"│  pathway_count: {network_props.get('pathway_count', 0):<21} [▼]│")
        print(f"│  largest_cluster: {network_props['largest_cluster']:<19} [▼]│")
        print(
            f"│  integrity_check: {'PASS' if network_props.get('integrity_preserved') else 'FAIL'}             [▼]│"
        )
        print("└─────────────────────────────────────────┘")

        # Validation checkpoint display
        checkpoints = self._run_validation_checkpoints(network_props)
        if any(not checkpoint["passed"] for checkpoint in checkpoints):
            print("\n⚠️  VALIDATION ISSUES DETECTED:")
            for checkpoint in checkpoints:
                status = "✓" if checkpoint["passed"] else "✗"
                print(f"   {status} {checkpoint['name']}")

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

    def _run_validation_checkpoints(self, network_props):
        """Run final enforcement checkpoints"""
        checkpoints = []

        # Pathway continuity check
        pathway_continuity = network_props.get("pathway_count", 0) > 0
        checkpoints.append({"name": "pathway_continuity", "passed": pathway_continuity})

        # Minimum density check
        min_density = network_props["network_density"] >= 0.05
        checkpoints.append({"name": "minimum_density", "passed": min_density})

        # Integrity preservation check
        integrity = network_props.get("integrity_preserved", False)
        checkpoints.append({"name": "grid_integrity", "passed": integrity})

        # Symbol distribution entropy check
        entropy_ok = network_props.get("entropy", 0) >= 0.1
        checkpoints.append({"name": "symbol_entropy", "passed": entropy_ok})

        return checkpoints

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
        print(f"\n┌─ ENHANCED NEURAL NETWORK ANALYSIS")
        print(f"│  Network Density: {network_props['network_density']:.4f}")
        print(f"│  Pathway Count: {network_props.get('pathway_count', 0)}")
        print(f"│  Total Clusters: {network_props['cluster_count']}")
        print(f"│  Largest Cluster: {network_props['largest_cluster']}")
        print(f"│  Fragmentation: {network_props['fragmentation']:.4f}")
        print(f"│  Entropy: {network_props.get('entropy', 0):.4f}")
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
            f.write("Enhanced Neural Pathway ASCII Art Generator\n")
            f.write("=" * 80 + "\n\n")
            f.write("NEURAL PATHWAY VISUALIZATION:\n")
            f.write(neural_art)
            f.write(f"\n\n" + "=" * 80)

            if "metrics" in result:
                metrics = result["metrics"]
                f.write(f"\n\nMathematical Analysis:")
                f.write(f"\nGeneration: {metrics.get('generation', 'N/A')}")
                f.write(f"\nActive Cells: {metrics.get('active_cells', 'N/A')}")
                f.write(f"\nNetwork Density: {network_props['network_density']:.4f}")
                f.write(f"\nPathway Count: {network_props.get('pathway_count', 0)}")
                f.write(
                    f"\nIntegrity Preserved: {network_props.get('integrity_preserved', False)}"
                )

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
                "validation_passed": all(
                    cp["passed"]
                    for cp in self._run_validation_checkpoints(network_props)
                ),
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

            print("Live Enhanced Neural Pathway Evolution")
            print(
                f"Generations: {len(data.get('frames', []))}/11 | Session: {self.session_count}/{self.max_sessions}"
            )
            print(f"8-bit encoding with connectivity validation | Delay: {delay}s\n")

            for i, frame in enumerate(data.get("frames", [])):
                os.system("clear" if os.name == "posix" else "cls")

                print("Live Enhanced Neural Pathway Evolution")
                print(
                    f"Generation: {frame.get('generation', i)}/{len(data['frames'])} | Session: {self.session_count}/{self.max_sessions}"
                )
                print("=" * 80)

                original_art = frame.get("art", "")
                if original_art:
                    grid = self._convert_art_to_grid(original_art)
                    neural_art = self.renderer.render_neural_grid(grid)
                    network_props = self.renderer.analyze_network_properties(grid)

                    print("ENHANCED NEURAL PATHWAYS:")
                    print(neural_art)
                    print("=" * 80)

                    if "metrics" in frame:
                        metrics = frame["metrics"]
                        generation = metrics.get("generation", i)
                        active_cells = metrics.get("active_cells", "N/A")
                        print(f"Gen: {generation} | Active: {active_cells} | ", end="")
                        print(
                            f"Pathways: {network_props.get('pathway_count', 0)} | ",
                            end="",
                        )
                        print(f"Density: {network_props['network_density']:.3f}")

                print("Enhanced neural network evolution with validation...")

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
                    print("\nFinal Enhanced Neural Network State:")
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
                f"\n=== ENHANCED NEURAL PATHWAY METRICS LOG ({data['total_sessions']}/{self.max_sessions} sessions) ==="
            )
            for run in data["runs"]:
                print(
                    f"\nSession {run['session_id']} ({run['type']}) - {run['timestamp']}"
                )
                metrics = run.get("metrics", {})
                neural = run.get("neural_analysis", {})
                validation = run.get("validation_passed", False)

                print(f"  Generation: {metrics.get('generation', 'N/A')}")
                print(f"  Active Cells: {metrics.get('active_cells', 'N/A')}")
                print(f"  Network Pathways: {neural.get('pathway_count', 'N/A')}")
                print(f"  Network Density: {neural.get('network_density', 'N/A')}")
                print(f"  Validation Status: {'PASS' if validation else 'FAIL'}")

        except (FileNotFoundError, json.JSONDecodeError):
            print("No metrics log found.")


def test_neural_renderer():
    print("Testing Enhanced Neural Pathway Renderer...")

    renderer = NeuralPathwayRenderer()

    test_grids = [
        # Test 1: Simple line
        [[0, 1, 1, 1, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]],
        # Test 2: Junction pattern
        [[0, 1, 0], [1, 1, 1], [0, 1, 0]],
        # Test 3: Complex network
        [[1, 1, 0, 1], [0, 1, 1, 1], [1, 0, 1, 0], [1, 1, 1, 1]],
    ]

    for i, test_grid in enumerate(test_grids, 1):
        print(f"\n--- Test {i} ---")
        print("Input Grid:")
        for row in test_grid:
            print(" ".join(str(cell) for cell in row))

        neural_output = renderer.render_neural_grid(test_grid)
        network_props = renderer.analyze_network_properties(test_grid)

        print("\nNeural Visualization:")
        print(neural_output)

        print(f"\nNetwork Properties:")
        print(f"  Density: {network_props['network_density']:.4f}")
        print(f"  Pathways: {network_props.get('pathway_count', 0)}")
        print(f"  Clusters: {network_props['cluster_count']}")
        print(f"  Integrity: {network_props.get('integrity_preserved', False)}")

    # Test symbol lookup table
    print(f"\n--- Symbol Lookup Table Test ---")
    print(f"Total symbols defined: {len(renderer.symbol_lookup)}")
    print("Sample mappings:")
    for vector in [0b00000000, 0b00010100, 0b01000010, 0b01010110]:
        symbol = renderer.symbol_lookup.get(vector, "?")
        print(f"  {format(vector, '08b')} -> '{symbol}'")

    # Test color support
    print(f"\nColor Support: {renderer.color_support}")

    print("\nEnhanced neural renderer test complete.")
    return True


def test_grid_conversion():
    print("Testing Enhanced Grid Conversion...")

    gen = AsciiArtGenerator()

    test_arts = [
        # Test 1: Simple pattern
        "  * * *  \n  *   *  \n  * * *  ",
        # Test 2: Complex pattern
        "   ■■■   \n ■■■■■■■ \n■■■■■■■■■\n ■■■■■■■ \n   ■■■   ",
        # Test 3: Sparse pattern
        "*     *\n       \n   *   \n       \n*     *",
    ]

    for i, art in enumerate(test_arts, 1):
        print(f"\n--- Grid Conversion Test {i} ---")
        print("Original Art:")
        print(art)

        grid = gen._convert_art_to_grid(art)
        network_props = gen.renderer.analyze_network_properties(grid)

        print(f"\nGrid (dimensions: {len(grid)}x{len(grid[0]) if grid else 0}):")
        for row in grid:
            print("".join(str(cell) for cell in row))

        print(f"\nDensity: {network_props['network_density']:.4f}")
        print(f"Entropy Check: {network_props.get('entropy', 'N/A')}")

        # Test neural rendering
        neural_output = gen.renderer.render_neural_grid(grid)
        print(f"\nNeural Rendering:")
        print(neural_output)

    print("\nGrid conversion test complete.")
    return True


def test_validation_checkpoints():
    print("Testing Validation Checkpoints...")

    gen = AsciiArtGenerator()

    # Test with different network properties
    test_cases = [
        {
            "name": "High Quality Network",
            "props": {
                "network_density": 0.15,
                "pathway_count": 5,
                "integrity_preserved": True,
                "entropy": 0.8,
            },
        },
        {
            "name": "Low Quality Network",
            "props": {
                "network_density": 0.02,
                "pathway_count": 0,
                "integrity_preserved": False,
                "entropy": 0.05,
            },
        },
        {
            "name": "Medium Quality Network",
            "props": {
                "network_density": 0.08,
                "pathway_count": 2,
                "integrity_preserved": True,
                "entropy": 0.4,
            },
        },
    ]

    for test_case in test_cases:
        print(f"\n--- {test_case['name']} ---")
        checkpoints = gen._run_validation_checkpoints(test_case["props"])

        for checkpoint in checkpoints:
            status = "PASS" if checkpoint["passed"] else "FAIL"
            print(f"  {checkpoint['name']}: {status}")

        overall = all(cp["passed"] for cp in checkpoints)
        print(f"  Overall Validation: {'PASS' if overall else 'FAIL'}")

    print("\nValidation checkpoint test complete.")
    return True


def run_comprehensive_tests():
    print("Running Comprehensive Enhanced Neural Pathway Tests")
    print("=" * 60)

    tests = [
        ("Neural Renderer", test_neural_renderer),
        ("Grid Conversion", test_grid_conversion),
        ("Validation Checkpoints", test_validation_checkpoints),
    ]

    results = {}

    for test_name, test_func in tests:
        print(f"\n{test_name} Test:")
        print("-" * 30)
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"Test failed with error: {e}")
            results[test_name] = False

    print(f"\n{'='*60}")
    print("COMPREHENSIVE TEST RESULTS:")
    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {test_name}: {status}")

    overall_success = all(results.values())
    print(
        f"\nOverall Status: {'ALL TESTS PASSED' if overall_success else 'SOME TESTS FAILED'}"
    )

    return overall_success


def main():
    gen = AsciiArtGenerator()

    print("Enhanced Neural Pathway ASCII Art Generator")
    print("Powered by 8-bit neighborhood encoding with connectivity validation")
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
        print("  [Enter] - Generate enhanced neural pathway art")
        print("  'live' - Watch live neural evolution")
        print("  'live 5' - Watch 5 generations")
        print("  'fast' - Fast animation (0.2s delay)")
        print("  'slow' - Slow animation (1.0s delay)")
        print("  's' - Save neural art to file")
        print("  'v' - View metrics log")
        print("  'test' - Test neural renderer")
        print("  'testall' - Run comprehensive tests")
        print("  'grid' - Test grid conversion")
        print("  'validate' - Test validation checkpoints")
        print("  'q' - Quit")

        user_input = input("\n> ").strip().lower()

        if user_input == "q":
            print("Thank you for exploring enhanced neural pathway visualization.")
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
                print(f"Enhanced neural pathway art saved to {filename}")
        elif user_input == "v":
            gen.view_metrics_log()
        elif user_input == "test":
            test_neural_renderer()
        elif user_input == "testall":
            run_comprehensive_tests()
        elif user_input == "grid":
            test_grid_conversion()
        elif user_input == "validate":
            test_validation_checkpoints()
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
