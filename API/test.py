import asyncio
import websockets
import json
import cv2
import numpy as np
import time
import os
from typing import Dict, List, Any

# --- Configuration ---
# Match this with SESSION_TIMEOUT_MINUTES in your server's stream_manager.py
SERVER_TIMEOUT_MINUTES = 5
SERVER_TIMEOUT_SECONDS = SERVER_TIMEOUT_MINUTES * 60
# Add a buffer for network latency/processing time
TIMEOUT_TEST_WAIT_SECONDS = SERVER_TIMEOUT_SECONDS + 15 # Wait slightly longer than server timeout

# Expected close code when server rejects due to existing session
REJECT_EXISTING_SESSION_CODE = 1011 # Default for FastAPI/Starlette internal errors, or use your custom code if set
# Expected close code when server closes due to inactivity timeout
INACTIVITY_TIMEOUT_CLOSE_CODE = 1000 # Normal closure initiated by server

class WebSocketTester:
    def __init__(self, uri: str = "ws://localhost:8000/ws/stream", image_path: str = "./Data/test-img.jpg"):
        self.uri = uri
        self.test_img_bytes = self._load_test_image(image_path)
        # Store results per test for clarity
        self.test_results: Dict[str, List[Dict[str, Any]]] = {}
        self.overall_summary = {"passed": 0, "failed": 0}
        print(f"Tester configured for URI: {self.uri}")
        print(f"Expecting server timeout after {SERVER_TIMEOUT_MINUTES} minutes.")

    def _load_test_image(self, path: str) -> bytes:
        """Loads an image file and encodes it as jpg bytes."""
        if not os.path.exists(path):
             # Try a relative path from the script location as a fallback
            script_dir = os.path.dirname(__file__)
            alt_path = os.path.join(script_dir, path)
            if not os.path.exists(alt_path):
                 raise FileNotFoundError(f"Test image not found at '{path}' or '{alt_path}'")
            path = alt_path

        img = cv2.imread(path)
        if img is None:
            raise ValueError(f"Failed to load image from {path} using OpenCV")
        is_success, img_encoded = cv2.imencode('.jpg', img)
        if not is_success:
             raise ValueError(f"Failed to encode image from {path} to JPG format")
        print(f"Test image loaded successfully from: {path}")
        return img_encoded.tobytes()

    def _record_result(self, test_name: str, result: Dict[str, Any]):
        """Adds a result to the specific test's list."""
        if test_name not in self.test_results:
            self.test_results[test_name] = []
        self.test_results[test_name].append(result)

    def _start_test(self, test_name: str):
        """Prints the start of a test and clears previous results for it."""
        print(f"\n--- Starting Test: {test_name} ---")
        self.test_results[test_name] = [] # Clear results for this specific test

    def _finish_test(self, test_name: str, success: bool):
        """Prints the end of a test and updates the overall summary."""
        status = "PASSED" if success else "FAILED"
        print(f"--- Finished Test: {test_name} [{status}] ---")
        if success:
            self.overall_summary["passed"] += 1
        else:
            self.overall_summary["failed"] += 1
        # Optionally print results summary for the test
        if self.test_results.get(test_name):
             print(f"Results recorded for {test_name}: {len(self.test_results[test_name])} entries")


    async def _send_receive_one(self, websocket: websockets.WebSocketClientProtocol, test_name: str) -> Dict | None:
        """Sends one image and waits for one JSON response."""
        try:
            start_send_time = time.perf_counter()
            await websocket.send(self.test_img_bytes)
            send_duration = (time.perf_counter() - start_send_time) * 1000

            start_recv_time = time.perf_counter()
            response_raw = await asyncio.wait_for(websocket.recv(), timeout=15) # 15 sec timeout for response
            recv_latency = (time.perf_counter() - start_recv_time) * 1000

            response_data = json.loads(response_raw)
            result = {
                "status": "success",
                "send_duration_ms": round(send_duration, 2),
                "recv_latency_ms": round(recv_latency, 2),
                "response": response_data
            }
            self._record_result(test_name, result)
            return result
        except websockets.exceptions.ConnectionClosed as e:
             error_result = {"status": "error", "error_type": "ConnectionClosed", "code": e.code, "reason": e.reason, "message": f"Connection closed unexpectedly during send/receive: {e}"}
             self._record_result(test_name, error_result)
             print(f"ERROR in {test_name}: {error_result['message']}")
             return None
        except asyncio.TimeoutError:
            error_result = {"status": "error", "error_type": "TimeoutError", "message": "Timeout waiting for server response"}
            self._record_result(test_name, error_result)
            print(f"ERROR in {test_name}: {error_result['message']}")
            return None
        except json.JSONDecodeError:
             error_result = {"status": "error", "error_type": "JSONDecodeError", "message": "Server sent non-JSON response"}
             self._record_result(test_name, error_result)
             print(f"ERROR in {test_name}: {error_result['message']}")
             return None
        except Exception as e:
            error_result = {"status": "error", "error_type": type(e).__name__, "message": f"Unexpected error during send/receive: {e}"}
            self._record_result(test_name, error_result)
            print(f"ERROR in {test_name}: {error_result['message']}")
            return None

    async def test_single_connection(self):
        """Test: Basic connection and single message exchange."""
        test_name = "Single Connection"
        self._start_test(test_name)
        success = False
        try:
            async with websockets.connect(self.uri) as ws:
                result = await self._send_receive_one(ws, test_name)
                if result and result.get("status") == "success":
                    print("Single message exchange successful.")
                    # Add specific checks here if needed, e.g., check response content
                    if result['response'].get('status') == 'prediction_result':
                         print("Server returned prediction result.")
                         success = True
                    else:
                         print(f"Server returned unexpected status: {result['response'].get('status')}")
        except websockets.exceptions.InvalidStatusCode as e:
             # Handle connection failures (e.g., server not running)
             self._record_result(test_name, {"status": "error", "error_type": "ConnectionFailed", "code": e.status_code, "message": f"Failed to connect: {e}"})
             print(f"ERROR: Could not connect to server at {self.uri}. Status code: {e.status_code}")
        except Exception as e:
            self._record_result(test_name, {"status": "error", "error_type": type(e).__name__, "message": f"Test failed: {e}"})
            print(f"ERROR during single connection test: {e}")
        finally:
            self._finish_test(test_name, success)


    async def test_rapid_fire(self, count=20):
        """Test: Sending many messages quickly on one connection."""
        test_name = f"Rapid Fire ({count} messages)"
        self._start_test(test_name)
        success = False
        messages_ok = 0
        total_latency = 0
        try:
            async with websockets.connect(self.uri) as ws:
                start_time = time.perf_counter()
                for i in range(count):
                    result = await self._send_receive_one(ws, test_name)
                    if result and result.get("status") == "success":
                        messages_ok += 1
                        total_latency += result.get("recv_latency_ms", 0)
                        print(f"Sent/Received message {i+1}/{count}", end='\r')
                    else:
                        print(f"\nError during rapid fire at message {i+1}. Stopping.")
                        break # Stop test on first error

                total_time = time.perf_counter() - start_time
                print(f"\nCompleted {messages_ok}/{count} messages.")
                if messages_ok > 0:
                    print(f"Average latency: {total_latency / messages_ok:.2f}ms")
                    print(f"Total time: {total_time:.2f} seconds")
                if messages_ok == count:
                     success = True # Consider successful only if all messages pass
        except Exception as e:
            self._record_result(test_name, {"status": "error", "error_type": type(e).__name__, "message": f"Test failed: {e}"})
            print(f"\nERROR during rapid fire test setup or connection: {e}")
        finally:
            self._finish_test(test_name, success)


    async def test_inactivity_timeout(self):
        """Test: Verify server closes connection after inactivity."""
        test_name = "Inactivity Timeout"
        self._start_test(test_name)
        success = False
        try:
            async with websockets.connect(self.uri) as ws:
                # Send one message to establish session and start timer on server
                initial_result = await self._send_receive_one(ws, test_name)
                if not (initial_result and initial_result.get("status") == "success"):
                     print("ERROR: Could not send initial message for timeout test.")
                     self._finish_test(test_name, success)
                     return

                print(f"Connection established. Waiting for server timeout (~{SERVER_TIMEOUT_MINUTES} mins)...")
                # Now, wait longer than the server's timeout period expecting a close
                try:
                    # This will block until the server sends something OR closes the connection
                    unexpected_msg = await asyncio.wait_for(ws.recv(), timeout=TIMEOUT_TEST_WAIT_SECONDS)
                    # If we receive something, it's unexpected (unless server sends keepalives, unlikely here)
                    error_msg = f"Received unexpected message before timeout: {unexpected_msg}"
                    self._record_result(test_name, {"status": "error", "error_type": "UnexpectedMessage", "message": error_msg})
                    print(f"ERROR: {error_msg}")

                except asyncio.TimeoutError:
                    # This means ws.recv() timed out *before* the server closed the connection. Test Failed.
                    error_msg = f"Client timeout reached ({TIMEOUT_TEST_WAIT_SECONDS}s) before server closed connection."
                    self._record_result(test_name, {"status": "error", "error_type": "ClientTimeout", "message": error_msg})
                    print(f"ERROR: {error_msg}")

                except websockets.exceptions.ConnectionClosed as e:
                    # This is the EXPECTED outcome
                    print(f"Connection closed by server as expected. Code: {e.code}, Reason: '{e.reason}'")
                    self._record_result(test_name, {"status": "success", "code": e.code, "reason": e.reason})
                    # Verify the close code (optional but good)
                    if e.code == INACTIVITY_TIMEOUT_CLOSE_CODE:
                        print("SUCCESS: Server closed connection with the expected timeout code.")
                        success = True
                    else:
                        print(f"WARNING: Server closed connection, but code {e.code} != expected {INACTIVITY_TIMEOUT_CLOSE_CODE}.")
                        success = True # Still counts as success because it closed, but log warning

        except Exception as e:
            self._record_result(test_name, {"status": "error", "error_type": type(e).__name__, "message": f"Test failed: {e}"})
            print(f"ERROR during inactivity timeout test: {e}")
        finally:
            # Ensure ws is closed if test failed mid-way without entering 'except ConnectionClosed'
            # (The async with should handle this, but being explicit doesn't hurt if needed)
            self._finish_test(test_name, success)


    async def test_invalid_data(self):
        """Test: Sending non-image text data, expecting error response."""
        test_name = "Invalid Data"
        self._start_test(test_name)
        success = False
        try:
            async with websockets.connect(self.uri) as ws:
                invalid_payload = b"this is definitely not a valid image"
                await ws.send(invalid_payload)
                print("Sent invalid data payload.")

                # Expecting an error response from the server
                response_raw = await asyncio.wait_for(ws.recv(), timeout=10)
                response_data = json.loads(response_raw)
                print(f"Server response: {response_data}")

                if response_data.get("status") == "error":
                    print("SUCCESS: Server correctly responded with an error status.")
                    self._record_result(test_name, {"status": "success", "response": response_data})
                    success = True
                else:
                    msg = f"Server responded with status '{response_data.get('status')}', expected 'error'."
                    self._record_result(test_name, {"status": "error", "error_type": "UnexpectedResponse", "message": msg, "response": response_data})
                    print(f"ERROR: {msg}")

        except json.JSONDecodeError:
             msg = "Server sent non-JSON response to invalid data."
             self._record_result(test_name, {"status": "error", "error_type": "JSONDecodeError", "message": msg})
             print(f"ERROR: {msg}")
        except websockets.exceptions.ConnectionClosed as e:
             msg = f"Server closed connection unexpectedly after receiving invalid data. Code: {e.code}"
             self._record_result(test_name, {"status": "error", "error_type": "ConnectionClosed", "message": msg})
             print(f"ERROR: {msg}")
        except Exception as e:
            self._record_result(test_name, {"status": "error", "error_type": type(e).__name__, "message": f"Test failed: {e}"})
            print(f"ERROR during invalid data test: {e}")
        finally:
            self._finish_test(test_name, success)


    async def test_concurrent_connections(self, count=3):
        """Test: Multiple simultaneous connection attempts, expecting only one success."""
        test_name = f"Concurrent Connections ({count} attempts)"
        self._start_test(test_name)
        success = False # Test success means exactly 1 connection works, others rejected correctly

        async def single_client_attempt(client_id: int):
            """Tries to connect, send/recv once, reports outcome."""
            try:
                # Shorten timeout for connection attempt itself
                async with asyncio.wait_for(websockets.connect(self.uri), timeout=5) as ws:
                    # If connect succeeds, try one message
                    result = await self._send_receive_one(ws, test_name + f"_client_{client_id}")
                    if result and result.get("status") == "success":
                        return {"id": client_id, "status": "connected"}
                    else:
                         # Connection ok, but message failed?
                         return {"id": client_id, "status": "message_fail", "details": result}
            except websockets.exceptions.ConnectionClosed as e:
                 # Connection actively rejected by server
                 return {"id": client_id, "status": "rejected", "code": e.code, "reason": e.reason}
            except asyncio.TimeoutError:
                 return {"id": client_id, "status": "timeout", "details": "Timeout during connection attempt"}
            except websockets.exceptions.InvalidStatusCode as e:
                  return {"id": client_id, "status": "connect_fail", "code": e.status_code, "details": f"HTTP {e.status_code} during handshake"}
            except Exception as e:
                return {"id": client_id, "status": "error", "details": str(e)}

        tasks = [single_client_attempt(i) for i in range(count)]
        results = await asyncio.gather(*tasks)

        # Analyze results
        connected_clients = [r for r in results if r.get("status") == "connected"]
        rejected_clients = [r for r in results if r.get("status") == "rejected"]
        failed_clients = [r for r in results if r.get("status") not in ["connected", "rejected"]]

        print("\nConcurrent Connection Results:")
        for r in results: print(f"  Client {r['id']}: {r['status']} {r.get('details', '')} {r.get('code', '')} {r.get('reason', '')}")

        num_connected = len(connected_clients)
        num_rejected = len(rejected_clients)
        num_failed = len(failed_clients)

        # Define success criteria: Exactly 1 connected, count-1 rejected
        if num_connected == 1 and num_rejected == count - 1 and num_failed == 0:
            print(f"SUCCESS: Exactly 1 client connected, {num_rejected} rejected as expected.")
            success = True
            # Optional: Check rejection code/reason for rejected clients
            for r in rejected_clients:
                 if r.get("code") != REJECT_EXISTING_SESSION_CODE:
                      print(f"  WARNING: Client {r['id']} rejected with code {r.get('code')}, expected {REJECT_EXISTING_SESSION_CODE}")
        else:
            print(f"FAILURE: Expected 1 connection and {count-1} rejections.")
            print(f"  Got: Connected={num_connected}, Rejected={num_rejected}, Failed={num_failed}")

        self._finish_test(test_name, success)

    async def test_connection_stress(self, cycles=10):
        """Test: Rapid connect/send/disconnect cycles."""
        test_name = f"Connection Stress ({cycles} cycles)"
        self._start_test(test_name)
        success_cycles = 0
        for i in range(cycles):
            cycle_ok = False
            try:
                async with websockets.connect(self.uri) as ws:
                    result = await self._send_receive_one(ws, test_name + f"_cycle_{i+1}")
                    if result and result.get("status") == "success":
                        cycle_ok = True
                # The 'async with' block handles disconnect implicitly here
                if cycle_ok:
                     success_cycles += 1
                     print(f"Cycle {i+1}/{cycles}: Success", end='\r')
                else:
                     print(f"\nCycle {i+1}/{cycles}: Failed - Message exchange error")
                     # Optional: stop on first failure?
            except websockets.exceptions.ConnectionClosed as e:
                 # Might happen if server rejects immediately (e.g., previous session didn't clean up fast enough)
                 print(f"\nCycle {i+1}/{cycles}: Failed - Connection rejected/closed prematurely. Code: {e.code}")
                 self._record_result(test_name, {"status": "error", "cycle": i+1, "error_type": "ConnectionClosed", "code": e.code, "reason": e.reason})
            except Exception as e:
                print(f"\nCycle {i+1}/{cycles}: Failed - Unexpected error: {e}")
                self._record_result(test_name, {"status": "error", "cycle": i+1, "error_type": type(e).__name__, "message": str(e)})
            await asyncio.sleep(0.1) # Small delay between cycles

        print(f"\nCompleted {success_cycles}/{cycles} stress cycles successfully.")
        self._finish_test(test_name, success_cycles == cycles)


    async def run_all_tests(self, include_timeout_test=False):
        """Runs the selected test suite."""
        print("\n=========================")
        print(" Starting WebSocket Test Suite")
        print("=========================")
        suite_start_time = time.perf_counter()

        # --- Run Tests ---
        await self.test_single_connection()
        await self.test_rapid_fire(count=50) # Increase count for better stress
        await self.test_invalid_data()
        await self.test_concurrent_connections(count=5) # Test with 5 concurrent attempts
        await self.test_connection_stress(cycles=20) # Increase cycles

        if include_timeout_test:
            # This test takes a long time
            await self.test_inactivity_timeout()
        else:
             print("\nSkipping Inactivity Timeout test (takes ~5 minutes). Set include_timeout_test=True to run.")


        # --- Summary ---
        suite_duration = time.perf_counter() - suite_start_time
        print("\n=========================")
        print(" Test Suite Summary")
        print("=========================")
        print(f"Total Tests Passed: {self.overall_summary['passed']}")
        print(f"Total Tests Failed: {self.overall_summary['failed']}")
        print(f"Total Duration: {suite_duration:.2f} seconds")
        print("=========================")

        # Save detailed results to a file
        results_filename = "websocket_test_results.json"
        try:
            with open(results_filename, "w") as f:
                json.dump(self.test_results, f, indent=2)
            print(f"Detailed results saved to {results_filename}")
        except Exception as e:
            print(f"Error saving results to {results_filename}: {e}")

        # Indicate overall success/failure
        return self.overall_summary['failed'] == 0


