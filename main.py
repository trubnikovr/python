import argparse
import http.client
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


def main():
    parser = argparse.ArgumentParser(description="Measure download speed with 10 sequential requests.")
    parser.add_argument("url", help="HTTP or HTTPS URL to download")
    args = parser.parse_args()

    parsed = urllib.parse.urlsplit(args.url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        parser.error("URL must be a valid HTTP or HTTPS address")

    total_bytes = 0
    total_seconds = 0.0
    for number in range(1, 11):
        request = urllib.request.Request(args.url, headers={"Cache-Control": "no-cache"})
        start = time.perf_counter()
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                downloaded = 0
                while chunk := response.read(64 * 1024):
                    downloaded += len(chunk)
                expected = response.headers.get("Content-Length")
                if expected is not None and downloaded != int(expected):
                    raise ValueError("response body is incomplete")
        except (urllib.error.URLError, OSError, http.client.HTTPException, ValueError) as error:
            print(f"Request {number} failed: {error}", file=sys.stderr)
            return 1
        total_seconds += time.perf_counter() - start
        total_bytes += downloaded
        print(f"\r[{'#' * number}{'-' * (10 - number)}] {number}/10", end="", flush=True)

    print()
    print(f"Average request time: {total_seconds / 10:.3f} s")
    print(f"Total downloaded: {total_bytes} bytes")
    print(f"Download speed: {total_bytes * 8 / total_seconds / 1_000_000:.2f} Mbps")
    return 0


if __name__ == "__main__":
    sys.exit(main())
