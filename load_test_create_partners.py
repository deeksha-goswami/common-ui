"""Load Test: Create 300 Partners via UI - Visible Browser."""

from playwright.sync_api import sync_playwright
import time
import statistics
from datetime import datetime
import json
import os

# Configuration
BASE_URL = "https://d317e9jhn09i0d.cloudfront.net"
LOGIN_URL = f"{BASE_URL}/login"
PARTNERS_URL = f"{BASE_URL}/partners"

# Login credentials
LOGIN_USERNAME = "deeksha_portal_user"
LOGIN_PASSWORD = "Welcome@1234"

# Partners to create
TOTAL_PARTNERS_TO_CREATE = 10
START_PARTNER_NUMBER = 401

class LoadTestResults:
    def __init__(self):
        self.create_times = []
        self.form_fill_times = []
        self.submit_times = []
        self.successful_creates = 0
        self.failed_creates = 0
        self.errors = []
        self.start_time = None
        self.end_time = None

results = LoadTestResults()

def calculate_stats(times, name):
    """Calculate statistics for a list of times."""
    if not times:
        return {"name": name, "count": 0, "min": 0, "max": 0, "avg": 0, "median": 0, "p90": 0, "p95": 0, "p99": 0}
    
    sorted_times = sorted(times)
    count = len(sorted_times)
    
    return {
        "name": name,
        "count": count,
        "min": round(min(sorted_times), 3),
        "max": round(max(sorted_times), 3),
        "avg": round(statistics.mean(sorted_times), 3),
        "median": round(statistics.median(sorted_times), 3),
        "p90": round(sorted_times[int(count * 0.9)] if count > 0 else 0, 3),
        "p95": round(sorted_times[int(count * 0.95)] if count > 0 else 0, 3),
        "p99": round(sorted_times[int(count * 0.99)] if count > 0 else 0, 3)
    }

