from faster_whisper import WhisperModel

_model = None


def get_model():
    global _model

    if _model is None:
        _model = WhisperModel(
            "base",
            device="cpu",
            compute_type="int8",
            cpu_threads=4,
            num_workers=1
        )

    return _model


def transcribe_audio_file(file_path):
    model = get_model()

    segments, info = model.transcribe(
        file_path,
        beam_size=1,
        language="en",
        task="transcribe",
        vad_filter=False,
        condition_on_previous_text=False
    )

    transcript_parts = []

    for segment in segments:
        text = segment.text.strip()

        if text:
            transcript_parts.append(text)

    transcript = " ".join(transcript_parts).strip()

    print("Faster-Whisper transcript:", repr(transcript), flush=True)

    return transcript


