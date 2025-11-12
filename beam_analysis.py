import matplotlib.pyplot as plt
import numpy as np


def fixed_fixed_point_load(F, a, L):
    """
    Calculate moments and reactions for a fixed-fixed beam with a single point load.
    
    Parameters:
    F (float): Point load magnitude (positive downward).
    a (float): Distance from left support A to load point.
    L (float): Span length.
    
    Returns:
    dict: Contains M_A, M_B, M_F, R_A, R_B.
    
    Sign convention:
    - Loads: Downward positive for F.
    - Moments: Positive for sagging (bottom tension).
    """
    b = L - a
    M_A = -F * a * b**2 / L**2
    M_B = -F * a**2 * b / L**2
    M_F = 2 * F * a**2 * b**2 / L**3
    R_A = F * (3 * a + b) * b**2 / L**3
    R_B = F * (a + 3 * b) * a**2 / L**3
    return {
        'M_A': M_A,
        'M_B': M_B,
        'M_F': M_F,
        'R_A': R_A,
        'R_B': R_B
    }


def fixed_fixed_uniform_load(q, L):
    """
    Calculate moments and reactions for a fixed-fixed beam with uniform distributed load.
    
    Parameters:
    q (float): Uniform load intensity (positive downward).
    L (float): Span length.
    
    Returns:
    dict: Contains M_A, M_B, M_center, R_A.
    
    Sign convention: Same as above.
    """
    M_A = -q * L**2 / 12
    M_B = M_A
    M_center = q * L**2 / 24
    R_A = q * L / 2
    R_B = R_A
    return {
        'M_A': M_A,
        'M_B': M_B,
        'M_center': M_center,
        'R_A': R_A,
        'R_B': R_B  # Symmetric
    }


def pinned_pinned_point_load(F, a, L):
    """
    Calculate moments and reactions for a pinned-pinned beam with a single point load.
    
    Parameters:
    F (float): Point load magnitude (positive downward).
    a (float): Distance from left support A to load point.
    L (float): Span length.
    
    Returns:
    dict: Contains M_F, R_A, R_B.
    
    Sign convention: Same as above.
    """
    b = L - a
    M_F = F * a * b / L
    R_A = F * b / L
    R_B = F * a / L
    return {
        'M_F': M_F,
        'R_A': R_A,
        'R_B': R_B
    }


def pinned_pinned_uniform_load(q, L):
    """
    Calculate moments and reactions for a pinned-pinned beam with uniform distributed load.
    
    Parameters:
    q (float): Uniform load intensity (positive downward).
    L (float): Span length.
    
    Returns:
    dict: Contains M_center, R_A.
    
    Sign convention: Same as above.
    """
    M_center = q * L**2 / 8
    R_A = q * L / 2
    R_B = R_A
    return {
        'M_center': M_center,
        'R_A': R_A,
        'R_B': R_B  # Symmetric
    }


# Note: For two point loads, superposition can be used by calling the single point load function twice.
# Deflection formulas are commented in the reference but not implemented here as they require E and I.