def generate_html_report(stats, total_attempts, success_rate, duration, successful, failed, errors):
    """Generate HTML report."""
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Partner Portal - Create 300 Partners Load Test Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #8E2DE2 0%, #4A00E0 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }}
        .header h1 {{ color: #8E2DE2; font-size: 2em; margin-bottom: 10px; }}
        .header .subtitle {{ color: #666; font-size: 1.1em; }}
        .badge {{
            display: inline-block;
            background: #8E2DE2;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            margin-top: 10px;
            margin-right: 10px;
        }}
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .card {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
            text-align: center;
        }}
        .card h3 {{
            color: #666;
            font-size: 0.8em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }}
        .card .value {{ font-size: 2em; font-weight: bold; color: #333; }}
        .card.success .value {{ color: #28a745; }}
        .card.warning .value {{ color: #ffc107; }}
        .card.danger .value {{ color: #dc3545; }}
        .card.info .value {{ color: #8E2DE2; }}
        .stats-table {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
            margin-bottom: 20px;
            overflow-x: auto;
        }}
        .stats-table h2 {{
            color: #8E2DE2;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #eee;
        }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{
            background: #f8f9fa;
            color: #333;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.8em;
        }}
        tr:hover {{ background: #f8f9fa; }}
        .status-badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: 600;
        }}
        .status-pass {{ background: #d4edda; color: #155724; }}
        .status-warning {{ background: #fff3cd; color: #856404; }}
        .status-fail {{ background: #f8d7da; color: #721c24; }}
        .chart-container {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
            margin-bottom: 20px;
        }}
        .chart-container h2 {{ color: #8E2DE2; margin-bottom: 20px; }}
        .bar-chart {{
            display: flex;
            align-items: flex-end;
            height: 180px;
            gap: 30px;
            padding: 20px;
            justify-content: center;
        }}
        .bar-wrapper {{
            display: flex;
            flex-direction: column;
            align-items: center;
            flex: 1;
            max-width: 150px;
        }}
        .bar {{
            width: 100%;
            background: linear-gradient(to top, #8E2DE2, #4A00E0);
            border-radius: 8px 8px 0 0;
        }}
        .bar-label {{ margin-top: 10px; font-size: 0.85em; color: #666; text-align: center; }}
        .bar-value {{ margin-bottom: 5px; font-weight: bold; color: #8E2DE2; font-size: 1.1em; }}
        .test-info {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
            margin-bottom: 20px;
        }}
        .test-info h2 {{ color: #8E2DE2; margin-bottom: 15px; }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        .info-item {{ padding: 10px; background: #f8f9fa; border-radius: 8px; }}
        .info-item label {{ font-size: 0.8em; color: #666; text-transform: uppercase; }}
        .info-item span {{ display: block; font-size: 1.1em; font-weight: 600; color: #333; margin-top: 5px; }}
        .errors-section {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        }}
        .errors-section h2 {{ color: #8E2DE2; margin-bottom: 15px; }}
        .error-item {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 12px;
            margin-bottom: 8px;
            border-radius: 0 8px 8px 0;
            font-size: 0.9em;
        }}
        .no-errors {{
            background: #d4edda;
            border-left: 4px solid #28a745;
            padding: 15px;
            border-radius: 0 8px 8px 0;
            color: #155724;
        }}
        .footer {{ text-align: center; padding: 20px; color: white; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Partner Portal - Create Partners Load Test</h1>
            <p class="subtitle">Creating {TOTAL_PARTNERS_TO_CREATE} Partners via UI</p>
            <span class="badge">GUI Browser Testing</span>
            <span class="badge">Partner Creation Load Test</span>
            <span class="badge">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
        </div>
        
        <div class="summary-cards">
            <div class="card info">
                <h3>Total Attempts</h3>
                <div class="value">{total_attempts}</div>
            </div>
            <div class="card success">
                <h3>Partners Created</h3>
                <div class="value">{successful}</div>
            </div>
            <div class="card {'danger' if failed > 0 else 'success'}">
                <h3>Failed</h3>
                <div class="value">{failed}</div>
            </div>
            <div class="card {'success' if success_rate >= 95 else 'warning' if success_rate >= 80 else 'danger'}">
                <h3>Success Rate</h3>
                <div class="value">{success_rate:.1f}%</div>
            </div>
        </div>
        
        <div class="summary-cards">
            <div class="card info">
                <h3>Test Duration</h3>
                <div class="value">{duration/60:.1f}m</div>
            </div>
            <div class="card info">
                <h3>Throughput</h3>
                <div class="value">{successful/duration*60:.1f}/min</div>
            </div>
            <div class="card info">
                <h3>Avg Create Time</h3>
                <div class="value">{stats[0]['avg']:.2f}s</div>
            </div>
            <div class="card info">
                <h3>Avg Form Fill</h3>
                <div class="value">{stats[1]['avg']:.2f}s</div>
            </div>
        </div>

        <div class="test-info">
            <h2>Test Configuration</h2>
            <div class="info-grid">
                <div class="info-item">
                    <label>Target URL</label>
                    <span>{PARTNERS_URL}</span>
                </div>
                <div class="info-item">
                    <label>Partners to Create</label>
                    <span>{TOTAL_PARTNERS_TO_CREATE}</span>
                </div>
                <div class="info-item">
                    <label>Test Type</label>
                    <span>GUI Partner Creation Load Test</span>
                </div>
                <div class="info-item">
                    <label>Login Account</label>
                    <span>{LOGIN_USERNAME}</span>
                </div>
                <div class="info-item">
                    <label>Partner Range</label>
                    <span>LoadTest_Partner_{START_PARTNER_NUMBER:03d} to LoadTest_Partner_{START_PARTNER_NUMBER + TOTAL_PARTNERS_TO_CREATE - 1:03d}</span>
                </div>
            </div>
        </div>

        <div class="chart-container">
            <h2>Response Time Distribution</h2>
            <div class="bar-chart">
"""
    
    max_avg = max([s['avg'] for s in stats]) if stats else 1
    for stat in stats:
        height_percent = (stat['avg'] / max_avg * 140) if max_avg > 0 else 0
        html += f"""
                <div class="bar-wrapper">
                    <div class="bar-value">{stat['avg']:.2f}s</div>
                    <div class="bar" style="height: {max(height_percent, 20)}px;"></div>
                    <div class="bar-label">{stat['name']}<br><small>({stat['count']} ops)</small></div>
                </div>
"""
    
    html += """
            </div>
        </div>
        
        <div class="stats-table">
            <h2>Detailed Performance Metrics</h2>
            <table>
                <thead>
                    <tr>
                        <th>Operation</th>
                        <th>Count</th>
                        <th>Min (s)</th>
                        <th>Max (s)</th>
                        <th>Avg (s)</th>
                        <th>Median (s)</th>
                        <th>P90 (s)</th>
                        <th>P95 (s)</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    for stat in stats:
        status = "Pass" if stat['avg'] < 5 else "Slow" if stat['avg'] < 10 else "Critical"
        status_class = "status-pass" if status == "Pass" else "status-warning" if status == "Slow" else "status-fail"
        html += f"""
                    <tr>
                        <td><strong>{stat['name']}</strong></td>
                        <td>{stat['count']}</td>
                        <td>{stat['min']}</td>
                        <td>{stat['max']}</td>
                        <td>{stat['avg']}</td>
                        <td>{stat['median']}</td>
                        <td>{stat['p90']}</td>
                        <td>{stat['p95']}</td>
                        <td><span class="status-badge {status_class}">{status}</span></td>
                    </tr>
"""
    
    html += """
                </tbody>
            </table>
        </div>
        
        <div class="errors-section">
            <h2>Errors & Issues</h2>
"""
    
    if errors:
        unique_errors = list(set(errors))[:15]
        for error in unique_errors:
            html += f'            <div class="error-item">{error[:150]}</div>\n'
        if len(errors) > 15:
            html += f'            <div class="error-item">... and {len(errors) - 15} more errors</div>\n'
    else:
        html += '            <div class="no-errors">No errors - All partners created successfully!</div>\n'
    
    html += f"""
        </div>
        
        <div class="footer">
            <p>Partner Portal - Create Partners Load Test | {successful} Partners Created</p>
            <p>Duration: {duration/60:.1f} minutes | Success Rate: {success_rate:.1f}%</p>
        </div>
    </div>
</body>
</html>
"""
    return html

def run_create_partners_load_test():
    """Run load test to create partners via UI."""
    print("=" * 70, flush=True)
    print("Partner Portal - Create 10 Partners Load Test", flush=True)
    print("=" * 70, flush=True)
    print(f"\nConfiguration:", flush=True)
    print(f"  URL: {PARTNERS_URL}", flush=True)
    print(f"  Login: {LOGIN_USERNAME}", flush=True)
    print(f"  Partners to Create: {TOTAL_PARTNERS_TO_CREATE}", flush=True)
    print(f"  Partner Names: LoadTest_Partner_{START_PARTNER_NUMBER:03d} to LoadTest_Partner_{START_PARTNER_NUMBER + TOTAL_PARTNERS_TO_CREATE - 1:03d}", flush=True)
    print("\n" + "-" * 70, flush=True)
    
    results.start_time = time.time()
    
    print("\nLaunching browser - watch the partner creation process...", flush=True)
    print("-" * 70, flush=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            slow_mo=50,
            args=['--start-maximized']
        )
        
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            ignore_https_errors=True
        )
        context.set_default_timeout(30000)
        
        page = context.new_page()
        
        # Login first
        print("\n[LOGIN] Logging in as deeksha_portal_user...", flush=True)
        page.goto(LOGIN_URL)
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        
        page.locator("input").first.fill(LOGIN_USERNAME)
        time.sleep(0.2)
        page.locator("input[type='password']").first.fill(LOGIN_PASSWORD)
        time.sleep(0.2)
        page.locator("button[type='submit']").first.click()
        
        page.wait_for_load_state("networkidle")
        time.sleep(5)
        print(f"[LOGIN] Login successful! Current URL: {page.url}", flush=True)
        
        # Navigate to partners page
        print("[NAV] Navigating to Partners page...", flush=True)
        page.goto(PARTNERS_URL)
        page.wait_for_load_state("networkidle")
        time.sleep(3)
        print(f"[READY] On partners page: {page.url}", flush=True)
        
        # Take screenshot of partners page
        page.screenshot(path="screenshots/partners_page_before.png")
        
        print("\n" + "-" * 70, flush=True)
        print("Starting partner creation...", flush=True)
        print("-" * 70, flush=True)
        
        # Create partners
        for i in range(TOTAL_PARTNERS_TO_CREATE):
            partner_num = START_PARTNER_NUMBER + i
            partner_name = f"LoadTest_Partner_{partner_num:03d}"
            partner_email = f"partner_{partner_num:03d}@loadtest.com"
            
            total_start = time.time()
            
            try:
                # Wait for page to be ready
                page.wait_for_load_state("networkidle")
                time.sleep(0.3)
                
                # Click New Partner button
                new_partner_btn = page.locator("button:has-text('New Partner'), button:has-text('+ New Partner')").first
                new_partner_btn.wait_for(state="visible", timeout=10000)
                new_partner_btn.click()
                time.sleep(1.5)
                
                # Wait for form and fill
                form_start = time.time()
                
                # Find all visible text inputs for the form
                all_inputs = page.locator("input[type='text']:visible").all()
                
                # Filter out search inputs
                form_inputs = []
                for inp in all_inputs:
                    try:
                        placeholder = inp.get_attribute("placeholder") or ""
                        if "search" not in placeholder.lower():
                            form_inputs.append(inp)
                    except:
                        pass
                
                # Fill Account Name (Short Identifier) - first input
                if len(form_inputs) >= 1:
                    form_inputs[0].click()
                    time.sleep(0.1)
                    form_inputs[0].fill("")
                    form_inputs[0].type(partner_name, delay=15)
                    print(f"    Filled Account Name: {partner_name}", flush=True) if (i + 1) <= 3 else None
                
                time.sleep(0.2)
                
                # Fill Account Full Name - second input
                partner_full_name = f"LoadTest Partner {partner_num:03d} Inc."
                if len(form_inputs) >= 2:
                    form_inputs[1].click()
                    time.sleep(0.1)
                    form_inputs[1].fill("")
                    form_inputs[1].type(partner_full_name, delay=15)
                    print(f"    Filled Full Name: {partner_full_name}", flush=True) if (i + 1) <= 3 else None
                
                time.sleep(0.2)
                
                form_fill_time = time.time() - form_start
                results.form_fill_times.append(form_fill_time)
                
                # Submit
                submit_start = time.time()
                
                # Find and click Create Partner button
                save_btn = page.locator("button:has-text('Create Partner'), button:has-text('Save'), button:has-text('Create'), button:has-text('Submit')")
                visible_save_btns = []
                for j in range(save_btn.count()):
                    try:
                        if save_btn.nth(j).is_visible():
                            visible_save_btns.append(save_btn.nth(j))
                    except:
                        pass
                
                if visible_save_btns:
                    visible_save_btns[-1].click()  # Click the last visible one (usually in modal)
                
                # Wait for result
                time.sleep(2)
                page.wait_for_load_state("networkidle")
                time.sleep(0.5)
                
                submit_time = time.time() - submit_start
                results.submit_times.append(submit_time)
                
                total_time = time.time() - total_start
                results.create_times.append(total_time)
                
                # Check if dialog closed (success) or still open (error)
                dialog_visible = page.locator("[class*='MuiDialog']:visible, [class*='MuiModal']:visible").count() > 0
                
                if dialog_visible:
                    # Check for error
                    error = page.locator("[class*='error'], [role='alert'], [class*='MuiAlert']")
                    if error.count() > 0 and error.first.is_visible():
                        error_text = error.first.text_content()
                        results.errors.append(f"{partner_name}: {error_text[:50]}")
                    else:
                        results.errors.append(f"{partner_name}: Dialog still open")
                    
                    # Close dialog
                    cancel = page.locator("button:has-text('Cancel'):visible, button:has-text('Close'):visible")
                    if cancel.count() > 0:
                        cancel.first.click()
                        time.sleep(0.5)
                    else:
                        page.keyboard.press("Escape")
                        time.sleep(0.5)
                    
                    results.failed_creates += 1
                else:
                    results.successful_creates += 1
                
                # Progress update
                if (i + 1) % 10 == 0:
                    elapsed = time.time() - results.start_time
                    rate = (i + 1) / elapsed * 60
                    print(f"  [{i + 1}/{TOTAL_PARTNERS_TO_CREATE}] Created: {results.successful_creates} | Failed: {results.failed_creates} | Rate: {rate:.1f}/min | Last: {total_time:.2f}s", flush=True)
                
            except Exception as e:
                results.failed_creates += 1
                results.errors.append(f"{partner_name}: {str(e)[:50]}")
                print(f"  [{i + 1}] ERROR creating {partner_name}: {str(e)[:40]}", flush=True)
                
                # Try to close any dialog
                try:
                    page.keyboard.press("Escape")
                    time.sleep(0.5)
                except:
                    pass
        
        print("\n" + "-" * 70, flush=True)
        print(f"Completed creating partners", flush=True)
        
        # Take final screenshot
        page.screenshot(path="screenshots/load_test_create_partners_final.png")
        
        context.close()
        browser.close()
    
    results.end_time = time.time()
    
    # Calculate statistics
    print("\nCalculating statistics...", flush=True)
    
    create_stats = calculate_stats(results.create_times, "Total Create Time")
    form_stats = calculate_stats(results.form_fill_times, "Form Fill Time")
    submit_stats = calculate_stats(results.submit_times, "Submit Time")
    
    all_stats = [create_stats, form_stats, submit_stats]
    
    total_attempts = results.successful_creates + results.failed_creates
    success_rate = (results.successful_creates / total_attempts * 100) if total_attempts > 0 else 0
    test_duration = results.end_time - results.start_time
    
    # Print summary
    print("\n" + "=" * 70, flush=True)
    print("CREATE PARTNERS LOAD TEST SUMMARY", flush=True)
    print("=" * 70, flush=True)
    print(f"\nTotal Attempts: {total_attempts}", flush=True)
    print(f"Successfully Created: {results.successful_creates}", flush=True)
    print(f"Failed: {results.failed_creates}", flush=True)
    print(f"Success Rate: {success_rate:.1f}%", flush=True)
    print(f"Test Duration: {test_duration/60:.1f} minutes", flush=True)
    print(f"Throughput: {results.successful_creates/test_duration*60:.1f} partners/minute", flush=True)
    
    print("\nOperation Times (seconds):", flush=True)
    print("-" * 70, flush=True)
    print(f"{'Operation':<20} {'Count':>8} {'Min':>8} {'Max':>8} {'Avg':>8} {'P95':>8}", flush=True)
    print("-" * 70, flush=True)
    for stat in all_stats:
        print(f"{stat['name']:<20} {stat['count']:>8} {stat['min']:>8.3f} {stat['max']:>8.3f} {stat['avg']:>8.3f} {stat['p95']:>8.3f}", flush=True)
    
    # Generate HTML report
    print("\nGenerating HTML report...", flush=True)
    html_report = generate_html_report(all_stats, total_attempts, success_rate, test_duration,
                                        results.successful_creates, results.failed_creates, results.errors)
    
    os.makedirs("reports", exist_ok=True)
    report_filename = f"reports/create_partners_load_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(html_report)
    
    print(f"\n[OK] HTML Report saved to: {report_filename}", flush=True)
    
    # Save JSON
    json_results = {
        "test_config": {
            "url": PARTNERS_URL,
            "partners_to_create": TOTAL_PARTNERS_TO_CREATE,
            "start_partner_number": START_PARTNER_NUMBER,
            "test_type": "GUI Partner Creation Load Test",
            "login_user": LOGIN_USERNAME
        },
        "summary": {
            "total_attempts": total_attempts,
            "successful": results.successful_creates,
            "failed": results.failed_creates,
            "success_rate": success_rate,
            "test_duration_seconds": test_duration,
            "throughput_per_minute": results.successful_creates / test_duration * 60 if test_duration > 0 else 0
        },
        "statistics": all_stats,
        "errors_count": len(results.errors)
    }
    
    json_filename = f"reports/create_partners_load_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(json_results, f, indent=2)
    
    print(f"[OK] JSON Results saved to: {json_filename}", flush=True)
    print("=" * 70, flush=True)

if __name__ == "__main__":
    os.makedirs("screenshots", exist_ok=True)
    run_create_partners_load_test()