# --- Main Execution ---
if __name__ == "__main__":
    # Create the directory for the test image if it doesn't exist
    data_dir = "./Data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # Define the path for the test image
    image_file_path = os.path.join(data_dir, "test-img.jpg")

    # Check if the test image exists, if not create a dummy one
    if not os.path.exists(image_file_path):
        print(f"Test image '{image_file_path}' not found. Creating a dummy black image.")
        try:
            dummy_img = np.zeros((100, 100, 3), dtype=np.uint8) # 100x100 black image
            cv2.imwrite(image_file_path, dummy_img)
            print(f"Dummy image created at '{image_file_path}'.")
        except Exception as e:
            print(f"ERROR: Could not create dummy test image: {e}")
            print("Please ensure you have a valid image at './Data/test-img.jpg' or provide the correct path.")
            exit(1) # Exit if we can't even create a dummy image

    # --- Instantiate and Run Tester ---
    try:
         tester = WebSocketTester(image_path=image_file_path)
         # Set include_timeout_test=True if you want to run the long timeout test
         run_success = asyncio.run(tester.run_all_tests(include_timeout_test=False))

         if run_success:
              print("\nOverall Test Suite Result: PASSED")
              exit(0)
         else:
              print("\nOverall Test Suite Result: FAILED")
              exit(1)

    except FileNotFoundError as e:
         print(f"\nERROR: {e}")
         print("Please ensure the test image exists or the path is correct.")
         exit(1)
    except Exception as e:
        print(f"\nAn unexpected error occurred during testing: {e}")
        exit(1)