import os
import sys
import cProfile
import pstats
import asyncio
import httpx
import uvicorn
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
import time

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

async def run_test_requests():
    await asyncio.sleep(2)  # Wait for server startup
    async with httpx.AsyncClient() as client:
        # Make test requests
        await client.get('http://localhost:8000/customers/')
        await client.get('http://localhost:8000/customers/ctoumieh')

    # Stop the server
    import signal
    import os
    os.kill(os.getpid(), signal.SIGTERM)

def run_server(app):
    uvicorn.run(app, host="0.0.0.0", port=8000)

def profile_customer_service():
    from services.customer.customer_service import app
    
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Start server in a separate thread
    server_thread = Thread(target=run_server, args=(app,))
    server_thread.daemon = True
    server_thread.start()
    
    # Run test requests
    asyncio.run(run_test_requests())
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.dump_stats('customer_profile.prof')
    stats.print_stats()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python profile_service.py [customer|inventory]")
        sys.exit(1)
        
    service = sys.argv[1]
    if service == "customer":
        profile_customer_service()