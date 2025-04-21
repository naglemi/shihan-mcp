#!/usr/bin/env python3
"""
Example of how to implement metric drift detection with Shihan MCP.

This script demonstrates how Shihan could compute QED/SA score medians across epochs
and alarm on regression (a future extension mentioned in shihan_creation.txt).
"""

import os
import json
import random
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Simulate training metrics over time
def generate_sample_metrics(num_epochs=50):
    """
    Generate sample training metrics.
    
    Args:
        num_epochs: Number of epochs to generate metrics for.
        
    Returns:
        A dictionary of metrics by epoch.
    """
    metrics = {}
    
    # Start date (10 days ago)
    start_date = datetime.now() - timedelta(days=10)
    
    # Base values
    qed_base = 0.65
    sa_base = 0.72
    loss_base = 0.5
    
    for epoch in range(1, num_epochs + 1):
        # Calculate date for this epoch
        epoch_date = start_date + timedelta(hours=epoch * 4)
        date_str = epoch_date.strftime("%Y-%m-%d %H:%M:%S")
        
        # Generate metrics with some randomness and trends
        if epoch < 30:
            # Improving trend
            qed = qed_base + (epoch * 0.005) + random.uniform(-0.02, 0.02)
            sa = sa_base + (epoch * 0.004) + random.uniform(-0.02, 0.02)
            loss = loss_base - (epoch * 0.01) + random.uniform(-0.02, 0.02)
        else:
            # Regression after epoch 30
            qed = qed_base + (30 * 0.005) - ((epoch - 30) * 0.01) + random.uniform(-0.02, 0.02)
            sa = sa_base + (30 * 0.004) - ((epoch - 30) * 0.008) + random.uniform(-0.02, 0.02)
            loss = loss_base - (30 * 0.01) + ((epoch - 30) * 0.02) + random.uniform(-0.02, 0.02)
        
        # Ensure values are in reasonable range
        qed = max(0.0, min(1.0, qed))
        sa = max(0.0, min(1.0, sa))
        loss = max(0.0, loss)
        
        # Store metrics
        metrics[epoch] = {
            "date": date_str,
            "qed_score": round(qed, 4),
            "sa_score": round(sa, 4),
            "loss": round(loss, 4)
        }
    
    return metrics

