# tests/load_test.py
import concurrent.futures
from google.cloud import storage
import time
import random
import os
from datetime import datetime
import json

# python load_test.py --project-id your-project-id --input-bucket your-bucket-name --output-bucket your-bucket-name --test-images-dir path/to/test/images

class ImageProcessorLoadTest:
    def __init__(self, project_id, input_bucket, output_bucket, test_images_dir):
        self.project_id = project_id
        self.input_bucket = input_bucket
        self.output_bucket = output_bucket
        self.storage_client = storage.Client()
        self.test_images = self._load_test_images(test_images_dir)
        self.results = []

    def _load_test_images(self, test_images_dir):
        images = []
        for filename in os.listdir(test_images_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                with open(os.path.join(test_images_dir, filename), 'rb') as f:
                    images.append({
                        'data': f.read(),
                        'name': filename,
                    })
        return images

    def run_test(self, concurrent_uploads, duration_seconds):
        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=concurrent_uploads
        ) as executor:
            while time.time() - start_time < duration_seconds:
                futures = []
                for _ in range(concurrent_uploads):
                    image = random.choice(self.test_images)
                    futures.append(executor.submit(self._upload_and_verify, image))

                for future in concurrent.futures.as_completed(futures):
                    self.results.append(future.result())

    def _upload_and_verify(self, image):
        start_time = time.time()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"test_{timestamp}_{random.randint(1000,9999)}_{image['name']}"

        try:
            # Upload image
            input_bucket = self.storage_client.bucket(self.input_bucket)
            output_bucket = self.storage_client.bucket(self.output_bucket)
            blob = input_bucket.blob(filename)
            blob.upload_from_string(image['data'], content_type='image/jpeg')

            # Verify processing results with retry logic
            verification = None
            max_retries = 10
            retry_delay = 2  # seconds
            for attempt in range(max_retries):
                verification = self._verify_processing(output_bucket, filename)
                if all(verification.values()):  # Check if all verifications are True
                    break
                print(f"Verification failed, retrying... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(retry_delay)
            else:
                print("Max retries reached. Verification incomplete.")

            end_time = time.time()

            return {
                'filename': filename,
                'duration': end_time - start_time,
                'status': 'success',
                'verification': verification,
                'timestamp': start_time,
            }
        except Exception as e:
            return {
                'filename': filename,
                'duration': time.time() - start_time,
                'status': 'error',
                'error': str(e),
                'timestamp': start_time,
            }

    def _verify_processing(self, bucket, filename):
        verification = {
            'metadata': False,
            'thumbnails': False,
            'rgb_channels': False,
            'converted_formats': False,
        }

        # Check metadata
        metadata_blob = bucket.blob(f"metadata/{filename}.json")
        channels_blob = bucket.blob(f"channels/{filename}/metadata.json")
        thumbnail_blob = bucket.blob(f"thumbnail/{filename}/metadata.json")
        converted_blob = bucket.blob(f"converted/{filename}/metadata.json")

        if metadata_blob.exists():
            verification['metadata'] = True

            if channels_blob.exists():
                if channels_blob['thumbnails']:
                        verification['thumbnails'] = True

            if thumbnail_blob.exists():
                if thumbnail_blob['rgb_channels']:
                        verification['rgb_channels'] = True

            if converted_blob.exists():
                if converted_blob['converted_formats']:
                        verification['converted_formats'] = True

        return verification

    def generate_summary(self):
        total_uploads = len(self.results)
        successful_uploads = len([r for r in self.results if r['status'] == 'success'])
        failed_uploads = total_uploads - successful_uploads

        durations = [r['duration'] for r in self.results]
        avg_duration = sum(durations) / len(durations) if durations else 0

        # Calculate verification success rates
        verification_success = {
            k: 0 for k in ['metadata', 'thumbnails', 'rgb_channels', 'converted_formats']
        }
        for result in self.results:
            if result['status'] == 'success':
                for key, value in result['verification'].items():
                    if value:
                        verification_success[key] += 1

        verification_rates = {
            k: (v / successful_uploads * 100 if successful_uploads > 0 else 0)
            for k, v in verification_success.items()
        }

        return {
            'total_uploads': total_uploads,
            'successful_uploads': successful_uploads,
            'failed_uploads': failed_uploads,
            'average_duration': avg_duration,
            'verification_rates': verification_rates,
        }


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Run load tests for image processor')
    parser.add_argument('--project-id', required=True, help='Google Cloud Project ID')
    parser.add_argument('--input-bucket', required=True, help='Input bucket name')
    parser.add_argument('--output-bucket', required=True, help='Output bucket name')
    parser.add_argument('--test-images-dir', required=True, help='Directory containing test images')

    args = parser.parse_args()

    test_scenarios = [
        {'concurrent': 1, 'duration': 60},  # Baseline
        {'concurrent': 10, 'duration': 120},  # Medium load
        {'concurrent': 50, 'duration': 180},  # High load
        {'concurrent': 100, 'duration': 300},  # Stress test
    ]

    tester = ImageProcessorLoadTest(
        project_id=args.project_id,
        input_bucket=args.input_bucket,
        output_bucket=args.output_bucket,
        test_images_dir=args.test_images_dir,
    )

    for scenario in test_scenarios:
        print(f"\nRunning test with {scenario['concurrent']} concurrent uploads...")
        print(f"Duration: {scenario['duration']} seconds")
        tester.run_test(scenario['concurrent'], scenario['duration'])

        # Print summary after each scenario
        summary = tester.generate_summary()
        print("\nScenario Summary:")
        print(f"Total uploads: {summary['total_uploads']}")
        print(f"Successful uploads: {summary['successful_uploads']}")
        print(f"Failed uploads: {summary['failed_uploads']}")
        print(f"Average duration: {summary['average_duration']:.2f} seconds")
        print("\nVerification rates:")
        for step, rate in summary['verification_rates'].items():
            print(f"{step}: {rate:.1f}%")

        # Clear results for next scenario
        tester.results = []


if __name__ == "__main__":
    main()