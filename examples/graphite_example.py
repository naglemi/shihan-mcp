#!/usr/bin/env python3
"""
Example of how to implement Graphite/Grafana integration with Shihan MCP.

This script demonstrates how Shihan could push supervision metrics to Graphite
for long-term health tracking (a future extension mentioned in shihan_creation.txt).
"""

import time
import socket
import random
import argparse
from datetime import datetime, timedelta

class GraphiteClient:
    """
    Simple client for sending metrics to Graphite.
    """
    
    def __init__(self, host='localhost', port=2003, prefix='shihan'):
        """
        Initialize the Graphite client.
        
        Args:
            host: Graphite server host.
            port: Graphite server port.
            prefix: Prefix for all metrics.
        """
        self.host = host
        self.port = port
        self.prefix = prefix
    
    def send_metric(self, name, value, timestamp=None):
        """
        Send a metric to Graphite.
        
        Args:
            name: Metric name.
            value: Metric value.
            timestamp: Timestamp for the metric (default: current time).
        """
        if timestamp is None:
            timestamp = int(time.time())
        
        # Format the metric
        metric = f"{self.prefix}.{name} {value} {timestamp}\n"
        
        try:
            # Send the metric to Graphite
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host, self.port))
            sock.send(metric.encode('utf-8'))
            sock.close()
            
            print(f"Sent metric: {metric.strip()}")
            return True
            
        except Exception as e:
            print(f"Error sending metric to Graphite: {str(e)}")
            return False

def simulate_metrics(client, duration_minutes=10, interval_seconds=10):
    """
    Simulate sending metrics to Graphite.
    
    Args:
        client: GraphiteClient instance.
        duration_minutes: Duration to simulate metrics for.
        interval_seconds: Interval between metrics.
    """
    print(f"Simulating metrics for {duration_minutes} minutes with {interval_seconds} second intervals")
    
    # Calculate end time
    end_time = datetime.now() + timedelta(minutes=duration_minutes)
    
    # Counters for various events
    cycle_count = 0
    error_count = 0
    violation_count = 0
    
    # Simulate metrics
    while datetime.now() < end_time:
        # Current timestamp
        now = int(time.time())
        
        # Simulate cycle completion
        if random.random() < 0.2:  # 20% chance of cycle completion
            cycle_count += 1
            
            # Cycle duration (in seconds)
            cycle_duration = random.randint(60, 300)
            client.send_metric("cycles.count", cycle_count, now)
            client.send_metric("cycles.duration", cycle_duration, now)
            
            # Changes made in this cycle
            changes = random.randint(0, 5)
            client.send_metric("cycles.changes", changes, now)
        
        # Simulate log errors
        if random.random() < 0.1:  # 10% chance of log error
            error_count += 1
            client.send_metric("errors.count", error_count, now)
            
            # Error severity (1-3)
            severity = random.randint(1, 3)
            client.send_metric("errors.severity", severity, now)
        
        # Simulate creed violations
        if random.random() < 0.05:  # 5% chance of creed violation
            violation_count += 1
            client.send_metric("violations.count", violation_count, now)
        
        # Simulate QED score
        qed_score = 0.65 + random.uniform(-0.1, 0.1)
        client.send_metric("metrics.qed_score", round(qed_score, 4), now)
        
        # Simulate SA score
        sa_score = 0.72 + random.uniform(-0.1, 0.1)
        client.send_metric("metrics.sa_score", round(sa_score, 4), now)
        
        # Simulate loss
        loss = 0.3 + random.uniform(-0.1, 0.1)
        client.send_metric("metrics.loss", round(loss, 4), now)
        
        # Wait for the next interval
        time.sleep(interval_seconds)

def main():
    """
    Main function to demonstrate Graphite integration.
    """
    parser = argparse.ArgumentParser(description="Shihan MCP Graphite Integration Example")
    parser.add_argument("--host", default="localhost", help="Graphite server host")
    parser.add_argument("--port", type=int, default=2003, help="Graphite server port")
    parser.add_argument("--prefix", default="shihan", help="Metric prefix")
    parser.add_argument("--duration", type=int, default=10, help="Duration in minutes")
    parser.add_argument("--interval", type=int, default=10, help="Interval in seconds")
    args = parser.parse_args()
    
    print("📊 Shihan MCP Graphite Integration Example")
    
    # Create Graphite client
    client = GraphiteClient(host=args.host, port=args.port, prefix=args.prefix)
    
    # Simulate metrics
    try:
        simulate_metrics(client, args.duration, args.interval)
    except KeyboardInterrupt:
        print("\nSimulation stopped by user")
    
    print("\n🏁 Example complete")
    print("\nIn a real implementation, Shihan would:")
    print("1. Extract metrics from training.log and supervision results")
    print("2. Push metrics to Graphite at regular intervals")
    print("3. Use Grafana dashboards to visualize long-term trends")
    print("4. Set up alerts for significant metric changes")
    
    print("\nExample Grafana dashboard panels:")
    print("- Cycle Completion Rate (cycles per day)")
    print("- Average Cycle Duration")
    print("- Error Rate (errors per day)")
    print("- Creed Violation Rate (violations per day)")
    print("- QED/SA Score Trends")
    print("- Loss Trends")

if __name__ == "__main__":
    main()