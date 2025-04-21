#!/usr/bin/env python3
"""
Example of how to implement an SSE gateway with Shihan MCP.

This script demonstrates how Shihan could expose /events so remote dashboards
can subscribe to Shihan events (a future extension mentioned in shihan_creation.txt).
"""

import asyncio
import json
import subprocess
import time
import sys
import random
from datetime import datetime
from aiohttp import web

# Simulated events that Shihan might emit
EVENT_TYPES = [
    "log_error",
    "creed_violation",
    "plan_critique",
    "metric_drift",
    "cycle_complete"
]

# Sample event generators
def generate_log_error_event():
    """Generate a sample log error event."""
    errors = [
        "RuntimeError: CUDA out of memory",
        "AssertionError: Tensor dimension mismatch",
        "ValueError: Expected tensor to have shape (10, 5) but got (10, 10)",
        "KeyError: 'model_state' not found in checkpoint",
        "IndexError: Dimension out of range (expected to be in range of [-1, 0], but got 1)"
    ]
    return {
        "type": "log_error",
        "timestamp": datetime.now().isoformat(),
        "error": random.choice(errors),
        "file": "training.log",
        "severity": random.choice(["warning", "error", "critical"])
    }

def generate_creed_violation_event():
    """Generate a sample creed violation event."""
    violations = [
        "Using 'is None' check (forbidden by Creed)",
        "Using '**kwargs' (forbidden by Creed)",
        "Using mock objects (forbidden by Creed)",
        "Using None fallback pattern (forbidden by Creed)",
        "Using hasattr() (forbidden by Creed)"
    ]
    files = [
        "model.py",
        "trainer.py",
        "data_loader.py",
        "utils.py",
        "metrics.py"
    ]
    return {
        "type": "creed_violation",
        "timestamp": datetime.now().isoformat(),
        "violation": random.choice(violations),
        "file": random.choice(files),
        "line": random.randint(10, 500),
        "severity": "error"
    }

def generate_plan_critique_event():
    """Generate a sample plan critique event."""
    issues = [
        "Plan lacks specific test cases",
        "Multiple changes proposed at once",
        "Solution is overly complex",
        "Edge cases not considered",
        "No verification steps included"
    ]
    return {
        "type": "plan_critique",
        "timestamp": datetime.now().isoformat(),
        "scroll_path": f".scrolls/{datetime.now().strftime('%m-%d-%H%M')}-fix-plan.md",
        "score": random.randint(50, 95),
        "issues": random.sample(issues, k=random.randint(1, 3)),
        "severity": "warning" if random.random() > 0.5 else "info"
    }

def generate_metric_drift_event():
    """Generate a sample metric drift event."""
    metrics = ["qed_score", "sa_score", "loss"]
    metric = random.choice(metrics)
    prev_value = round(random.uniform(0.6, 0.8), 4)
    drift = round(random.uniform(0.05, 0.15), 4)
    
    # For loss, drift is positive (getting worse)
    # For other metrics, drift is negative (getting worse)
    if metric == "loss":
        current_value = round(prev_value + drift, 4)
    else:
        current_value = round(prev_value - drift, 4)
    
    return {
        "type": "metric_drift",
        "timestamp": datetime.now().isoformat(),
        "metric": metric,
        "prev_value": prev_value,
        "current_value": current_value,
        "drift": drift if metric == "loss" else -drift,
        "epoch": random.randint(30, 50),
        "severity": "warning"
    }

def generate_cycle_complete_event():
    """Generate a sample cycle complete event."""
    return {
        "type": "cycle_complete",
        "timestamp": datetime.now().isoformat(),
        "duration": f"{random.randint(5, 60)}m {random.randint(0, 59)}s",
        "changes_made": random.randint(0, 5),
        "issues_found": random.randint(0, 3),
        "severity": "info"
    }

# Event generator mapping
EVENT_GENERATORS = {
    "log_error": generate_log_error_event,
    "creed_violation": generate_creed_violation_event,
    "plan_critique": generate_plan_critique_event,
    "metric_drift": generate_metric_drift_event,
    "cycle_complete": generate_cycle_complete_event
}

