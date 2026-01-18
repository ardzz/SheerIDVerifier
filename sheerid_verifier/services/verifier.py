"""Core verification service."""

from __future__ import annotations

import random
import re
import time
from typing import TYPE_CHECKING, Any

from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeRemainingColumn

from sheerid_verifier import console
from sheerid_verifier.config import (
    DOCUMENT_TYPE,
    MAX_DELAY_MS,
    MIN_DELAY_MS,
    POLL_INTERVAL_SECONDS,
    POLL_MAX_ATTEMPTS,
    PROGRAM_ID,
    SHEERID_API_URL,
    UPLOAD_TIMEOUT,
    VALID_STEPS,
)
from sheerid_verifier.console import StepLogger
from sheerid_verifier.models.student import Student
from sheerid_verifier.models.university import select_university
from sheerid_verifier.services.document import (
    DocumentResult,
    generate_class_schedule,
    generate_student_id,
    generate_transcript,
)
from sheerid_verifier.services.http_client import HttpClient
from sheerid_verifier.services.stats import Stats
from sheerid_verifier.utils.fingerprint import generate_fingerprint
from sheerid_verifier.utils.headers import get_headers

if TYPE_CHECKING:
    from sheerid_verifier.models.university import University


def _random_delay() -> None:
    """Add random delay between requests to avoid detection."""
    time.sleep(random.randint(MIN_DELAY_MS, MAX_DELAY_MS) / 1000)


def _parse_verification_id(url: str) -> str | None:
    """Extract verification ID from SheerID URL."""
    match = re.search(r"verificationId=([a-f0-9]+)", url, re.IGNORECASE)
    return match.group(1) if match else None


