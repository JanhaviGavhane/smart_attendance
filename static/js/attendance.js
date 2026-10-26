let audioStream = null;
let mediaRecorder = null;
let chunks = [];
let recording = false;
let stopping = false;
let requestInProgress = false;
let segmentTimer = null;

const audioQueue = [];
let processingQueue = false;
let pendingSegments = 0;
let transcripts = [];

const startButton = document.getElementById("startMic");
const stopButton = document.getElementById("stopMic");
const saveButton = document.getElementById("saveAttendance");
const statusText = document.getElementById("micStatus");
const transcriptText = document.getElementById("transcript");
const absentList = document.getElementById("absentList");
const presentList = document.getElementById("presentList");
const absentCount = document.getElementById("absentCount");
const presentCount = document.getElementById("presentCount");

if (startButton) {
    startButton.addEventListener("click", startMicrophone);
}

if (stopButton) {
    stopButton.addEventListener("click", stopMicrophone);
}

function updateCounts() {
    if (absentCount && absentList) {
        absentCount.textContent = absentList.children.length;
    }

    if (presentCount && presentList) {
        presentCount.textContent = presentList.children.length;
    }
}

function setStatus(message) {
    if (statusText) {
        statusText.textContent = message;
    }
}

function moveToPresent(roll) {
    const rollText = String(roll).trim();

    if (!absentList || !presentList) {
        return;
    }

    const alreadyPresent = Array.from(presentList.children).some(
        item => item.dataset.roll === rollText
    );

    if (alreadyPresent) {
        return;
    }

    const student = Array.from(absentList.children).find(
        item => item.dataset.roll === rollText
    );

    if (student) {
        presentList.appendChild(student);
        updateCounts();
    } else {
        console.warn(
            "Recognized roll number was not found in the Absent list:",
            rollText
        );
    }
}

async function startMicrophone() {
    try {
        if (!navigator.mediaDevices?.getUserMedia) {
            setStatus("Microphone requires Chrome on localhost or HTTPS.");
            return;
        }

        audioStream = await navigator.mediaDevices.getUserMedia({
            audio: {
                channelCount: 1,
                echoCancellation: true,
                noiseSuppression: true
            }
        });

        recording = true;
        stopping = false;
        pendingSegments = 0;
        transcripts = [];
        audioQueue.length = 0;

        if (transcriptText) {
            transcriptText.textContent = "";
        }

        startButton.disabled = true;
        stopButton.disabled = false;
        saveButton.disabled = true;

        setStatus("Microphone on. Speak clearly, one roll number at a time.");

        startSegment();

    } catch (error) {
        console.error("Microphone error:", error);
        setStatus("Could not access the microphone. Check microphone permission.");
        cleanup();
    }
}

function startSegment() {
    if (!recording || !audioStream) {
        return;
    }

    chunks = [];

    const options = {};

    if (MediaRecorder.isTypeSupported("audio/webm;codecs=opus")) {
        options.mimeType = "audio/webm;codecs=opus";
    }

    const recorder = new MediaRecorder(audioStream, options);
    mediaRecorder = recorder;

    recorder.ondataavailable = event => {
        if (event.data && event.data.size > 0) {
            chunks.push(event.data);
        }
    };

    recorder.onerror = event => {
        console.error("Recorder error:", event.error);
        setStatus("Microphone recording error. Check the browser console.");
    };

    recorder.onstop = () => {
        const blob = new Blob(chunks, {
            type: recorder.mimeType || "audio/webm"
        });

        if (blob.size > 1000) {
            audioQueue.push(blob);
            pendingSegments++;
            processAudioQueue();
        }

        if (recording && !stopping) {
            startSegment();
        } else {
            finishWhenQueueIsEmpty();
        }
    };

    recorder.start();

    segmentTimer = setTimeout(() => {
        if (recorder.state === "recording") {
            recorder.stop();
        }
    }, 4000);
}

async function processAudioQueue() {
    if (processingQueue) {
        return;
    }

    processingQueue = true;

    try {
        while (audioQueue.length > 0) {
            const blob = audioQueue.shift();
            await sendAudio(blob);
            pendingSegments--;
        }
    } finally {
        processingQueue = false;

        if (audioQueue.length > 0) {
            processAudioQueue();
        } else {
            finishWhenQueueIsEmpty();
        }
    }
}

async function sendAudio(blob) {
    requestInProgress = true;

    try {
        const formData = new FormData();
        formData.append("audio", blob, "roll-call.webm");

        const response = await fetch("/attendance/transcribe", {
            method: "POST",
            body: formData
        });

        const responseText = await response.text();

        console.log("Transcription HTTP status:", response.status);
        console.log("Transcription response:", responseText);

        let result;

        try {
            result = JSON.parse(responseText);
        } catch (error) {
            console.error("Invalid Flask response:", responseText);
            setStatus("Invalid transcription response. Check the Flask terminal.");
            return;
        }

        if (!response.ok) {
            setStatus(result.error || "Transcription failed.");
            return;
        }

        if (result.transcript) {
            transcripts.push(result.transcript);

            if (transcriptText) {
                transcriptText.textContent =
                    "Recognized speech: " + transcripts.join(" | ");
            }
        }

        if (Array.isArray(result.matches)) {
            result.matches.forEach(student => {
                moveToPresent(student.roll);
            });
        }

        updateCounts();

        if (result.message) {
            setStatus(result.message);
        }

    } catch (error) {
        console.error("Transcription request failed:", error);
        setStatus("Could not contact Flask. Check the server.");
    } finally {
        requestInProgress = false;
    }
}

function stopMicrophone() {
    if (!recording) {
        return;
    }

    stopping = true;
    recording = false;

    if (segmentTimer) {
        clearTimeout(segmentTimer);
        segmentTimer = null;
    }

    setStatus("Stopping microphone and processing remaining audio...");

    if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();
    } else {
        finishWhenQueueIsEmpty();
    }
}

function finishWhenQueueIsEmpty() {
    if (recording || !stopping) {
        return;
    }

    if (
        pendingSegments > 0 ||
        audioQueue.length > 0 ||
        processingQueue ||
        requestInProgress
    ) {
        return;
    }

    finishStop();
}

function finishStop() {
    if (segmentTimer) {
        clearTimeout(segmentTimer);
        segmentTimer = null;
    }

    if (audioStream) {
        audioStream.getTracks().forEach(track => track.stop());
        audioStream = null;
    }

    startButton.disabled = false;
    stopButton.disabled = true;
    saveButton.disabled = false;

    updateCounts();

    setStatus("Microphone stopped. Review Present and Absent before saving.");
}

function cleanup() {
    recording = false;
    stopping = true;

    if (segmentTimer) {
        clearTimeout(segmentTimer);
        segmentTimer = null;
    }

    if (audioStream) {
        audioStream.getTracks().forEach(track => track.stop());
        audioStream = null;
    }

    if (startButton) {
        startButton.disabled = false;
    }

    if (stopButton) {
        stopButton.disabled = true;
    }

    if (saveButton) {
        saveButton.disabled = true;
    }
}

updateCounts();