# SSE Gateway implementation
class SSEGateway:
    """
    Server-Sent Events gateway for Shihan MCP.
    """
    
    def __init__(self):
        """Initialize the SSE gateway."""
        self.clients = set()
        self.app = web.Application()
        self.app.router.add_get('/', self.index_handler)
        self.app.router.add_get('/events', self.events_handler)
        self.app.router.add_get('/dashboard', self.dashboard_handler)
    
    async def index_handler(self, request):
        """Handle requests to the index page."""
        return web.Response(
            text="""
            <html>
                <head>
                    <title>Shihan MCP SSE Gateway</title>
                </head>
                <body>
                    <h1>Shihan MCP SSE Gateway</h1>
                    <p>This is a demonstration of the SSE gateway for Shihan MCP.</p>
                    <p>Visit <a href="/dashboard">the dashboard</a> to see events in real-time.</p>
                </body>
            </html>
            """,
            content_type='text/html'
        )
    
    async def dashboard_handler(self, request):
        """Handle requests to the dashboard page."""
        return web.Response(
            text="""
            <html>
                <head>
                    <title>Shihan MCP Dashboard</title>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
                        h1 { color: #333; }
                        #events { margin-top: 20px; }
                        .event { margin-bottom: 10px; padding: 10px; border-radius: 5px; }
                        .info { background-color: #e3f2fd; }
                        .warning { background-color: #fff9c4; }
                        .error, .critical { background-color: #ffebee; }
                        .event-time { font-size: 0.8em; color: #666; }
                        .event-type { font-weight: bold; }
                        .event-details { margin-top: 5px; }
                    </style>
                </head>
                <body>
                    <h1>Shihan MCP Dashboard</h1>
                    <p>Real-time events from Shihan MCP:</p>
                    <div id="events"></div>
                    
                    <script>
                        const eventsDiv = document.getElementById('events');
                        const eventSource = new EventSource('/events');
                        
                        eventSource.onmessage = function(event) {
                            const eventData = JSON.parse(event.data);
                            const eventDiv = document.createElement('div');
                            eventDiv.className = `event ${eventData.severity || 'info'}`;
                            
                            const eventTime = document.createElement('div');
                            eventTime.className = 'event-time';
                            eventTime.textContent = new Date(eventData.timestamp).toLocaleString();
                            
                            const eventType = document.createElement('div');
                            eventType.className = 'event-type';
                            eventType.textContent = eventData.type.replace(/_/g, ' ').toUpperCase();
                            
                            const eventDetails = document.createElement('div');
                            eventDetails.className = 'event-details';
                            eventDetails.textContent = JSON.stringify(eventData, null, 2);
                            
                            eventDiv.appendChild(eventTime);
                            eventDiv.appendChild(eventType);
                            eventDiv.appendChild(eventDetails);
                            
                            eventsDiv.insertBefore(eventDiv, eventsDiv.firstChild);
                        };
                        
                        eventSource.onerror = function() {
                            console.error('EventSource failed');
                        };
                    </script>
                </body>
            </html>
            """,
            content_type='text/html'
        )
    
    async def events_handler(self, request):
        """Handle SSE connections."""
        response = web.StreamResponse()
        response.headers['Content-Type'] = 'text/event-stream'
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['Connection'] = 'keep-alive'
        await response.prepare(request)
        
        # Register this client
        client_queue = asyncio.Queue()
        self.clients.add(client_queue)
        
        try:
            # Send initial message
            await response.write(
                f"data: {json.dumps({'type': 'connection_established', 'timestamp': datetime.now().isoformat()})}\n\n".encode('utf-8')
            )
            
            # Keep the connection open and send events
            while True:
                event = await client_queue.get()
                await response.write(f"data: {json.dumps(event)}\n\n".encode('utf-8'))
        
        finally:
            # Remove this client when the connection is closed
            self.clients.remove(client_queue)
        
        return response
    
    async def broadcast_event(self, event):
        """Broadcast an event to all connected clients."""
        for client_queue in self.clients:
            await client_queue.put(event)
    
    async def generate_random_events(self):
        """Generate random events for demonstration purposes."""
        while True:
            # Wait a random amount of time
            await asyncio.sleep(random.uniform(2, 5))
            
            # Generate a random event
            event_type = random.choice(EVENT_TYPES)
            event = EVENT_GENERATORS[event_type]()
            
            # Broadcast the event
            await self.broadcast_event(event)
            print(f"Broadcasted event: {event['type']}")
    
    async def start(self, host='localhost', port=8080):
        """Start the SSE gateway."""
        # Start the event generator
        asyncio.create_task(self.generate_random_events())
        
        # Start the web server
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        
        print(f"SSE Gateway running at http://{host}:{port}")
        print(f"Dashboard available at http://{host}:{port}/dashboard")
        
        # Keep the server running
        while True:
            await asyncio.sleep(3600)

async def main():
    """
    Main function to demonstrate the SSE gateway.
    """
    print("📡 Shihan MCP SSE Gateway Example")
    
    # Create and start the SSE gateway
    gateway = SSEGateway()
    await gateway.start()

if __name__ == "__main__":
    asyncio.run(main())