class Verifier:
    """SheerID student verification service."""

    def __init__(
        self,
        http_client: HttpClient,
        stats: Stats,
        *,
        verbose: bool = True,
        logger: StepLogger | None = None,
    ) -> None:
        """
        Initialize verifier.

        Args:
            http_client: HTTP client for API requests
            stats: Statistics tracker
            verbose: Whether to print progress to console
            logger: Optional StepLogger for contextual logging. If None and verbose=True,
                    creates a default StepLogger.
        """
        self._client = http_client
        self._stats = stats
        self._verbose = verbose
        self._logger = logger or StepLogger(verbose=verbose)
        self._fingerprint = generate_fingerprint()

    def _request(
        self,
        method: str,
        endpoint: str,
        body: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any], int]:
        """Make API request with headers and delay."""
        _random_delay()

        headers = get_headers(for_sheerid=True)
        url = f"{SHEERID_API_URL}{endpoint}"

        if method == "GET":
            resp = self._client.get(url, headers=headers)
        elif method == "POST":
            resp = self._client.post(url, json=body, headers=headers)
        elif method == "DELETE":
            resp = self._client.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")

        return resp.json(), resp.status_code

    def _upload_document(self, upload_url: str, data: bytes) -> bool:
        """Upload document to S3."""
        headers = {"Content-Type": "image/png"}
        resp = self._client.put(upload_url, content=data, headers=headers, timeout=UPLOAD_TIMEOUT)
        return 200 <= resp.status_code < 300

    def _sleep_with_progress(self, seconds: int) -> None:
        """
        Sleep with a Rich progress bar countdown.

        Args:
            seconds: Number of seconds to sleep
        """
        if not self._verbose:
            time.sleep(seconds)
            return

        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Next poll in"),
            BarColumn(bar_width=25),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            transient=True,
        ) as progress:
            task = progress.add_task("waiting", total=seconds)
            for _ in range(seconds):
                time.sleep(1)
                progress.advance(task, 1)

    def _poll_status(
        self,
        vid: str,
        interval: int = POLL_INTERVAL_SECONDS,
        max_attempts: int = POLL_MAX_ATTEMPTS,
    ) -> dict[str, Any]:
        """
        Poll verification status until it is no longer pending.

        Args:
            vid: Verification ID
            interval: Seconds between polls
            max_attempts: Maximum number of poll attempts

        Returns:
            Final status data from API
        """
        data: dict[str, Any] = {}

        for attempt in range(max_attempts):
            data, status = self._request("GET", f"/verification/{vid}")
            current_step = data.get("currentStep", "")

            if current_step != "pending":
                return data

            # Log polling progress
            estimated_time = data.get("estimatedReviewTime", "unknown")
            self._logger.info(
                f"Status: pending (attempt {attempt + 1}/{max_attempts}, est: {estimated_time})"
            )

            # Progress bar countdown for sleep interval
            self._sleep_with_progress(interval)

        # Return last status even if still pending after max attempts
        return data

    def check_link(self, url: str) -> dict[str, Any]:
        """
        Check if verification link is valid.

        Args:
            url: SheerID verification URL

        Returns:
            Dict with valid bool and step or error
        """
        vid = _parse_verification_id(url)
        if not vid:
            return {"valid": False, "error": "Invalid URL - no verification ID found"}

        data, status = self._request("GET", f"/verification/{vid}")
        if status != 200:
            return {"valid": False, "error": f"HTTP {status}"}

        step = data.get("currentStep", "")
        if step in VALID_STEPS:
            return {"valid": True, "step": step}
        elif step == "success":
            return {"valid": False, "error": "Already verified"}
        elif step == "pending":
            return {"valid": False, "error": "Already pending review"}
        elif step == "error":
            # Extract error details from API response
            error_ids = data.get("errorIds", [])
            segment = data.get("segment", "")
            error_str = ", ".join(error_ids) if error_ids else "unknown"
            error_msg = f"Verification error: {error_str}"
            if segment:
                error_msg += f" (segment: {segment})"
            return {"valid": False, "error": error_msg}

        return {"valid": False, "error": f"Invalid step: {step}"}

    def verify(self, url: str) -> dict[str, Any]:
        """
        Run full verification process.

        Args:
            url: SheerID verification URL

        Returns:
            Dict with success bool and result details
        """
        vid = _parse_verification_id(url)
        if not vid:
            return {"success": False, "error": "Invalid verification URL"}

        # Track university for stats recording
        university: University | None = None

        try:
            # Check current step
            check_data, check_status = self._request("GET", f"/verification/{vid}")
            current_step = check_data.get("currentStep", "") if check_status == 200 else ""

            # Select university with weighted random selection
            university = select_university(self._stats.get_rate)

            # Generate student data
            student = Student.generate(university.domain)

            if self._verbose:
                console.print_student_info(
                    student.first_name,
                    student.last_name,
                    student.email,
                    university.name,
                    student.birth_date,
                    vid,
                )
                self._logger.detail("Starting step", current_step)

            # Step 1: Generate document
            # Select document type based on config
            if DOCUMENT_TYPE == "random":
                # Weighted random: class_schedule (50%), transcript (30%), id_card (20%)
                doc_type = random.choices(
                    ["class_schedule", "transcript", "id_card"],
                    weights=[50, 30, 20],
                    k=1,
                )[0]
            else:
                doc_type = DOCUMENT_TYPE

            with self._logger.step(1, 6, f"Generating {doc_type.replace('_', ' ')}"):
                doc_result: DocumentResult
                if doc_type == "class_schedule":
                    doc_result = generate_class_schedule(
                        student.first_name,
                        student.last_name,
                        university.name,
                        return_info=True,
                        verification_id=vid,
                    )
                    filename = "class_schedule.png"
                elif doc_type == "transcript":
                    doc_result = generate_transcript(
                        student.first_name,
                        student.last_name,
                        university.name,
                        student.birth_date,
                        return_info=True,
                        verification_id=vid,
                    )
                    filename = "transcript.png"
                else:  # id_card
                    doc_result = generate_student_id(
                        student.first_name,
                        student.last_name,
                        university.name,
                        return_info=True,
                        verification_id=vid,
                    )
                    filename = "student_card.png"

                doc = doc_result.data
                self._logger.detail("Type", doc_type)
                self._logger.detail("Method", doc_result.method)
                self._logger.detail("Size", f"{len(doc) / 1024:.1f} KB")
                if doc_result.cached_path:
                    self._logger.detail("Cached", str(doc_result.cached_path))

            # Step 2: Submit student info (if needed)
            if current_step == "collectStudentPersonalInfo":
                with self._logger.step(2, 6, "Submitting student info"):
                    body = {
                        "firstName": student.first_name,
                        "lastName": student.last_name,
                        "birthDate": student.birth_date,
                        "email": student.email,
                        "phoneNumber": "",
                        "organization": university.to_api_dict(),
                        "deviceFingerprintHash": self._fingerprint,
                        "locale": "en-US",
                        "metadata": {
                            "marketConsentValue": False,
                            "verificationId": vid,
                            "refererUrl": f"https://services.sheerid.com/verify/{PROGRAM_ID}/?verificationId={vid}",
                            "flags": '{"collect-info-step-email-first":"default","doc-upload-considerations":"default","doc-upload-may24":"default","doc-upload-redesign-use-legacy-message-keys":false,"docUpload-assertion-checklist":"default","font-size":"default","include-cvec-field-france-student":"not-labeled-optional"}',
                            "submissionOptIn": "By submitting the personal information above, I acknowledge that my personal information is being collected under the privacy policy of the business from which I am seeking a discount",
                        },
                    }

                    data, status = self._request(
                        "POST", f"/verification/{vid}/step/collectStudentPersonalInfo", body
                    )

                    if status != 200:
                        self._stats.record(university.name, False)
                        return {"success": False, "error": f"Submit failed: {status} - {data}"}

                    if data.get("currentStep") == "error":
                        self._stats.record(university.name, False)
                        return {"success": False, "error": f"Error: {data.get('errorIds', [])}"}

                    current_step = data.get("currentStep", "")
                    self._logger.detail("Current step", current_step)
            else:
                with self._logger.step(2, 6, "Skipping (already past info submission)"):
                    pass  # No-op, just log timing

            # Step 3: Skip SSO if needed
            if current_step in ["sso", "collectStudentPersonalInfo"]:
                with self._logger.step(3, 6, "Skipping SSO"):
                    self._request("DELETE", f"/verification/{vid}/step/sso")
            else:
                with self._logger.step(3, 6, "SSO not required"):
                    pass  # No-op, just log timing

            # Step 4: Upload document
            with self._logger.step(4, 6, "Uploading document"):
                upload_body = {
                    "files": [{"fileName": filename, "mimeType": "image/png", "fileSize": len(doc)}]
                }
                data, status = self._request(
                    "POST", f"/verification/{vid}/step/docUpload", upload_body
                )

                if not data.get("documents"):
                    self._stats.record(university.name, False)
                    return {"success": False, "error": "No upload URL received"}

                upload_url = data["documents"][0].get("uploadUrl")
                if not self._upload_document(upload_url, doc):
                    self._stats.record(university.name, False)
                    return {"success": False, "error": "Document upload failed"}

                self._logger.success("Document uploaded!")

            # Step 5: Complete upload
            with self._logger.step(5, 6, "Completing upload"):
                data, status = self._request("POST", f"/verification/{vid}/step/completeDocUpload")
                current_step = data.get("currentStep", "")
                self._logger.detail("Status", current_step)

            # Step 6: Poll for final status (if pending)
            if current_step == "pending":
                with self._logger.step(6, 6, "Waiting for review"):
                    final_data = self._poll_status(vid)
                    current_step = final_data.get("currentStep", "")

                    if current_step == "success":
                        self._logger.success("Verification approved!")
                        self._stats.record(university.name, True)
                        return {
                            "success": True,
                            "message": "Verification approved!",
                            "student": student.full_name,
                            "email": student.email,
                            "school": university.name,
                            "redirectUrl": final_data.get("redirectUrl"),
                        }
                    elif current_step == "docUpload":
                        # Document was rejected, need to resubmit
                        rejection_reasons = final_data.get("lastResponse", {}).get(
                            "rejectionReasons", []
                        )
                        self._logger.error(f"Document rejected: {rejection_reasons}")
                        self._stats.record(university.name, False)
                        return {
                            "success": False,
                            "error": f"Document rejected: {rejection_reasons}",
                            "rejectionReasons": rejection_reasons,
                            "student": student.full_name,
                            "school": university.name,
                        }
                    elif current_step == "error":
                        error_ids = final_data.get("errorIds", [])
                        self._logger.error(f"Verification failed: {error_ids}")
                        self._stats.record(university.name, False)
                        return {
                            "success": False,
                            "error": f"Verification error: {error_ids}",
                            "student": student.full_name,
                            "school": university.name,
                        }
                    elif current_step == "pending":
                        # Still pending after max attempts
                        self._logger.warning("Still pending after max poll attempts")
                        self._stats.record(university.name, True)  # Submitted successfully
                        return {
                            "success": True,
                            "message": "Verification submitted, still pending review.",
                            "student": student.full_name,
                            "email": student.email,
                            "school": university.name,
                            "status": "pending",
                        }
            else:
                with self._logger.step(6, 6, "Checking final status"):
                    if current_step == "success":
                        self._logger.success("Verification approved!")
                        self._stats.record(university.name, True)
                        return {
                            "success": True,
                            "message": "Verification approved!",
                            "student": student.full_name,
                            "email": student.email,
                            "school": university.name,
                            "redirectUrl": data.get("redirectUrl"),
                        }

            # Default: submission was successful
            self._stats.record(university.name, True)
            return {
                "success": True,
                "message": "Verification submitted! Wait for review.",
                "student": student.full_name,
                "email": student.email,
                "school": university.name,
                "status": current_step,
            }

        except Exception as e:
            if university is not None:
                self._stats.record(university.name, False)
            return {"success": False, "error": str(e)}
