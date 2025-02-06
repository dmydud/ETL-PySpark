"""
This script generates fake user data and saves it to a CSV file.

Usage:
    python generate_fake_user_data.py <csv_filename> <num_records> [--start_date=<start_date>] [--end_date=<end_date>] [--locale <locale> ...]

Arguments:
    <csv_filename>  Name of the output CSV file.
    <num_records>   Number of records to generate.

Optional Arguments:
    --start_date    Start date for generating signup dates (e.g., '-5y', '-1y'). Default is '-5y'.
    --end_date      End date for generating signup dates (e.g., 'now', '-1m'). Default is 'now'.
    --locale        List of locales for generating fake data (e.g., 'en_US', 'fr_FR'). Default is 'en_US'.

Example usage:
    python generate_user_data.py data.csv 1000 --start_date="-1y" --locale en_US fr_FR
"""
import os
import argparse
import csv
from typing import List, Tuple

# Try to import tqdm for progress bar
try:
    from tqdm import tqdm
    USE_TQDM = True  # If tqdm is installed, use it
except ImportError:
    USE_TQDM = False  # If tqdm is not installed, fall back to print-based progress

try:
    import faker
except ImportError:
    print("Error: The 'Faker' library is required but not installed.")
    print("You can install it by running: pip install Faker==35.2.0")
    exit(1)  # Exit the script to prevent further errors


def create_fake_user_data(fake: faker.Faker, start_date: str,
                          end_date: str) -> Tuple[str, str, float]:
    """Generate fake user data."""
    name: str = fake.name()
    email: str = fake.unique.ascii_free_email()
    signup_date: float = fake.date_time_between(
        start_date=start_date,
        end_date=end_date
    ).timestamp()

    if signup_date is None:
        signup_date = 0

    return name, email, signup_date


def write_to_csv(csv_filename: str, num_records: int, fake: faker.Faker, start_date: str,
                 end_date: str) -> None:
    """Write fake data to the CSV file."""
    try:
        with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["user_id", "name", "email", "signup_date"])

            # Determine the iterator for records, with progress tracking if tqdm is available
            record_iterator = range(1, num_records + 1)

            if USE_TQDM:
                record_iterator = tqdm(record_iterator)
            else:
                # Calculate 10% progress threshold
                progress_threshold = num_records // 10

            for user_id in record_iterator:
                # Print progress every 10% if tqdm is not used
                if not USE_TQDM and user_id % progress_threshold == 0:
                    print(f"Generated {user_id}/{num_records} records...")

                name, email, signup_date = create_fake_user_data(fake, start_date, end_date)
                writer.writerow([user_id, name, email, signup_date])

        print(f"CSV file '{csv_filename}' generated with {num_records} records.")
    except IOError as e:
        print(f"IO error writing to file {csv_filename}: {e}")
    except ValueError as e:
        print(f"Value error in data: {e}")


def check_and_confirm_file_overwrite(csv_filename: str) -> bool:
    """Check if the file exists and ask user for confirmation to overwrite it."""
    if os.path.exists(csv_filename):
        # Ask user for confirmation to overwrite the file
        confirm = input(
            f"The file '{csv_filename}' already exists. Do you want to overwrite it? (y/n): "
        ).strip().lower()
        if confirm != 'y':
            print("File creation aborted.")
            return False  # Return False if user doesn't want to overwrite
    return True  # Return True if file doesn't exist or user confirms overwrite


def generate_fake_user_csv(csv_filename: str, num_records: int, start_date: str,
                           end_date: str, locale: List[str]) -> None:
    """Main function to initialize Faker and call writing logic."""
    fake = faker.Faker(locale=locale)
    if check_and_confirm_file_overwrite(csv_filename):
        write_to_csv(csv_filename, num_records, fake, start_date, end_date)


if __name__ == "__main__":
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Generate a CSV file with fake user data."
    )
    parser.add_argument(
        "csv_filename", type=str, help="Name of the output CSV file."
    )
    parser.add_argument(
        "num_records", type=int, help="Number of records to generate."
    )
    parser.add_argument(
        "--start_date", type=str, default="-5y",
        help="Start date for signup dates (e.g., '-5y', '-1y')."
    )
    parser.add_argument(
        "--end_date", type=str, default="now",
        help="End date for signup dates (e.g., 'now', '-1m')."
    )
    parser.add_argument(
        "--locale", type=str, nargs='+', default=["en_US"],
        help="Locales for generating fake data (e.g., 'en_US', 'fr_FR')."
    )

    args: argparse.Namespace = parser.parse_args()

    try:
        generate_fake_user_csv(args.csv_filename, args.num_records, args.start_date,
                               args.end_date, args.locale)
    except ValueError as e:
        print(f"Argument error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