def plot_fixed_fixed_point_bmd(F, a, L, save_path=None, num_points=100):
    """
    Plot the bending moment diagram (BMD) for a fixed-fixed beam with a single point load.
    
    Parameters:
    F (float): Point load magnitude (positive downward).
    a (float): Distance from left support A to load point.
    L (float): Span length.
    save_path (str, optional): Path to save the plot (e.g., 'bmd.png'). If None, displays the plot.
    num_points (int): Number of points to discretize the beam for plotting.
    
    Sign convention: Same as fixed_fixed_point_load.
    """
    # Get moments and reactions
    results = fixed_fixed_point_load(F, a, L)
    M_A = results['M_A']
    M_B = results['M_B']
    M_F = results['M_F']
    R_A = results['R_A']
    R_B = results['R_B']
    
    b = L - a
    
    # Generate x points
    x_left = np.linspace(0, a, num_points//2 + 1)
    x_right = np.linspace(a, L, num_points//2 + 1)
    x = np.concatenate([x_left[:-1], x_right])  # Avoid duplicating a
    
    # Compute M(x)
    M_left = M_A + R_A * x_left[:-1]  # For 0 <= x < a
    M_right = M_F + (R_A - F) * (x_right[1:] - a)
    M = np.concatenate([M_left, M_right])
    
    # At x=a, include M_F
    x_full = np.concatenate([x_left, x_right[1:]])
    M_full = np.concatenate([M_A + R_A * x_left, M_F + (R_A - F) * (x_right[1:] - a)])
    
    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(x_full, M_full, 'b-', linewidth=2, label='BMD')
    
    # Mark key points
    plt.plot(0, M_A, 'ro', markersize=8, label=f'M_A = {M_A:.2f}')
    plt.plot(a, M_F, 'go', markersize=8, label=f'M_F = {M_F:.2f}')
    plt.plot(L, M_B, 'ro', markersize=8, label=f'M_B = {M_B:.2f}')
    
    # Load position
    plt.axvline(x=a, color='k', linestyle='--', alpha=0.5, label=f'Load at x={a}')
    
    plt.xlabel('Distance x (m)')
    plt.ylabel('Bending Moment M (kN·m)')
    plt.title(f'Bending Moment Diagram: Fixed-Fixed Beam, F={F} kN at a={a} m, L={L} m')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.ylim(min(M_full) * 1.1, max(M_full) * 1.1)  # Adjust y-limits for visibility
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {save_path}")
    else:
        plt.show()
    
    # Optional: Return x and M for further use
    return x_full, M_full


def plot_fixed_fixed_superposed_bmd(F1, a1, F2, a2, L, save_path=None, num_points=200):
    """
    Plot individual and superposed bending moment diagrams for a fixed-fixed beam with two point loads.
    Uses superposition: Computes BMD for each load separately and sums them.
    
    Parameters:
    F1 (float): Magnitude of first point load (positive downward).
    a1 (float): Position of first load from left support A.
    F2 (float): Magnitude of second point load (positive downward).
    a2 (float): Position of second load from left support A.
    L (float): Span length.
    save_path (str, optional): Path to save the plot. If None, displays.
    num_points (int): Number of points for discretization (higher for smoother plots).
    
    Returns:
    tuple: (x_full, M_total, max_positive_M) where max_positive_M is the maximum sagging moment.
    
    Sign convention: Same as before.
    """
    # Generate common x grid
    x_full = np.linspace(0, L, num_points)
    
    # Compute BMD for first load
    results1 = fixed_fixed_point_load(F1, a1, L)
    M1 = np.where(x_full <= a1, 
                  results1['M_A'] + results1['R_A'] * x_full,
                  results1['M_F'] + (results1['R_A'] - F1) * (x_full - a1))
    
    # Compute BMD for second load
    results2 = fixed_fixed_point_load(F2, a2, L)
    M2 = np.where(x_full <= a2, 
                  results2['M_A'] + results2['R_A'] * x_full,
                  results2['M_F'] + (results2['R_A'] - F2) * (x_full - a2))
    
    # Superpose
    M_total = M1 + M2
    
    # Find max positive moment
    positive_M = M_total[M_total > 0]
    max_positive_M = np.max(positive_M) if len(positive_M) > 0 else 0
    
    # Plot
    plt.figure(figsize=(12, 8))
    plt.plot(x_full, M1, 'r--', linewidth=2, label=f'BMD Load 1 (F={F1} kN at x={a1} m)')
    plt.plot(x_full, M2, 'g--', linewidth=2, label=f'BMD Load 2 (F={F2} kN at x={a2} m)')
    plt.plot(x_full, M_total, 'b-', linewidth=3, label=f'Superposed BMD (Max +M = {max_positive_M:.2f} kN·m)')
    
    # Mark key points for total (ends and load positions)
    M_total_A = M_total[0]
    M_total_B = M_total[-1]
    M_total_at_a1 = M_total[np.argmin(np.abs(x_full - a1))]
    M_total_at_a2 = M_total[np.argmin(np.abs(x_full - a2))]
    plt.plot(0, M_total_A, 'ro', markersize=8, label=f'M_A total = {M_total_A:.2f}')
    plt.plot(a1, M_total_at_a1, 'go', markersize=8)
    plt.plot(a2, M_total_at_a2, 'mo', markersize=8)
    plt.plot(L, M_total_B, 'ro', markersize=8, label=f'M_B total = {M_total_B:.2f}')
    
    # Load positions
    plt.axvline(x=a1, color='r', linestyle=':', alpha=0.5)
    plt.axvline(x=a2, color='g', linestyle=':', alpha=0.5)
    
    plt.xlabel('Distance x (m)')
    plt.ylabel('Bending Moment M (kN·m)')
    plt.title(f'BMD Superposition: Fixed-Fixed Beam, Loads at {a1}m & {a2}m, L={L} m')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.ylim(min(M_total) * 1.1, max(M_total) * 1.1)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {save_path}")
    else:
        plt.show()
    
    return x_full, M_total, max_positive_M


def fixed_fixed_two_point_load(F, L):
    """
    Calculate moments and reactions for a fixed-fixed beam with two equal point loads F at L/3 and 2L/3.
    Uses superposition of two single point load cases.
    
    Parameters:
    F (float): Magnitude of each point load (positive downward).
    L (float): Span length.
    
    Returns:
    dict: Contains M_A, M_B (end moments, symmetric), M_pos_max (at center), R_A, R_B (symmetric).
    
    Sign convention: Positive moments sagging; ends hogging (negative).
    """
    a1 = L / 3
    a2 = 2 * L / 3
    
    # First load at a1 = L/3
    results1 = fixed_fixed_point_load(F, a1, L)
    M_A1 = results1['M_A']
    M_B1 = results1['M_B']
    R_A1 = results1['R_A']
    R_B1 = results1['R_B']
    
    # Second load at a2 = 2L/3 (symmetric to first from right)
    results2 = fixed_fixed_point_load(F, a2, L)
    M_A2 = results2['M_A']
    M_B2 = results2['M_B']
    R_A2 = results2['R_A']
    R_B2 = results2['R_B']
    
    # Superpose
    M_A = M_A1 + M_A2
    M_B = M_B1 + M_B2
    R_A = R_A1 + R_A2
    R_B = R_B1 + R_B2
    
    # Max positive moment at center (x = L/2) by superposition
    # For each single load, M(L/2) = FL/18 (as derived), so total 2*(FL/18) = FL/9
    # But compute numerically for consistency
    M_pos_max = (results1['M_F'] + (results1['R_A'] - F) * (L/2 - a1)) + \
                (results2['M_F'] + (results2['R_A'] - F) * (L/2 - a2))
    
    return {
        'M_A': M_A,
        'M_B': M_B,
        'M_pos_max': M_pos_max,
        'R_A': R_A,
        'R_B': R_B
    }


# Example usage (commented out):
# results = fixed_fixed_two_point_load(F=10, L=6)
# print(f"M_neg_max: {results['M_A']:.2f} kN·m")  # ≈ -13.33
# print(f"M_pos_max: {results['M_pos_max']:.2f} kN·m")  # ≈ 6.67 (FL/9 = 60/9 ≈6.67)

if __name__ == "__main__":
    # Example for 1/3 L and 2/3 L (uncomment to run):
    L = 6.0
    F = 10.0  # Same F for both
    a1 = L / 3
    a2 = 2 * L / 3
    x, M_tot, max_pos = plot_fixed_fixed_superposed_bmd(F, a1, F, a2, L, save_path='superposed_bmd.png')
    print(f"Maximum positive moment: {max_pos:.2f} kN·m")