def detect_metric_drift(metrics, window_size=5, threshold=0.05):
    """
    Detect metric drift in the training metrics.
    
    Args:
        metrics: Dictionary of metrics by epoch.
        window_size: Size of the window to compute median over.
        threshold: Threshold for drift detection.
        
    Returns:
        A list of drift events.
    """
    drift_events = []
    
    # Get sorted epochs
    epochs = sorted(metrics.keys())
    
    if len(epochs) < window_size * 2:
        return drift_events
    
    # Compute moving medians
    for metric_name in ["qed_score", "sa_score", "loss"]:
        for i in range(window_size, len(epochs) - window_size + 1):
            # Current window
            current_window = [metrics[epochs[j]][metric_name] for j in range(i, i + window_size)]
            current_median = sorted(current_window)[len(current_window) // 2]
            
            # Previous window
            prev_window = [metrics[epochs[j]][metric_name] for j in range(i - window_size, i)]
            prev_median = sorted(prev_window)[len(prev_window) // 2]
            
            # Check for drift
            if metric_name in ["qed_score", "sa_score"]:
                # For these metrics, lower is worse
                if prev_median - current_median > threshold:
                    drift_events.append({
                        "epoch": epochs[i],
                        "metric": metric_name,
                        "prev_median": prev_median,
                        "current_median": current_median,
                        "drift": prev_median - current_median,
                        "date": metrics[epochs[i]]["date"]
                    })
            else:
                # For loss, higher is worse
                if current_median - prev_median > threshold:
                    drift_events.append({
                        "epoch": epochs[i],
                        "metric": metric_name,
                        "prev_median": prev_median,
                        "current_median": current_median,
                        "drift": current_median - prev_median,
                        "date": metrics[epochs[i]]["date"]
                    })
    
    return drift_events

def plot_metrics(metrics, drift_events=None):
    """
    Plot the metrics and mark drift events.
    
    Args:
        metrics: Dictionary of metrics by epoch.
        drift_events: List of drift events to mark on the plot.
    """
    epochs = sorted(metrics.keys())
    
    # Extract metrics
    dates = [metrics[epoch]["date"] for epoch in epochs]
    qed_scores = [metrics[epoch]["qed_score"] for epoch in epochs]
    sa_scores = [metrics[epoch]["sa_score"] for epoch in epochs]
    losses = [metrics[epoch]["loss"] for epoch in epochs]
    
    # Create figure
    plt.figure(figsize=(12, 8))
    
    # Plot QED scores
    plt.subplot(3, 1, 1)
    plt.plot(epochs, qed_scores, 'b-', label='QED Score')
    plt.title('QED Score by Epoch')
    plt.xlabel('Epoch')
    plt.ylabel('QED Score')
    plt.grid(True)
    
    # Mark drift events
    if drift_events:
        for event in drift_events:
            if event["metric"] == "qed_score":
                plt.axvline(x=event["epoch"], color='r', linestyle='--', alpha=0.5)
    
    # Plot SA scores
    plt.subplot(3, 1, 2)
    plt.plot(epochs, sa_scores, 'g-', label='SA Score')
    plt.title('SA Score by Epoch')
    plt.xlabel('Epoch')
    plt.ylabel('SA Score')
    plt.grid(True)
    
    # Mark drift events
    if drift_events:
        for event in drift_events:
            if event["metric"] == "sa_score":
                plt.axvline(x=event["epoch"], color='r', linestyle='--', alpha=0.5)
    
    # Plot losses
    plt.subplot(3, 1, 3)
    plt.plot(epochs, losses, 'r-', label='Loss')
    plt.title('Loss by Epoch')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.grid(True)
    
    # Mark drift events
    if drift_events:
        for event in drift_events:
            if event["metric"] == "loss":
                plt.axvline(x=event["epoch"], color='r', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    
    # Save the plot
    plt.savefig('metric_drift.png')
    print("Plot saved as metric_drift.png")

def main():
    """
    Main function to demonstrate metric drift detection.
    """
    print("📊 Shihan MCP Metric Drift Detection Example")
    
    # Generate sample metrics
    print("\n🔢 Generating sample training metrics...")
    metrics = generate_sample_metrics(num_epochs=50)
    
    # Save metrics to file
    with open('sample_metrics.json', 'w') as f:
        json.dump(metrics, f, indent=2)
    print("Sample metrics saved to sample_metrics.json")
    
    # Detect metric drift
    print("\n🔍 Detecting metric drift...")
    drift_events = detect_metric_drift(metrics, window_size=5, threshold=0.05)
    
    # Print drift events
    if drift_events:
        print(f"\n⚠️ Detected {len(drift_events)} drift events:")
        for event in drift_events:
            print(f"  - Epoch {event['epoch']}: {event['metric']} drifted by {event['drift']:.4f}")
            print(f"    Previous median: {event['prev_median']:.4f}, Current median: {event['current_median']:.4f}")
            print(f"    Date: {event['date']}")
    else:
        print("\n✅ No metric drift detected")
    
    # Plot metrics
    print("\n📈 Plotting metrics...")
    plot_metrics(metrics, drift_events)
    
    print("\n🏁 Example complete")
    print("\nIn a real implementation, Shihan would:")
    print("1. Extract metrics from training.log")
    print("2. Compute moving medians across epochs")
    print("3. Detect significant regressions")
    print("4. Page Hayato when drift exceeds thresholds")
    print("5. Optionally push metrics to Graphite/Grafana for long-term tracking")

if __name__ == "__main__":
    main()